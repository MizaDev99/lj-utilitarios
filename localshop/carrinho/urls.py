from django.urls import path
from . import views

app_name = 'carrinho'

urlpatterns = [
    path('', views.ver_carrinho, name='ver'),
    path('adicionar/<int:produto_id>/', views.adicionar_item, name='adicionar'),
    path('remover/<int:produto_id>/', views.remover_item, name='remover'),
    path('atualizar/<int:produto_id>/', views.atualizar_quantidade, name='atualizar'),
]
