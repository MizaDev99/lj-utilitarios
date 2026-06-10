import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lj_utilitarios.settings')
application = get_wsgi_application()
