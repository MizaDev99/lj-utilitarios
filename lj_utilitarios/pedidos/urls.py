from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/finalizar/', views.finalizar_pedido, name='finalizar'),
    path('pedidos/frete/', views.calcular_frete, name='calcular_frete'),
    path('pedido/<str:numero>/', views.pedido_confirmado, name='confirmado'),
]
