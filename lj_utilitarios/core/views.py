from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from produtos.models import Produto, Categoria
from core.models import Configuracao, LogConsentimento


def homepage(request):
    config = Configuracao.get_config()
    categorias = Categoria.objects.filter(ativo=True).order_by('ordem', 'nome')
    destaques = Produto.objects.filter(ativo=True, destaque=True, estoque__gt=0)[:8]
    ofertas = Produto.objects.filter(ativo=True, preco_promocional__isnull=False, estoque__gt=0)[:8]
    recentes = Produto.objects.filter(ativo=True, estoque__gt=0).order_by('-criado_em')[:8]

    context = {
        'categorias': categorias,
        'destaques': destaques,
        'ofertas': ofertas,
        'recentes': recentes,
    }
    return render(request, 'core/homepage.html', context)


def privacidade(request):
    config = Configuracao.get_config()
    return render(request, 'core/privacidade.html', {'config': config})


def termos(request):
    config = Configuracao.get_config()
    return render(request, 'core/termos.html', {'config': config})


@require_POST
def log_cookies(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')
    LogConsentimento.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        ip_address=ip,
        acao='aceite_cookies',
        detalhes={'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]},
    )
    return JsonResponse({'ok': True})
