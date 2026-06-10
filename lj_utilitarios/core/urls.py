from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('privacidade/', views.privacidade, name='privacidade'),
    path('termos/', views.termos, name='termos'),
    path('log-cookies/', views.log_cookies, name='log_cookies'),
]
