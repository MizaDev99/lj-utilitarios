import uuid
from django.db import models


def gerar_numero_pedido():
    return str(uuid.uuid4()).replace('-', '')[:8].upper()


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    numero_pedido = models.CharField(
        'Número do Pedido', max_length=20, unique=True, default=gerar_numero_pedido
    )
    nome_cliente = models.CharField('Nome do Cliente', max_length=200)
    telefone_cliente = models.CharField('Telefone', max_length=20)
    cidade_cliente = models.CharField('Cidade', max_length=100)
    endereco_cliente = models.TextField('Endereço')
    observacoes = models.TextField('Observações', blank=True)
    status = models.CharField(
        'Status', max_length=20, choices=STATUS_CHOICES, default='aguardando'
    )
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, default=0)
    frete = models.DecimalField('Frete', max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Pedido #{self.numero_pedido} - {self.nome_cliente}'

    def get_status_display_color(self):
        cores = {
            'aguardando': '#F59E0B',
            'confirmado': '#3B82F6',
            'enviado': '#8B5CF6',
            'entregue': '#10B981',
            'cancelado': '#EF4444',
        }
        return cores.get(self.status, '#6B7280')


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='itens', verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        'produtos.Produto', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Produto'
    )
    nome_produto = models.CharField('Nome do Produto', max_length=200)
    quantidade = models.IntegerField('Quantidade')
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.nome_produto}'

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario
