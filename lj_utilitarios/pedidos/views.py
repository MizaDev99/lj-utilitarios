from decimal import Decimal
from urllib.parse import quote
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.utils import timezone
from core.models import Configuracao, LogConsentimento
from produtos.models import Produto
from .models import Pedido, ItemPedido
from .forms import CheckoutForm


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')


def calcular_frete(request):
    cidade = request.GET.get('cidade', '')
    config = Configuracao.get_config()
    frete = float(config.get_frete_cidade(cidade))
    return JsonResponse({'frete': f'{frete:.2f}', 'cidade': cidade})


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('/?login_required=true')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('carrinho:ver')

    config = Configuracao.get_config()
    subtotal = _subtotal(carrinho)

    initial = {}
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfilcliente
            initial['nome_cliente'] = request.user.get_full_name() or request.user.email
            if perfil.telefone:
                initial['telefone_cliente'] = perfil.telefone
        except Exception:
            initial['nome_cliente'] = request.user.get_full_name() or request.user.email

    form = CheckoutForm(request.POST or None, initial=initial)
    itens = _itens_resumo(carrinho)

    context = {
        'form': form,
        'itens': itens,
        'subtotal': subtotal,
        'frete': 0,
        'total': subtotal,
        'config': config,
    }
    return render(request, 'pedidos/checkout.html', context)


def finalizar_pedido(request):
    if not request.user.is_authenticated:
        return redirect('/?login_required=true')

    if request.method != 'POST':
        return redirect('pedidos:checkout')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        return redirect('carrinho:ver')

    config = Configuracao.get_config()
    subtotal = _subtotal(carrinho)

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        itens = _itens_resumo(carrinho)
        frete_atual = _frete_do_form(request.POST, config)
        return render(request, 'pedidos/checkout.html', {
            'form': form, 'itens': itens,
            'subtotal': subtotal, 'frete': frete_atual, 'total': subtotal + frete_atual,
            'config': config,
        })

    pedido = form.save(commit=False)
    pedido.cliente = request.user if request.user.is_authenticated else None
    pedido.subtotal = subtotal
    pedido.consentimento_lgpd = True
    pedido.data_consentimento = timezone.now()
    pedido.ip_cliente = _get_client_ip(request)

    forma_recebimento = form.cleaned_data['forma_recebimento']
    if forma_recebimento == 'retirada':
        pedido.frete = 0
        pedido.cidade_cliente = 'Retirada na loja — Três Rios, RJ'
        pedido.endereco_cliente = ''
    else:
        cidade = form.cleaned_data.get('cidade_cliente', '')
        pedido.frete = float(config.get_frete_cidade(cidade))

    # Re-valida preços diretamente do banco — nunca confia em preços da sessão
    itens_validados = []
    subtotal_db = Decimal('0')
    for pid, item in carrinho.items():
        try:
            produto = Produto.objects.get(pk=int(pid))
            preco = produto.preco_atual
        except (Produto.DoesNotExist, ValueError):
            produto = None
            preco = Decimal(str(item['preco']))
        qtd = int(item['quantidade'])
        subtotal_db += preco * qtd
        itens_validados.append({
            'produto': produto,
            'nome': item['nome'],
            'quantidade': qtd,
            'preco': preco,
        })

    pedido.subtotal = subtotal_db
    pedido.total = subtotal_db + Decimal(str(pedido.frete))
    pedido.save()

    LogConsentimento.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        ip_address=pedido.ip_cliente,
        acao='consentimento_checkout',
        detalhes={'pedido_numero': pedido.numero_pedido, 'total': str(pedido.total)},
    )

    for item_data in itens_validados:
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item_data['produto'],
            nome_produto=item_data['nome'],
            quantidade=item_data['quantidade'],
            preco_unitario=item_data['preco'],
        )

    del request.session['carrinho']
    request.session.modified = True

    if config.whatsapp_numero:
        mensagem = _montar_mensagem(pedido, carrinho, config)
        numero = ''.join(c for c in config.whatsapp_numero if c.isdigit())
        if not numero.startswith('55'):
            numero = '55' + numero
        return redirect(f'https://wa.me/{numero}?text={quote(mensagem)}')

    return redirect('pedidos:confirmado', numero=pedido.numero_pedido)


def pedido_confirmado(request, numero):
    pedido = get_object_or_404(Pedido, numero_pedido=numero)
    # Apenas o dono do pedido ou staff pode visualizar — evita IDOR
    if not request.user.is_authenticated:
        return redirect('/?login_required=true')
    if pedido.cliente and pedido.cliente != request.user and not request.user.is_staff:
        raise Http404
    return render(request, 'pedidos/confirmado.html', {'pedido': pedido})


def _subtotal(carrinho):
    return sum(float(v['preco']) * v['quantidade'] for v in carrinho.values())


def _frete_do_form(post_data, config):
    forma = post_data.get('forma_recebimento', 'entrega')
    if forma == 'retirada':
        return 0.0
    cidade = post_data.get('cidade_cliente', '')
    return float(config.get_frete_cidade(cidade)) if cidade else 0.0


def _itens_resumo(carrinho):
    return [
        {
            'id': pid, 'nome': item['nome'], 'preco': item['preco'],
            'quantidade': item['quantidade'], 'imagem': item.get('imagem', ''),
            'slug': item.get('slug', ''),
            'subtotal': float(item['preco']) * item['quantidade'],
        }
        for pid, item in carrinho.items()
    ]


def _montar_mensagem(pedido, carrinho, config):
    FORMAS_PAGAMENTO = {
        'credito':  'Cartão de Crédito',
        'debito':   'Cartão de Débito',
        'dinheiro': 'Dinheiro',
        'pix':      'Pix',
    }
    forma_pgto_label = FORMAS_PAGAMENTO.get(pedido.forma_pagamento, pedido.forma_pagamento)

    linha_troco = ''
    if pedido.forma_pagamento == 'dinheiro' and pedido.troco_para:
        linha_troco = f'\n💵 *Troco para:* R$ {pedido.troco_para:.2f}'
    elif pedido.forma_pagamento == 'pix' and config.chave_pix:
        linha_troco = f'\n📱 *Pix* ({config.get_tipo_pix_label()}): {config.chave_pix}'

    if pedido.forma_recebimento == 'retirada':
        linha_entrega = '🏪 *Retirada na loja em Três Rios, RJ*'
    else:
        linha_entrega = (
            f'📍 *Cidade:* {pedido.cidade_cliente}\n'
            f'🏠 *Endereço:* {pedido.endereco_cliente}'
        )

    itens_texto = '\n'.join(
        f'• {item.quantidade}x {item.nome_produto} — R$ {item.preco_unitario:.2f}'
        for item in pedido.itens.all()
    )

    data_hora = timezone.localtime(pedido.criado_em).strftime('%d/%m/%Y às %H:%M')

    return (
        f'🛒 *Novo Pedido #{pedido.numero_pedido}* — L&J Utilitários\n\n'
        f'👤 *Cliente:* {pedido.nome_cliente}\n'
        f'📞 *Telefone:* {pedido.telefone_cliente}\n\n'
        f'🚚 *Entrega/Retirada:*\n'
        f'{linha_entrega}\n\n'
        f'💳 *Forma de Pagamento:* {forma_pgto_label}'
        f'{linha_troco}\n\n'
        f'🛍️ *Itens do Pedido:*\n'
        f'{itens_texto}\n\n'
        f'💰 Subtotal: R$ {float(pedido.subtotal):.2f}\n'
        f'🚚 Frete: R$ {float(pedido.frete):.2f}\n'
        f'💵 *TOTAL: R$ {float(pedido.total):.2f}*\n\n'
        f'📝 *Obs:* {pedido.observacoes or "Nenhuma"}\n'
        f'🕐 Pedido em: {data_hora}'
    )
