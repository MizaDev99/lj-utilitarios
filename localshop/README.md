# LocalShop

E-commerce marketplace para vendas locais com integração WhatsApp.

## Instalação

### 1. Clone / acesse a pasta
```bash
cd localshop
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env e adicione sua SECRET_KEY
```

### 5. Execute as migrations
```bash
python manage.py migrate
```

### 6. Crie os dados iniciais (superuser + produtos de exemplo)
```bash
python manage.py criar_dados_iniciais
```

### 7. Inicie o servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## Credenciais do painel

- URL: http://127.0.0.1:8000/painel/login/
- Usuário: `admin`
- Senha: `admin123`

## Configuração do WhatsApp

1. Acesse o painel → Configurações
2. Preencha o número WhatsApp da loja (apenas números, com DDD)
3. Personalize o template da mensagem
4. Configure as cidades atendidas

## Estrutura

```
localshop/
├── core/           # Homepage + Configurações da loja
├── produtos/       # Catálogo de produtos e categorias
├── carrinho/       # Carrinho de compras (baseado em sessão)
├── pedidos/        # Checkout + integração WhatsApp
├── painel/         # Painel administrativo customizado
├── templates/      # HTML templates
└── static/         # CSS, JS e imagens
```

## Funcionalidades

- Catálogo de produtos com categorias, filtros e busca
- Carrinho de compras com atualização via AJAX
- Checkout com validação de cidade
- Envio automático do pedido via WhatsApp (redirecionamento)
- Painel admin completo: produtos, categorias, pedidos, configurações
- Design responsivo inspirado em Shopee/Mercado Livre
- Configurações globais salvas no banco (nome, logo, frete, cores)

## Variáveis de ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta do Django | insecure-key |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |

## Para produção

1. Defina `DEBUG=False` no `.env`
2. Gere uma `SECRET_KEY` forte
3. Configure `ALLOWED_HOSTS` com seu domínio
4. Execute `python manage.py collectstatic`
5. Configure um servidor de banco de dados (PostgreSQL recomendado)
