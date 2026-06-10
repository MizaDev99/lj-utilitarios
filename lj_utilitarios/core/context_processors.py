from django.conf import settings
from .models import Configuracao
from produtos.models import Categoria


def configuracao_global(request):
    config = Configuracao.get_config()
    categorias_nav = Categoria.objects.filter(ativo=True).order_by('ordem', 'nome')

    firebase_config = {
        'apiKey': settings.FIREBASE_API_KEY,
        'authDomain': settings.FIREBASE_AUTH_DOMAIN,
        'projectId': settings.FIREBASE_PROJECT_ID,
        'storageBucket': settings.FIREBASE_STORAGE_BUCKET,
        'messagingSenderId': settings.FIREBASE_MESSAGING_SENDER_ID,
        'appId': settings.FIREBASE_APP_ID,
    }
    firebase_habilitado = bool(settings.FIREBASE_API_KEY and settings.FIREBASE_PROJECT_ID)

    return {
        'config': config,
        'categorias_nav': categorias_nav,
        'firebase_config': firebase_config,
        'firebase_habilitado': firebase_habilitado,
    }
