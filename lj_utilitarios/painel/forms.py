from django import forms
from core.models import Configuracao
from pedidos.models import Pedido


class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = [
            'nome_loja', 'whatsapp_numero', 'whatsapp_mensagem_template',
            'cidade_base', 'cidades_atendidas',
            'logo', 'logo_navbar', 'banner_principal',
            'texto_banner', 'subtexto_banner',
            'frete_fixo', 'frete_gratis_acima',
            'frete_tres_rios', 'frete_levy', 'frete_paraiba_sul', 'frete_bemposta', 'frete_areal',
            'chave_pix', 'tipo_chave_pix',
        ]
        widgets = {f: forms.TextInput(attrs={'class': 'fc'}) for f in [
            'nome_loja', 'whatsapp_numero', 'cidade_base', 'texto_banner', 'subtexto_banner', 'chave_pix'
        ]}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['whatsapp_mensagem_template', 'cidades_atendidas']:
            self.fields[f].widget = forms.Textarea(attrs={
                'class': 'fc',
                'rows': 4 if f == 'cidades_atendidas' else 13,
                'style': 'font-family:monospace;' if 'mensagem' in f else '',
            })
        for f in ['logo', 'logo_navbar', 'banner_principal']:
            self.fields[f].widget = forms.ClearableFileInput(
                attrs={'class': 'fc', 'accept': 'image/png,image/jpeg,image/webp'}
            )
        for f in ['frete_fixo', 'frete_gratis_acima',
                  'frete_tres_rios', 'frete_levy', 'frete_paraiba_sul', 'frete_bemposta', 'frete_areal']:
            self.fields[f].widget = forms.NumberInput(attrs={'class': 'fc', 'step': '0.01'})
        self.fields['tipo_chave_pix'].widget = forms.Select(attrs={'class': 'fc'})


class StatusPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'fc'})}
