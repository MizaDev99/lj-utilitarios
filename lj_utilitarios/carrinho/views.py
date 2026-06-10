import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from produtos.models import Produto
from core.models import Configuracao


def _get_carrinho(request):
    return request.session.get('carrinho', {})


def _save_carrinho(request, carrinho):
    request.session['carrinho'] = carrinho
    request.session.modified = True


def _calc_totais(carrinho, config):
    subtotal = sum(float(i['preco']) * i['quantidade'] for i in carrinho.values())
    frete = 0.0
    if subtotal > 0:
        frete = 0.0 if subtotal >= float(config.frete_gratis_acima) else float(config.frete_fixo)
    return subtotal, frete, subtotal + frete


def ver_carrinho(request):
    carrinho = _get_carrinho(request)
    config = Configuracao.get_config()
    subtotal, frete, total = _calc_totais(carrinho, config)

    itens = [
        {
            'id': pid,
            'nome': item['nome'],
            'preco': item['preco'],
            'quantidade': item['quantidade'],
            'imagem': item.get('imagem', ''),
            'slug': item.get('slug', ''),
            'subtotal': float(item['preco']) * item['quantidade'],
        }
        for pid, item in carrinho.items()
    ]

    context = {
        'itens': itens,
        'subtotal': subtotal,
        'frete': frete,
        'total': total,
        'frete_gratis_acima': float(config.frete_gratis_acima),
    }
    return render(request, 'carrinho/carrinho.html', context)


@require_POST
def adicionar_item(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id, ativo=True)
    carrinho = _get_carrinho(request)
    key = str(produto_id)
    try:
        quantidade = int(request.POST.get('quantidade', 1))
    except (ValueError, TypeError):
        quantidade = 1
    if quantidade < 1:
        quantidade = 1

    if key in carrinho:
        carrinho[key]['quantidade'] = min(carrinho[key]['quantidade'] + quantidade, produto.estoque)
    else:
        imagem_url = produto.imagem_principal.url if produto.imagem_principal else ''
        carrinho[key] = {
            'nome': produto.nome,
            'preco': str(produto.preco_atual),
            'quantidade': min(quantidade, produto.estoque),
            'imagem': imagem_url,
            'slug': produto.slug,
        }

    _save_carrinho(request, carrinho)
    total_itens = sum(i['quantidade'] for i in carrinho.values())

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'total_itens': total_itens})
    return redirect('carrinho:ver')


@require_POST
def remover_item(request, produto_id):
    carrinho = _get_carrinho(request)
    key = str(produto_id)
    if key in carrinho:
        del carrinho[key]
    _save_carrinho(request, carrinho)

    config = Configuracao.get_config()
    subtotal, frete, total = _calc_totais(carrinho, config)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_itens': sum(i['quantidade'] for i in carrinho.values()),
            'subtotal': subtotal, 'frete': frete, 'total': total,
        })
    return redirect('carrinho:ver')


@require_POST
def atualizar_quantidade(request, produto_id):
    carrinho = _get_carrinho(request)
    key = str(produto_id)

    try:
        data = json.loads(request.body)
        quantidade = int(data.get('quantidade', 1))
    except (json.JSONDecodeError, ValueError):
        quantidade = int(request.POST.get('quantidade', 1))

    if quantidade < 1:
        carrinho.pop(key, None)
    elif key in carrinho:
        produto = get_object_or_404(Produto, pk=produto_id)
        carrinho[key]['quantidade'] = min(quantidade, produto.estoque)

    _save_carrinho(request, carrinho)
    config = Configuracao.get_config()
    subtotal, frete, total = _calc_totais(carrinho, config)
    item_subtotal = float(carrinho[key]['preco']) * carrinho[key]['quantidade'] if key in carrinho else 0

    return JsonResponse({
        'success': True,
        'total_itens': sum(i['quantidade'] for i in carrinho.values()),
        'subtotal': subtotal, 'frete': frete, 'total': total,
        'item_subtotal': item_subtotal,
    })
