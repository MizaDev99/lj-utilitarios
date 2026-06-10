from django.core.exceptions import ValidationError


def validar_imagem(arquivo):
    """Valida que o arquivo é uma imagem permitida e não ultrapassa 5 MB."""
    limite_mb = 5
    if arquivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f'Imagem muito grande. Tamanho máximo: {limite_mb} MB.')

    # Verificar magic bytes para garantir que é uma imagem real
    import imghdr
    arquivo.seek(0)
    tipo = imghdr.what(arquivo)
    arquivo.seek(0)
    tipos_permitidos = {'jpeg', 'png', 'webp', 'gif'}
    if tipo not in tipos_permitidos:
        raise ValidationError('Formato inválido. Use JPG, PNG ou WebP.')
