from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Configuracao
from produtos.models import Categoria, Produto


class Command(BaseCommand):
    help = 'Cria dados iniciais: superuser, configuração, categorias e produtos de exemplo'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais para LJ Utilitários...')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@lj.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('  Superuser admin/admin123 criado'))

        if not Configuracao.objects.exists():
            Configuracao.objects.create(
                nome_loja='LJ Utilitários',
                whatsapp_numero='11999999999',
                cidade_base='São Paulo',
                cidades_atendidas='São Paulo, Guarulhos, Osasco, Santo André, São Bernardo do Campo',
                texto_banner='Utilitários de Qualidade',
                subtexto_banner='Entrega rápida em toda a região',
                frete_fixo=12.00,
                frete_gratis_acima=200.00,
            )
            self.stdout.write(self.style.SUCCESS('  Configuração da loja criada'))

        categorias_dados = [
            {'nome': 'Ferramentas', 'slug': 'ferramentas', 'icone': '🔧', 'ordem': 1},
            {'nome': 'Elétrica', 'slug': 'eletrica', 'icone': '⚡', 'ordem': 2},
            {'nome': 'Hidráulica', 'slug': 'hidraulica', 'icone': '🚿', 'ordem': 3},
            {'nome': 'Jardinagem', 'slug': 'jardinagem', 'icone': '🌿', 'ordem': 4},
            {'nome': 'Construção', 'slug': 'construcao', 'icone': '🏗️', 'ordem': 5},
            {'nome': 'Segurança', 'slug': 'seguranca', 'icone': '🔒', 'ordem': 6},
        ]

        categorias = {}
        for d in categorias_dados:
            cat, criado = Categoria.objects.get_or_create(
                slug=d['slug'],
                defaults={'nome': d['nome'], 'icone': d['icone'], 'ordem': d['ordem'], 'ativo': True}
            )
            categorias[d['slug']] = cat
            if criado:
                self.stdout.write(self.style.SUCCESS(f'  Categoria "{cat.nome}" criada'))

        produtos_dados = [
            {
                'nome': 'Kit Chaves de Fenda 6 peças',
                'slug': 'kit-chaves-fenda-6-pecas',
                'descricao': 'Kit completo com 6 chaves de fenda de diferentes tamanhos. Cabo ergonômico antiderrapante, aço inox de alta durabilidade.',
                'preco': 89.90,
                'preco_promocional': 69.90,
                'estoque': 25,
                'categoria': 'ferramentas',
                'destaque': True,
            },
            {
                'nome': 'Furadeira de Impacto 750W',
                'slug': 'furadeira-impacto-750w',
                'descricao': 'Furadeira de impacto 750W com mandril de 13mm, 2 velocidades, cabo antivibração e maleta de transporte.',
                'preco': 329.90,
                'preco_promocional': 279.90,
                'estoque': 10,
                'categoria': 'ferramentas',
                'destaque': True,
            },
            {
                'nome': 'Tomada Inteligente Wi-Fi',
                'slug': 'tomada-inteligente-wifi',
                'descricao': 'Tomada smart com controle via app, compatível com Alexa e Google Assistente. Monitoramento de consumo em tempo real.',
                'preco': 79.90,
                'preco_promocional': None,
                'estoque': 40,
                'categoria': 'eletrica',
                'destaque': True,
            },
            {
                'nome': 'Cabo PP 2x2,5mm Rolo 25m',
                'slug': 'cabo-pp-2x25mm-25m',
                'descricao': 'Cabo PP flexível 2x2,5mm², isolamento duplo, rolo com 25 metros. Certificado pelo Inmetro.',
                'preco': 119.00,
                'preco_promocional': 99.00,
                'estoque': 15,
                'categoria': 'eletrica',
                'destaque': False,
            },
            {
                'nome': 'Registro Gaveta 3/4" Bronze',
                'slug': 'registro-gaveta-3-4-bronze',
                'descricao': 'Registro de gaveta 3/4 em bronze com acabamento cromado. Alta resistência à corrosão.',
                'preco': 34.90,
                'preco_promocional': None,
                'estoque': 60,
                'categoria': 'hidraulica',
                'destaque': False,
            },
            {
                'nome': 'Kit Irrigação Automática',
                'slug': 'kit-irrigacao-automatica',
                'descricao': 'Kit completo para irrigação automática com timer digital, 20 gotejadores e 15m de mangueira micro.',
                'preco': 149.90,
                'preco_promocional': 119.90,
                'estoque': 20,
                'categoria': 'jardinagem',
                'destaque': True,
            },
            {
                'nome': 'Cadeado de Alta Segurança 40mm',
                'slug': 'cadeado-alta-seguranca-40mm',
                'descricao': 'Cadeado em aço carbono temperado, 40mm, resistente a corte e impacto. 3 chaves inclusas.',
                'preco': 59.90,
                'preco_promocional': None,
                'estoque': 35,
                'categoria': 'seguranca',
                'destaque': False,
            },
            {
                'nome': 'Tela de Aço Fio 12 1m x 2m',
                'slug': 'tela-aco-fio12-1x2m',
                'descricao': 'Tela soldada de aço galvanizado fio 12, malha 5x5cm, painel 1m x 2m. Ideal para vedação e construção.',
                'preco': 45.00,
                'preco_promocional': None,
                'estoque': 50,
                'categoria': 'construcao',
                'destaque': False,
            },
        ]

        for d in produtos_dados:
            cat = categorias.get(d.pop('categoria'))
            produto, criado = Produto.objects.get_or_create(
                slug=d['slug'],
                defaults={**d, 'categoria': cat, 'ativo': True}
            )
            if criado:
                self.stdout.write(self.style.SUCCESS(f'  Produto "{produto.nome}" criado'))

        self.stdout.write(self.style.SUCCESS('\nDados iniciais criados!'))
        self.stdout.write('\nAcesse o painel: http://127.0.0.1:8000/painel/login/')
        self.stdout.write('Login: admin | Senha: admin123')
