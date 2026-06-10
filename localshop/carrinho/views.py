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


def ver_carrinho(request):
    carrinho = _get_carrinho(request)
    config = Configuracao.get_config()

    subtotal = sum(
        float(item['preco']) * item['quantidade']
        for item in carrinho.values()
    )

    frete = 0.0
    if subtotal > 0:
        if subtotal >= float(config.frete_gratis_acima):
            frete = 0.0
        else:
            frete = float(config.frete_fixo)

    total = subtotal + frete

    context = {
        'carrinho': carrinho,
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

    quantidade = int(request.POST.get('quantidade', 1))
    if quantidade < 1:
        quantidade = 1

    if key in carrinho:
        nova_qtd = carrinho[key]['quantidade'] + quantidade
        carrinho[key]['quantidade'] = min(nova_qtd, produto.estoque)
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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_itens = sum(i['quantidade'] for i in carrinho.values())
        return JsonResponse({'success': True, 'total_itens': total_itens})

    return redirect('carrinho:ver')


@require_POST
def remover_item(request, produto_id):
    carrinho = _get_carrinho(request)
    key = str(produto_id)
    if key in carrinho:
        del carrinho[key]
        _save_carrinho(request, carrinho)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        config = Configuracao.get_config()
        subtotal = sum(float(i['preco']) * i['quantidade'] for i in carrinho.values())
        frete = 0.0
        if subtotal > 0:
            frete = 0.0 if subtotal >= float(config.frete_gratis_acima) else float(config.frete_fixo)
        return JsonResponse({
            'success': True,
            'total_itens': sum(i['quantidade'] for i in carrinho.values()),
            'subtotal': subtotal,
            'frete': frete,
            'total': subtotal + frete,
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
        if key in carrinho:
            del carrinho[key]
    else:
        produto = get_object_or_404(Produto, pk=produto_id)
        if key in carrinho:
            carrinho[key]['quantidade'] = min(quantidade, produto.estoque)

    _save_carrinho(request, carrinho)

    config = Configuracao.get_config()
    subtotal = sum(float(i['preco']) * i['quantidade'] for i in carrinho.values())
    frete = 0.0
    if subtotal > 0:
        frete = 0.0 if subtotal >= float(config.frete_gratis_acima) else float(config.frete_fixo)

    item_subtotal = 0.0
    if key in carrinho:
        item_subtotal = float(carrinho[key]['preco']) * carrinho[key]['quantidade']

    return JsonResponse({
        'success': True,
        'total_itens': sum(i['quantidade'] for i in carrinho.values()),
        'subtotal': subtotal,
        'frete': frete,
        'total': subtotal + frete,
        'item_subtotal': item_subtotal,
    })
