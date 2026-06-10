from django.shortcuts import render
from produtos.models import Produto, Categoria
from core.models import Configuracao


def homepage(request):
    config = Configuracao.get_config()
    categorias = Categoria.objects.filter(ativo=True)
    destaques = Produto.objects.filter(ativo=True, destaque=True, estoque__gt=0)[:8]
    ofertas = Produto.objects.filter(
        ativo=True, preco_promocional__isnull=False, estoque__gt=0
    )[:8]
    recentes = Produto.objects.filter(ativo=True, estoque__gt=0).order_by('-criado_em')[:8]

    context = {
        'config': config,
        'categorias': categorias,
        'destaques': destaques,
        'ofertas': ofertas,
        'recentes': recentes,
    }
    return render(request, 'core/homepage.html', context)
