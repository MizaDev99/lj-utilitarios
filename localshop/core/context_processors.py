from .models import Configuracao
from produtos.models import Categoria


def configuracao_global(request):
    config = Configuracao.get_config()
    categorias_nav = Categoria.objects.filter(ativo=True)
    return {
        'config': config,
        'categorias_nav': categorias_nav,
    }
