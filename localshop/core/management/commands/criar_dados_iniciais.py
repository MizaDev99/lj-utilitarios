from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Configuracao
from produtos.models import Categoria, Produto


class Command(BaseCommand):
    help = 'Cria dados iniciais: superuser, configuração, categorias e produtos de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais...')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@localshop.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('  Superuser admin/admin123 criado'))
        else:
            self.stdout.write('  Superuser "admin" já existe')

        if not Configuracao.objects.exists():
            Configuracao.objects.create(
                nome_loja='LocalShop',
                whatsapp_numero='11999999999',
                cidade_base='São Paulo',
                cidades_atendidas='São Paulo, Guarulhos, Osasco, Santo André, São Bernardo do Campo',
                cor_primaria='#FF6B00',
                texto_banner='As melhores ofertas da sua cidade!',
                frete_fixo=10.00,
                frete_gratis_acima=150.00,
            )
            self.stdout.write(self.style.SUCCESS('  Configuração padrão criada'))
        else:
            self.stdout.write('  Configuração já existe')

        categorias_dados = [
            {'nome': 'Eletrônicos', 'slug': 'eletronicos', 'icone': '📱'},
            {'nome': 'Roupas', 'slug': 'roupas', 'icone': '👕'},
            {'nome': 'Alimentos', 'slug': 'alimentos', 'icone': '🍎'},
            {'nome': 'Casa e Jardim', 'slug': 'casa-jardim', 'icone': '🏠'},
            {'nome': 'Esportes', 'slug': 'esportes', 'icone': '⚽'},
        ]

        categorias = {}
        for dados in categorias_dados:
            cat, criado = Categoria.objects.get_or_create(
                slug=dados['slug'],
                defaults={'nome': dados['nome'], 'icone': dados['icone'], 'ativo': True}
            )
            categorias[dados['slug']] = cat
            if criado:
                self.stdout.write(self.style.SUCCESS(f'  Categoria "{cat.nome}" criada'))

        produtos_dados = [
            {
                'nome': 'Smartphone Android 128GB',
                'slug': 'smartphone-android-128gb',
                'descricao': 'Smartphone moderno com tela de 6.5", câmera de 48MP, bateria de 5000mAh e 128GB de armazenamento interno.',
                'preco': 899.90,
                'preco_promocional': 749.90,
                'estoque': 15,
                'categoria': 'eletronicos',
                'destaque': True,
            },
            {
                'nome': 'Fone de Ouvido Bluetooth',
                'slug': 'fone-ouvido-bluetooth',
                'descricao': 'Fone sem fio com cancelamento de ruído, 30h de bateria e som de alta qualidade.',
                'preco': 199.90,
                'preco_promocional': None,
                'estoque': 30,
                'categoria': 'eletronicos',
                'destaque': True,
            },
            {
                'nome': 'Camiseta Básica Premium',
                'slug': 'camiseta-basica-premium',
                'descricao': 'Camiseta 100% algodão, corte moderno, disponível em várias cores. Conforto e estilo para o dia a dia.',
                'preco': 59.90,
                'preco_promocional': 39.90,
                'estoque': 50,
                'categoria': 'roupas',
                'destaque': False,
            },
            {
                'nome': 'Kit Temperos Gourmet',
                'slug': 'kit-temperos-gourmet',
                'descricao': 'Kit com 6 temperos artesanais selecionados para elevar o sabor das suas receitas.',
                'preco': 45.00,
                'preco_promocional': None,
                'estoque': 20,
                'categoria': 'alimentos',
                'destaque': True,
            },
            {
                'nome': 'Luminária de Mesa LED',
                'slug': 'luminaria-mesa-led',
                'descricao': 'Luminária LED com 3 níveis de intensidade, porta USB lateral e design moderno para seu escritório.',
                'preco': 89.90,
                'preco_promocional': 69.90,
                'estoque': 25,
                'categoria': 'casa-jardim',
                'destaque': True,
            },
            {
                'nome': 'Bola de Futebol Campo',
                'slug': 'bola-futebol-campo',
                'descricao': 'Bola oficial tamanho 5, material sintético resistente, ideal para jogos em campo gramado.',
                'preco': 79.90,
                'preco_promocional': None,
                'estoque': 40,
                'categoria': 'esportes',
                'destaque': False,
            },
        ]

        for dados in produtos_dados:
            cat_slug = dados.pop('categoria')
            categoria = categorias.get(cat_slug)
            produto, criado = Produto.objects.get_or_create(
                slug=dados['slug'],
                defaults={**dados, 'categoria': categoria, 'ativo': True}
            )
            if criado:
                self.stdout.write(self.style.SUCCESS(f'  Produto "{produto.nome}" criado'))

        self.stdout.write(self.style.SUCCESS('\nDados iniciais criados com sucesso!'))
        self.stdout.write('\nAcesse o painel em: http://127.0.0.1:8000/painel/login/')
        self.stdout.write('Login: admin | Senha: admin123')
