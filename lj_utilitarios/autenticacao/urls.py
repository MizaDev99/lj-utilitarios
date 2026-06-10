from django.urls import path
from . import views

app_name = 'autenticacao'

urlpatterns = [
    path('google/', views.google_login, name='google_login'),
    path('logout/', views.google_logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/atualizar/', views.perfil_atualizar, name='perfil_atualizar'),
    path('meus-dados/', views.meus_dados, name='meus_dados'),
    path('excluir-conta/', views.excluir_conta, name='excluir_conta'),
]
