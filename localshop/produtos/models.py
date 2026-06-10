from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    nome = models.CharField('Nome', max_length=100)
    slug = models.SlugField(unique=True)
    icone = models.CharField('Ícone', max_length=10, blank=True, help_text='Emoji ou texto curto')
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Produto(models.Model):
    nome = models.CharField('Nome', max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    descricao = models.TextField('Descrição', blank=True)
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    preco_promocional = models.DecimalField(
        'Preço Promocional', max_digits=10, decimal_places=2, null=True, blank=True
    )
    estoque = models.IntegerField('Estoque', default=0)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='produtos', verbose_name='Categoria'
    )
    imagem_principal = models.ImageField(
        'Imagem Principal', upload_to='produtos/', blank=True, null=True
    )
    ativo = models.BooleanField('Ativo', default=True)
    destaque = models.BooleanField('Destaque', default=False)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    @property
    def preco_atual(self):
        return self.preco_promocional if self.preco_promocional else self.preco

    @property
    def tem_promocao(self):
        return bool(self.preco_promocional)

    @property
    def percentual_desconto(self):
        if self.preco_promocional and self.preco > 0:
            return int(((self.preco - self.preco_promocional) / self.preco) * 100)
        return 0


class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, related_name='imagens', verbose_name='Produto'
    )
    imagem = models.ImageField('Imagem', upload_to='produtos/galeria/')

    class Meta:
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens do Produto'

    def __str__(self):
        return f'Imagem de {self.produto.nome}'
