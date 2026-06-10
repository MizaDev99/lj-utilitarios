from django import forms
from .models import Produto, Categoria, ImagemProduto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'slug', 'descricao', 'preco', 'preco_promocional',
            'estoque', 'categoria', 'imagem_principal', 'ativo', 'destaque'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_promocional': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'imagem_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destaque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'slug', 'icone', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'icone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 📱'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ImagemProdutoForm(forms.ModelForm):
    class Meta:
        model = ImagemProduto
        fields = ['imagem']
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
