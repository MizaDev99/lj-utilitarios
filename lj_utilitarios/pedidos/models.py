import uuid
from django.db import models
from django.contrib.auth.models import User


def gerar_numero():
    return str(uuid.uuid4()).replace('-', '')[:8].upper()


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    STATUS_CORES = {
        'aguardando': '#FFB800',
        'confirmado': '#4D6AFF',
        'enviado': '#9B6AFF',
        'entregue': '#00C48C',
        'cancelado': '#FF3D3D',
    }

    FORMAS_RECEBIMENTO = [
        ('entrega', 'Entrega no endereço'),
        ('retirada', 'Retirada na loja'),
    ]
    FORMAS_PAGAMENTO = [
        ('credito', 'Cartão de Crédito'),
        ('debito', 'Cartão de Débito'),
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
    ]

    numero_pedido = models.CharField(max_length=20, unique=True, default=gerar_numero)
    cliente = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pedidos', verbose_name='Cliente'
    )
    nome_cliente = models.CharField('Nome', max_length=200)
    telefone_cliente = models.CharField('Telefone', max_length=20)
    cidade_cliente = models.CharField('Cidade', max_length=100, blank=True)
    endereco_cliente = models.TextField('Endereço', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    forma_recebimento = models.CharField(
        'Forma de Recebimento', max_length=20,
        choices=FORMAS_RECEBIMENTO, default='entrega'
    )
    forma_pagamento = models.CharField(
        'Forma de Pagamento', max_length=20,
        choices=FORMAS_PAGAMENTO, default='credito'
    )
    troco_para = models.DecimalField(
        'Troco para (R$)', max_digits=10, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frete = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    consentimento_lgpd = models.BooleanField('Consentimento LGPD', default=False)
    data_consentimento = models.DateTimeField('Data do Consentimento', null=True, blank=True)
    ip_cliente = models.GenericIPAddressField('IP do Cliente', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.numero_pedido}'

    def get_status_cor(self):
        return self.STATUS_CORES.get(self.status, '#B0B8D1')


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.SET_NULL, null=True, blank=True)
    nome_produto = models.CharField(max_length=200)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f'{self.quantidade}x {self.nome_produto}'
