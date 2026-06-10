from django.db import models
from django.conf import settings
from core.validators import validar_imagem


DEFAULT_TEMPLATE = (
    "🛒 *Novo Pedido #{{numero}}* — L&J Utilitários\n\n"
    "👤 *Cliente:* {{nome}}\n"
    "📞 *Telefone:* {{telefone}}\n\n"
    "🚚 *Forma de Recebimento:* {{forma_recebimento}}\n"
    "{{info_entrega}}\n\n"
    "💳 *Forma de Pagamento:* {{forma_pagamento}}\n"
    "{{info_troco}}\n\n"
    "🛍️ *Itens do Pedido:*\n"
    "{{lista_itens}}\n\n"
    "💰 Subtotal: R$ {{subtotal}}\n"
    "🚚 Frete: R$ {{frete}}\n"
    "💵 *TOTAL: R$ {{total}}*\n\n"
    "📝 *Obs:* {{observacoes}}\n"
    "🕐 Pedido em: {{data_hora}}"
)


TIPO_PIX_CHOICES = [
    ('cpf', 'CPF'),
    ('cnpj', 'CNPJ'),
    ('email', 'E-mail'),
    ('telefone', 'Telefone'),
    ('aleatoria', 'Chave Aleatória'),
]


class Configuracao(models.Model):
    nome_loja = models.CharField('Nome da Loja', max_length=100, default='LJ Utilitários')
    whatsapp_numero = models.CharField(
        'WhatsApp', max_length=20, blank=True,
        help_text='Apenas números com DDD, ex: 11999999999'
    )
    whatsapp_mensagem_template = models.TextField(
        'Template da Mensagem', default=DEFAULT_TEMPLATE
    )
    cidade_base = models.CharField('Cidade Base', max_length=100, blank=True)
    cidades_atendidas = models.TextField(
        'Cidades Atendidas',
        help_text='Separadas por vírgula', blank=True
    )
    logo = models.ImageField('Logo Principal', upload_to='loja/', blank=True, null=True,
                             validators=[validar_imagem],
                             help_text='PNG com fundo transparente. Ideal: 200×200px. Máx: 5 MB.')
    logo_navbar = models.ImageField('Logo Navbar', upload_to='loja/', blank=True, null=True,
                                    validators=[validar_imagem],
                                    help_text='Versão horizontal para a navbar. PNG transparente. Ideal: 240×80px. Máx: 5 MB.')
    banner_principal = models.ImageField(
        'Banner Principal', upload_to='banners/', blank=True, null=True
    )
    texto_banner = models.CharField('Título do Banner', max_length=200, blank=True,
                                    default='Utilitários de Qualidade')
    subtexto_banner = models.CharField('Subtexto do Banner', max_length=300, blank=True,
                                       default='Entrega rápida na sua cidade')
    frete_fixo = models.DecimalField('Frete Fixo (R$)', max_digits=8, decimal_places=2, default=10.00)
    frete_gratis_acima = models.DecimalField(
        'Frete Grátis Acima de (R$)', max_digits=10, decimal_places=2, default=150.00
    )

    # Fretes por cidade
    frete_tres_rios = models.DecimalField(
        'Frete Três Rios, RJ', max_digits=8, decimal_places=2, default=8.00,
        help_text='Cidade da loja — frete mais barato'
    )
    frete_levy = models.DecimalField(
        'Frete Com. Levy Gasparian', max_digits=8, decimal_places=2, default=15.00
    )
    frete_paraiba_sul = models.DecimalField(
        'Frete Paraíba do Sul', max_digits=8, decimal_places=2, default=18.00
    )
    frete_bemposta = models.DecimalField(
        'Frete Bemposta', max_digits=8, decimal_places=2, default=20.00
    )
    frete_areal = models.DecimalField(
        'Frete Areal', max_digits=8, decimal_places=2, default=22.00
    )

    # Pix
    chave_pix = models.CharField('Chave Pix', max_length=100, blank=True)
    tipo_chave_pix = models.CharField(
        'Tipo da Chave Pix', max_length=20,
        choices=TIPO_PIX_CHOICES, default='aleatoria', blank=True
    )

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for field_name, max_size in [('logo', (200, 200)), ('logo_navbar', (240, 80))]:
            field = getattr(self, field_name)
            if not field:
                continue
            try:
                from PIL import Image
                img = Image.open(field.path)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.thumbnail(max_size, Image.LANCZOS)
                img.save(field.path, 'PNG', optimize=True)
            except Exception:
                pass

    def __str__(self):
        return self.nome_loja

    def get_cidades_lista(self):
        if self.cidades_atendidas:
            return [c.strip() for c in self.cidades_atendidas.split(',') if c.strip()]
        return []

    def get_frete_cidade(self, cidade):
        mapa = {
            'Três Rios, RJ': self.frete_tres_rios,
            'Comendador Levy Gasparian': self.frete_levy,
            'Paraíba do Sul': self.frete_paraiba_sul,
            'Bemposta': self.frete_bemposta,
            'Areal': self.frete_areal,
        }
        return mapa.get(cidade, self.frete_tres_rios)

    def get_tipo_pix_label(self):
        return dict(TIPO_PIX_CHOICES).get(self.tipo_chave_pix, self.tipo_chave_pix)

    @classmethod
    def get_config(cls):
        config = cls.objects.first()
        if not config:
            config = cls.objects.create(nome_loja='LJ Utilitários')
        return config


class LogConsentimento(models.Model):
    ACOES = [
        ('aceite_cookies', 'Aceite de Cookies'),
        ('consentimento_checkout', 'Consentimento no Checkout'),
        ('aceite_termos_google', 'Aceite de Termos (Google Login)'),
        ('exclusao_conta', 'Exclusão de Conta'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='logs_consentimento', verbose_name='Usuário'
    )
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    acao = models.CharField('Ação', max_length=50, choices=ACOES)
    data_hora = models.DateTimeField('Data/Hora', auto_now_add=True)
    detalhes = models.JSONField('Detalhes', default=dict, blank=True)

    class Meta:
        verbose_name = 'Log de Consentimento'
        verbose_name_plural = 'Logs de Consentimento'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.get_acao_display()} — {self.data_hora:%d/%m/%Y %H:%M}'
