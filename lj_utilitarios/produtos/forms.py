from django import forms
from .models import Produto, Categoria


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'slug', 'descricao', 'preco', 'preco_promocional',
            'estoque', 'categoria', 'imagem_principal', 'ativo', 'destaque'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'fc'}),
            'slug': forms.TextInput(attrs={'class': 'fc'}),
            'descricao': forms.Textarea(attrs={'class': 'fc', 'rows': 4}),
            'preco': forms.NumberInput(attrs={'class': 'fc', 'step': '0.01'}),
            'preco_promocional': forms.NumberInput(attrs={'class': 'fc', 'step': '0.01'}),
            'estoque': forms.NumberInput(attrs={'class': 'fc'}),
            'categoria': forms.Select(attrs={'class': 'fc'}),
            'imagem_principal': forms.ClearableFileInput(attrs={'class': 'fc'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'cb'}),
            'destaque': forms.CheckboxInput(attrs={'class': 'cb'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'slug', 'icone_emoji', 'icone_img', 'ordem', 'ativo']
        widgets = {
            'nome':        forms.TextInput(attrs={'class': 'fc'}),
            'slug':        forms.TextInput(attrs={'class': 'fc'}),
            'icone_emoji': forms.TextInput(attrs={'class': 'fc', 'placeholder': '📦', 'maxlength': '10'}),
            'icone_img':   forms.ClearableFileInput(attrs={'class': 'fc', 'accept': 'image/png,image/jpeg,image/webp'}),
            'ordem':       forms.NumberInput(attrs={'class': 'fc'}),
            'ativo':       forms.CheckboxInput(attrs={'class': 'cb'}),
        }
