from django import forms
from core.models import Configuracao
from pedidos.models import Pedido


class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = [
            'nome_loja', 'whatsapp_numero', 'whatsapp_mensagem_template',
            'cidade_base', 'cidades_atendidas', 'logo', 'cor_primaria',
            'banner_principal', 'texto_banner', 'frete_fixo', 'frete_gratis_acima',
        ]
        widgets = {
            'nome_loja': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_numero': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '11999999999'
            }),
            'whatsapp_mensagem_template': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 14, 'style': 'font-family: monospace;'
            }),
            'cidade_base': forms.TextInput(attrs={'class': 'form-control'}),
            'cidades_atendidas': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'São Paulo, Guarulhos, Osasco'
            }),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'cor_primaria': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'banner_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'texto_banner': forms.TextInput(attrs={'class': 'form-control'}),
            'frete_fixo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'frete_gratis_acima': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class StatusPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
