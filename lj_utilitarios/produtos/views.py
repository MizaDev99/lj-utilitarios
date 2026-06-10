from django.shortcuts import render, get_object_or_404
from .models import Produto, Categoria


def lista_produtos(request):
    produtos = Produto.objects.filter(ativo=True, estoque__gt=0).select_related('categoria')
    categorias = Categoria.objects.filter(ativo=True).order_by('ordem', 'nome')

    categoria_slug = request.GET.get('categoria', '')
    busca = request.GET.get('q', '').strip()
    ordem = request.GET.get('ordem', '')

    categoria_atual = None
    if categoria_slug:
        categoria_atual = get_object_or_404(Categoria, slug=categoria_slug, ativo=True)
        produtos = produtos.filter(categoria=categoria_atual)

    if busca:
        produtos = produtos.filter(nome__icontains=busca)

    if ordem == 'menor_preco':
        produtos = sorted(produtos, key=lambda p: p.preco_atual)
    elif ordem == 'maior_preco':
        produtos = sorted(produtos, key=lambda p: p.preco_atual, reverse=True)
    elif ordem == 'mais_novo':
        produtos = list(produtos.order_by('-criado_em'))
    else:
        produtos = list(produtos.order_by('-destaque', '-criado_em'))

    context = {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_atual': categoria_atual,
        'busca': busca,
        'ordem': ordem,
    }
    return render(request, 'produtos/listagem.html', context)


def detalhe_produto(request, slug):
    produto = get_object_or_404(Produto, slug=slug, ativo=True)
    imagens = produto.imagens.all()
    relacionados = Produto.objects.filter(
        ativo=True, categoria=produto.categoria, estoque__gt=0
    ).exclude(pk=produto.pk)[:4]

    context = {
        'produto': produto,
        'imagens': imagens,
        'relacionados': relacionados,
    }
    return render(request, 'produtos/detalhe.html', context)
