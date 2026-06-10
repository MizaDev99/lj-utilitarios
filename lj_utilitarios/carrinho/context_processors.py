def carrinho_context(request):
    carrinho = request.session.get('carrinho', {})
    total_itens = sum(item['quantidade'] for item in carrinho.values())
    return {'carrinho_total_itens': total_itens}
