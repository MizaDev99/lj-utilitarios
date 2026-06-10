from django import forms
from .models import Pedido
from core.models import Configuracao


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nome_cliente', 'telefone_cliente', 'cidade_cliente', 'endereco_cliente', 'observacoes']
        widgets = {
            'nome_cliente': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Seu nome completo'
            }),
            'telefone_cliente': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '(11) 99999-9999'
            }),
            'cidade_cliente': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sua cidade', 'id': 'id_cidade'
            }),
            'endereco_cliente': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Rua, número, bairro, complemento'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Alguma observação sobre o pedido? (opcional)'
            }),
        }
        labels = {
            'nome_cliente': 'Nome Completo',
            'telefone_cliente': 'Telefone / WhatsApp',
            'cidade_cliente': 'Cidade',
            'endereco_cliente': 'Endereço',
            'observacoes': 'Observações',
        }

    def clean_cidade_cliente(self):
        cidade = self.cleaned_data.get('cidade_cliente', '').strip()
        config = Configuracao.get_config()
        cidades = config.get_cidades_lista()
        if cidades:
            cidades_lower = [c.lower() for c in cidades]
            if cidade.lower() not in cidades_lower:
                cidades_str = ', '.join(cidades)
                raise forms.ValidationError(
                    f'Desculpe, não atendemos esta cidade. '
                    f'Cidades atendidas: {cidades_str}'
                )
        return cidade
