from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('sistema-interno-lj/', admin.site.urls),  # URL não-óbvia para o admin Django
    path('', include('core.urls')),
    path('produtos/', include('produtos.urls')),
    path('carrinho/', include('carrinho.urls')),
    path('', include('pedidos.urls')),
    path('painel/', include('painel.urls')),
    path('auth/', include('autenticacao.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
