from django import forms
from django.utils.safestring import mark_safe
from .models import Pedido


CIDADES_CHOICES = [
    ('', '— Selecione a cidade —'),
    ('Três Rios, RJ', 'Três Rios, RJ'),
    ('Comendador Levy Gasparian', 'Comendador Levy Gasparian'),
    ('Paraíba do Sul', 'Paraíba do Sul'),
    ('Bemposta', 'Bemposta'),
    ('Areal', 'Areal'),
]


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nome_cliente', 'telefone_cliente',
            'forma_recebimento', 'cidade_cliente', 'endereco_cliente',
            'forma_pagamento', 'troco_para', 'observacoes',
        ]
        widgets = {
            'nome_cliente': forms.TextInput(attrs={'class': 'fc', 'placeholder': 'Nome completo'}),
            'telefone_cliente': forms.TextInput(attrs={'class': 'fc', 'placeholder': '(24) 99999-9999'}),
            'forma_recebimento': forms.RadioSelect(),
            'cidade_cliente': forms.Select(
                choices=CIDADES_CHOICES, attrs={'class': 'fc', 'id': 'id_cidade_select'}
            ),
            'endereco_cliente': forms.Textarea(attrs={
                'class': 'fc', 'rows': 3, 'placeholder': 'Rua, número, bairro, complemento'
            }),
            'forma_pagamento': forms.RadioSelect(),
            'troco_para': forms.NumberInput(attrs={'class': 'fc', 'step': '0.01', 'placeholder': 'Ex: 50.00'}),
            'observacoes': forms.Textarea(attrs={'class': 'fc', 'rows': 2, 'placeholder': 'Alguma observação? (opcional)'}),
        }
        labels = {
            'nome_cliente': 'Nome Completo',
            'telefone_cliente': 'Telefone / WhatsApp',
            'cidade_cliente': 'Cidade de Entrega',
            'endereco_cliente': 'Endereço Completo',
            'forma_recebimento': 'Forma de Recebimento',
            'forma_pagamento': 'Forma de Pagamento',
            'troco_para': 'Precisa de troco? Para quanto? (R$)',
            'observacoes': 'Observações',
        }

    lgpd_aceito = forms.BooleanField(
        required=True,
        label=mark_safe(
            'Li e concordo com a <a href="/privacidade/" target="_blank" class="link-lgpd">Política de Privacidade</a> '
            'e os <a href="/termos/" target="_blank" class="link-lgpd">Termos de Uso</a>. '
            'Autorizo o uso dos meus dados para processar este pedido e receber contato via WhatsApp.'
        ),
        error_messages={'required': 'Você precisa aceitar os termos para continuar.'},
        widget=forms.CheckboxInput(attrs={'class': 'cb-lgpd'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cidade_cliente'].required = False
        self.fields['endereco_cliente'].required = False
        self.fields['troco_para'].required = False

    def clean(self):
        cleaned = super().clean()
        forma = cleaned.get('forma_recebimento', 'entrega')
        cidade = cleaned.get('cidade_cliente', '')
        endereco = cleaned.get('endereco_cliente', '').strip()
        pagamento = cleaned.get('forma_pagamento', '')

        if forma == 'entrega':
            if not cidade:
                self.add_error('cidade_cliente', 'Selecione a cidade de entrega.')
            if not endereco:
                self.add_error('endereco_cliente', 'Informe o endereço completo de entrega.')

        if pagamento == 'dinheiro':
            troco = cleaned.get('troco_para')
            if troco is not None and troco <= 0:
                self.add_error('troco_para', 'O valor do troco deve ser maior que zero.')

        return cleaned
