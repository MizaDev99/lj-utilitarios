from django.contrib import admin
from .models import Categoria, Produto, ImagemProduto

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(ImagemProduto)
