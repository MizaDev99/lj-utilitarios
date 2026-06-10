import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.urls import reverse
from django.views.decorators.http import require_POST
from produtos.models import Produto, Categoria
from produtos.forms import ProdutoForm, CategoriaForm
from pedidos.models import Pedido
from core.models import Configuracao, LogConsentimento
from .forms import ConfiguracaoForm, StatusPedidoForm


def _staff(u):
    return u.is_active and (u.is_staff or u.is_superuser)


def staff_required(fn):
    return user_passes_test(_staff, login_url='/painel/login/')(fn)


def painel_login(request):
    from django.core.cache import cache
    if request.user.is_authenticated and _staff(request.user):
        return redirect('painel:dashboard')

    ip = request.META.get('REMOTE_ADDR', '')
    cache_key = f'painel_login_{ip}'
    attempts = cache.get(cache_key, 0)
    if attempts >= 5:
        messages.error(request, 'Muitas tentativas. Aguarde 15 minutos antes de tentar novamente.')
        return render(request, 'painel/login.html')

    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user and _staff(user):
            login(request, user)
            cache.delete(cache_key)
            return redirect('painel:dashboard')
        cache.set(cache_key, attempts + 1, 60 * 15)
        messages.error(request, 'Credenciais inválidas ou sem permissão.')
    return render(request, 'painel/login.html')


@require_POST
def painel_logout(request):
    logout(request)
    return redirect('painel:login')


@staff_required
def dashboard(request):
    hoje = timezone.now().date()
    primeiro_mes = hoje.replace(day=1)
    pedidos_hoje = Pedido.objects.filter(criado_em__date=hoje).count()
    pedidos_pendentes = Pedido.objects.filter(status='aguardando').count()
    fat = Pedido.objects.filter(criado_em__date__gte=primeiro_mes, status__in=['confirmado', 'enviado', 'entregue']).aggregate(t=Sum('total'))['t'] or 0
    produtos_ativos = Produto.objects.filter(ativo=True).count()
    pedidos_recentes = Pedido.objects.all()[:10]
    return render(request, 'painel/dashboard.html', {
        'pedidos_hoje': pedidos_hoje,
        'pedidos_pendentes': pedidos_pendentes,
        'faturamento_mes': fat,
        'produtos_ativos': produtos_ativos,
        'pedidos_recentes': pedidos_recentes,
    })


@staff_required
def produtos_lista(request):
    q = request.GET.get('q', '')
    qs = Produto.objects.select_related('categoria').all()
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(categoria__nome__icontains=q))
    return render(request, 'painel/produtos_lista.html', {'produtos': qs, 'busca': q})


@staff_required
def produto_criar(request):
    form = ProdutoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        p = form.save()
        messages.success(request, f'Produto "{p.nome}" criado!')
        return redirect('painel:produtos')
    return render(request, 'painel/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})


@staff_required
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(request.POST or None, request.FILES or None, instance=produto)
    if form.is_valid():
        p = form.save()
        messages.success(request, f'Produto "{p.nome}" atualizado!')
        return redirect('painel:produtos')
    return render(request, 'painel/produto_form.html', {'form': form, 'produto': produto, 'titulo': f'Editar: {produto.nome}'})


@staff_required
def produto_deletar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        nome = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome}" removido.')
        return redirect('painel:produtos')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': produto, 'cancel_url': reverse('painel:produtos')
    })


@staff_required
def categorias_lista(request):
    return render(request, 'painel/categorias_lista.html', {'categorias': Categoria.objects.all()})


@staff_required
def categoria_criar(request):
    form = CategoriaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        c = form.save()
        messages.success(request, f'Categoria "{c.nome}" criada!')
        return redirect('painel:categorias')
    return render(request, 'painel/categoria_form.html', {'form': form, 'titulo': 'Nova Categoria'})


@staff_required
def categoria_editar(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, request.FILES or None, instance=cat)
    if form.is_valid():
        c = form.save()
        messages.success(request, f'Categoria "{c.nome}" atualizada!')
        return redirect('painel:categorias')
    return render(request, 'painel/categoria_form.html', {'form': form, 'categoria': cat, 'titulo': f'Editar: {cat.nome}'})


@staff_required
def categoria_deletar(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nome = cat.nome
        cat.delete()
        messages.success(request, f'Categoria "{nome}" removida.')
        return redirect('painel:categorias')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': cat, 'cancel_url': reverse('painel:categorias')
    })


@staff_required
def pedidos_lista(request):
    status = request.GET.get('status', '')
    qs = Pedido.objects.prefetch_related('itens').all()
    if status:
        qs = qs.filter(status=status)
    return render(request, 'painel/pedidos_lista.html', {
        'pedidos': qs, 'status_filtro': status, 'status_choices': Pedido.STATUS_CHOICES
    })


@staff_required
def pedido_detalhe(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = StatusPedidoForm(request.POST or None, instance=pedido)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Status atualizado!')
        return redirect('painel:pedido_detalhe', pk=pk)
    return render(request, 'painel/pedido_detalhe.html', {'pedido': pedido, 'form': form})


@staff_required
def configuracoes(request):
    config = Configuracao.get_config()
    form = ConfiguracaoForm(request.POST or None, request.FILES or None, instance=config)
    if form.is_valid():
        form.save()
        messages.success(request, 'Configurações salvas!')
        return redirect('painel:configuracoes')
    return render(request, 'painel/configuracoes.html', {'form': form, 'config': config})


@staff_required
def lgpd_logs(request):
    acao_filtro = request.GET.get('acao', '')
    data_ini = request.GET.get('data_ini', '')
    data_fim = request.GET.get('data_fim', '')

    logs = LogConsentimento.objects.select_related('usuario').all()
    if acao_filtro:
        logs = logs.filter(acao=acao_filtro)
    if data_ini:
        logs = logs.filter(data_hora__date__gte=data_ini)
    if data_fim:
        logs = logs.filter(data_hora__date__lte=data_fim)

    if request.GET.get('exportar') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="logs_lgpd.csv"'
        response.write('﻿')  # BOM para Excel
        writer = csv.writer(response)
        writer.writerow(['Data/Hora', 'Usuário', 'Ação', 'IP', 'Detalhes'])
        for log in logs:
            writer.writerow([
                log.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                log.usuario.email if log.usuario else '—',
                log.get_acao_display(),
                log.ip_address or '—',
                str(log.detalhes),
            ])
        return response

    context = {
        'logs': logs[:200],
        'acao_filtro': acao_filtro,
        'data_ini': data_ini,
        'data_fim': data_fim,
        'acoes': LogConsentimento.ACOES,
        'total': logs.count(),
    }
    return render(request, 'painel/lgpd.html', context)
