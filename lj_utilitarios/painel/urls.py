from django.urls import path
from . import views

app_name = 'painel'

urlpatterns = [
    path('login/', views.painel_login, name='login'),
    path('logout/', views.painel_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('produtos/', views.produtos_lista, name='produtos'),
    path('produtos/novo/', views.produto_criar, name='produto_criar'),
    path('produtos/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('produtos/<int:pk>/deletar/', views.produto_deletar, name='produto_deletar'),
    path('categorias/', views.categorias_lista, name='categorias'),
    path('categorias/nova/', views.categoria_criar, name='categoria_criar'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/deletar/', views.categoria_deletar, name='categoria_deletar'),
    path('pedidos/', views.pedidos_lista, name='pedidos'),
    path('pedidos/<int:pk>/', views.pedido_detalhe, name='pedido_detalhe'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('lgpd/', views.lgpd_logs, name='lgpd'),
]
