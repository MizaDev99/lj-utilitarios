import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import PerfilCliente
from .firebase_utils import validar_token_firebase
from core.models import LogConsentimento

logger = logging.getLogger(__name__)


def _get_ip(request):
    # Usa REMOTE_ADDR (não X-Forwarded-For) para evitar spoofing do IP no rate limiting.
    # X-Forwarded-For pode ser forjado pelo cliente e nunca deve ser usado para controle de acesso.
    return request.META.get('REMOTE_ADDR', '')


@require_POST
def google_login(request):
    from django.core.cache import cache
    ip = _get_ip(request)
    cache_key = f'login_attempts_{ip}'
    attempts = cache.get(cache_key, 0)
    if attempts >= 10:
        return JsonResponse(
            {'success': False, 'error': 'Muitas tentativas. Tente novamente em 15 minutos.'},
            status=429,
        )

    try:
        data = json.loads(request.body)
        id_token = data.get('id_token', '')
        if not id_token:
            return JsonResponse({'success': False, 'error': 'Token não fornecido.'}, status=400)

        usuario = validar_token_firebase(id_token)
        if not usuario:
            cache.set(cache_key, attempts + 1, 60 * 15)
            return JsonResponse(
                {'success': False, 'error': 'Token inválido ou Firebase não configurado.'},
                status=401,
            )

        email     = usuario['email']
        nome      = usuario.get('nome', '')
        partes    = nome.split(' ', 1) if nome else ['', '']
        first     = partes[0]
        last      = partes[1] if len(partes) > 1 else ''

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username':   email.split('@')[0][:140] + '_' + usuario['uid'][:6],
                'first_name': first,
                'last_name':  last,
            },
        )
        if not created and not user.first_name and first:
            user.first_name = first
            user.last_name  = last
            user.save(update_fields=['first_name', 'last_name'])

        perfil, _ = PerfilCliente.objects.get_or_create(user=user)
        perfil.firebase_uid = usuario['uid']
        if usuario.get('foto_url'):
            perfil.foto_url = usuario['foto_url']
        perfil.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        cache.delete(cache_key)  # limpar contador após login bem-sucedido

        LogConsentimento.objects.create(
            usuario=user,
            ip_address=_get_ip(request),
            acao='aceite_termos_google',
            detalhes={'email': email, 'uid': usuario['uid'][:12]},
        )

        return JsonResponse({
            'success': True,
            'user': {
                'name':      user.get_full_name() or email.split('@')[0],
                'email':     email,
                'photo_url': perfil.foto_url,
            },
        })

    except Exception as e:
        cache.set(cache_key, attempts + 1, 60 * 15)
        logger.error('Erro no google_login: %s', e, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Erro interno. Tente novamente mais tarde.'}, status=500)


@require_POST
def google_logout(request):
    logout(request)
    return JsonResponse({'success': True})


@login_required(login_url='/')
def perfil(request):
    try:
        perfil_obj = request.user.perfilcliente
    except PerfilCliente.DoesNotExist:
        perfil_obj = PerfilCliente.objects.create(user=request.user)

    pedidos = request.user.pedidos.all()[:10]
    return render(request, 'autenticacao/perfil.html', {
        'perfil':  perfil_obj,
        'pedidos': pedidos,
    })


@require_POST
@login_required(login_url='/')
def perfil_atualizar(request):
    try:
        perfil_obj = request.user.perfilcliente
    except PerfilCliente.DoesNotExist:
        perfil_obj = PerfilCliente.objects.create(user=request.user)

    perfil_obj.cidade   = request.POST.get('cidade', '')[:100].strip()
    perfil_obj.telefone = request.POST.get('telefone', '')[:20].strip()
    perfil_obj.save()
    messages.success(request, 'Perfil atualizado com sucesso!')
    return redirect('autenticacao:perfil')


@login_required(login_url='/')
def meus_dados(request):
    user = request.user
    try:
        perfil = user.perfilcliente
    except PerfilCliente.DoesNotExist:
        perfil = None

    dados = {
        'usuario': {
            'id':            user.pk,
            'nome':          user.get_full_name(),
            'email':         user.email,
            'username':      user.username,
            'membro_desde':  user.date_joined.strftime('%d/%m/%Y'),
        },
        'perfil': {
            'cidade':        perfil.cidade if perfil else '',
            'telefone':      perfil.telefone if perfil else '',
            'foto_url':      perfil.foto_url if perfil else '',
            'firebase_uid':  (perfil.firebase_uid[:8] + '...') if perfil and perfil.firebase_uid else '',
        },
        'pedidos': [
            {
                'numero': p.numero_pedido,
                'data':   p.criado_em.strftime('%d/%m/%Y'),
                'total':  str(p.total),
                'status': p.get_status_display(),
            }
            for p in user.pedidos.all()[:20]
        ],
    }
    return render(request, 'autenticacao/meus_dados.html', {'dados': dados})


@login_required(login_url='/')
def excluir_conta(request):
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao', '').strip()
        if confirmacao != 'CONFIRMAR':
            messages.error(request, 'Digite exatamente "CONFIRMAR" para prosseguir.')
            return render(request, 'autenticacao/excluir_conta.html')

        user = request.user
        ip   = _get_ip(request)

        for pedido in user.pedidos.all():
            pedido.nome_cliente     = 'Cliente Removido'
            pedido.telefone_cliente = ''
            pedido.endereco_cliente = ''
            pedido.save(update_fields=['nome_cliente', 'telefone_cliente', 'endereco_cliente'])

        try:
            if hasattr(user, 'perfilcliente') and user.perfilcliente.firebase_uid:
                from firebase_admin import auth as fb_auth
                fb_auth.revoke_refresh_tokens(user.perfilcliente.firebase_uid)
        except Exception:
            pass

        LogConsentimento.objects.create(
            usuario=None,
            ip_address=ip,
            acao='exclusao_conta',
            detalhes={'email': user.email, 'user_id': str(user.pk)},
        )

        logout(request)
        user.delete()

        messages.success(request, 'Sua conta foi excluída e todos os dados foram removidos.')
        return redirect('core:homepage')

    return render(request, 'autenticacao/excluir_conta.html')
