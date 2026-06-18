import re
from django.db import models


DEFAULT_TEMPLATE = """🛒 *Novo Pedido #{{numero}}*

👤 Cliente: {{nome}}
📍 Cidade: {{cidade}}
📞 Telefone: {{telefone}}
🏠 Endereço: {{endereco}}

*Itens:*
{{lista_itens}}

💰 Subtotal: R$ {{subtotal}}
🚚 Frete: R$ {{frete}}
💵 *Total: R$ {{total}}*

📝 Obs: {{observacoes}}"""


class Configuracao(models.Model):
    nome_loja = models.CharField('Nome da Loja', max_length=100, default='LocalShop')
    whatsapp_numero = models.CharField(
        'Número WhatsApp', max_length=20,
        help_text='Apenas números com DDD, ex: 11999999999', blank=True
    )
    whatsapp_mensagem_template = models.TextField(
        'Template da Mensagem', default=DEFAULT_TEMPLATE
    )
    cidade_base = models.CharField('Cidade Base', max_length=100, blank=True)
    cidades_atendidas = models.TextField(
        'Cidades Atendidas',
        help_text='Separe as cidades por vírgula', blank=True
    )
    logo = models.ImageField('Logo', upload_to='loja/', blank=True, null=True)
    cor_primaria = models.CharField('Cor Primária', max_length=7, default='#FF6B00')
    banner_principal = models.ImageField(
        'Banner Principal', upload_to='banners/', blank=True, null=True
    )
    texto_banner = models.CharField('Texto do Banner', max_length=200, blank=True)
    frete_fixo = models.DecimalField(
        'Frete Fixo (R$)', max_digits=8, decimal_places=2, default=10.00
    )
    frete_gratis_acima = models.DecimalField(
        'Frete Grátis Acima de (R$)', max_digits=10, decimal_places=2, default=150.00
    )

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return self.nome_loja

    @property
    def whatsapp_url(self):
        numero = re.sub(r'\D', '', self.whatsapp_numero)
        if numero and not numero.startswith('55'):
            numero = '55' + numero
        return f'https://wa.me/{numero}' if numero else ''

    def get_cidades_lista(self):
        if self.cidades_atendidas:
            return [c.strip() for c in self.cidades_atendidas.split(',') if c.strip()]
        return []

    @classmethod
    def get_config(cls):
        config = cls.objects.first()
        if not config:
            config = cls.objects.create(
                nome_loja='LocalShop',
                whatsapp_numero='',
                cidade_base='Sua Cidade',
            )
        return config
