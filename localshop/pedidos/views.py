from urllib.parse import quote
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Configuracao
from produtos.models import Produto
from .models import Pedido, ItemPedido
from .forms import CheckoutForm


def checkout(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('carrinho:ver')

    config = Configuracao.get_config()
    subtotal = sum(float(v['preco']) * v['quantidade'] for v in carrinho.values())
    frete = 0.0
    if subtotal > 0:
        frete = 0.0 if subtotal >= float(config.frete_gratis_acima) else float(config.frete_fixo)
    total = subtotal + frete

    form = CheckoutForm(request.POST or None)

    context = {
        'form': form,
        'carrinho': carrinho,
        'subtotal': subtotal,
        'frete': frete,
        'total': total,
        'cidades_atendidas': config.get_cidades_lista(),
    }
    return render(request, 'pedidos/checkout.html', context)


def finalizar_pedido(request):
    if request.method != 'POST':
        return redirect('pedidos:checkout')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('carrinho:ver')

    config = Configuracao.get_config()
    subtotal = sum(float(v['preco']) * v['quantidade'] for v in carrinho.values())
    frete = 0.0
    if subtotal > 0:
        frete = 0.0 if subtotal >= float(config.frete_gratis_acima) else float(config.frete_fixo)
    total = subtotal + frete

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        context = {
            'form': form,
            'carrinho': carrinho,
            'subtotal': subtotal,
            'frete': frete,
            'total': total,
            'cidades_atendidas': config.get_cidades_lista(),
        }
        return render(request, 'pedidos/checkout.html', context)

    pedido = form.save(commit=False)
    pedido.subtotal = subtotal
    pedido.frete = frete
    pedido.total = total
    pedido.save()

    for produto_id, item in carrinho.items():
        try:
            produto = Produto.objects.get(pk=int(produto_id))
        except Produto.DoesNotExist:
            produto = None

        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            nome_produto=item['nome'],
            quantidade=item['quantidade'],
            preco_unitario=float(item['preco']),
        )

    if config.whatsapp_numero:
        mensagem = _montar_mensagem(pedido, carrinho, subtotal, frete, total, config)
        numero = config.whatsapp_numero.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not numero.startswith('55'):
            numero = '55' + numero
        url_whatsapp = f'https://wa.me/{numero}?text={quote(mensagem)}'
        del request.session['carrinho']
        request.session.modified = True
        return redirect(url_whatsapp)

    del request.session['carrinho']
    request.session.modified = True
    return redirect('pedidos:confirmado', numero=pedido.numero_pedido)


def pedido_confirmado(request, numero):
    pedido = get_object_or_404(Pedido, numero_pedido=numero)
    return render(request, 'pedidos/confirmado.html', {'pedido': pedido})


def _montar_mensagem(pedido, carrinho, subtotal, frete, total, config):
    linhas_itens = []
    for item in carrinho.values():
        preco = float(item['preco'])
        qtd = item['quantidade']
        subtotal_item = preco * qtd
        linhas_itens.append(
            f"• {qtd}x {item['nome']} — R$ {subtotal_item:.2f}"
        )
    lista_itens = '\n'.join(linhas_itens)

    template = config.whatsapp_mensagem_template
    mensagem = (
        template
        .replace('{{numero}}', pedido.numero_pedido)
        .replace('{{nome}}', pedido.nome_cliente)
        .replace('{{cidade}}', pedido.cidade_cliente)
        .replace('{{telefone}}', pedido.telefone_cliente)
        .replace('{{endereco}}', pedido.endereco_cliente)
        .replace('{{lista_itens}}', lista_itens)
        .replace('{{subtotal}}', f'{subtotal:.2f}')
        .replace('{{frete}}', f'{frete:.2f}')
        .replace('{{total}}', f'{total:.2f}')
        .replace('{{observacoes}}', pedido.observacoes or 'Nenhuma')
    )
    return mensagem
