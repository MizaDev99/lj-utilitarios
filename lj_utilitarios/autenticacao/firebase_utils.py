import os
import firebase_admin
from firebase_admin import credentials, auth


def _resolver_caminho_json():
    """Resolve o caminho do service account JSON, absoluto ou relativo ao projeto."""
    json_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON', 'firebase-service-account.json')
    if not os.path.isabs(json_path):
        # Raiz do projeto = dois níveis acima deste arquivo (autenticacao/)
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base, json_path)
    return json_path


def inicializar_firebase():
    """Inicializa o Firebase Admin SDK se ainda não foi inicializado."""
    if firebase_admin._apps:
        return True
    json_path = _resolver_caminho_json()
    if os.path.exists(json_path):
        try:
            cred = credentials.Certificate(json_path)
            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            print(f'[Firebase] Erro ao inicializar: {e}')
    else:
        print(f'[Firebase] Arquivo service account não encontrado: {json_path}')
    return False


def validar_token_firebase(id_token):
    """Valida um ID token do Firebase e retorna os dados do usuário ou None."""
    try:
        inicializar_firebase()
        decoded = auth.verify_id_token(id_token)
        return {
            'uid':      decoded.get('uid', ''),
            'email':    decoded.get('email', ''),
            'nome':     decoded.get('name', ''),
            'foto_url': decoded.get('picture', ''),
        }
    except Exception as e:
        print(f'[Firebase] Erro ao validar token: {e}')
        return None
