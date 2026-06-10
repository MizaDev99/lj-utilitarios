from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/finalizar/', views.finalizar_pedido, name='finalizar'),
    path('pedido/confirmado/<str:numero>/', views.pedido_confirmado, name='confirmado'),
]
