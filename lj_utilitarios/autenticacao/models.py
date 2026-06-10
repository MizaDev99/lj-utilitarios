from django.db import models
from django.contrib.auth.models import User


class PerfilCliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfilcliente')
    firebase_uid = models.CharField('Firebase UID', max_length=128, unique=True, null=True, blank=True, default=None)
    foto_url = models.URLField('Foto', blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil do Cliente'
        verbose_name_plural = 'Perfis dos Clientes'

    def __str__(self):
        return f'Perfil de {self.user.email}'
