# LJ Utilitários

E-commerce marketplace dark mode para vendas locais com Firebase Auth + Supabase.

## Início Rápido (desenvolvimento local)

```bash
cd lj_utilitarios
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env                          # edite se precisar
python manage.py migrate
python manage.py criar_dados_iniciais
python manage.py runserver
```

- **Loja:** http://127.0.0.1:8000
- **Painel:** http://127.0.0.1:8000/painel/login/ → `admin` / `admin123`

> Sem Firebase/Supabase configurados, o app funciona com SQLite + armazenamento local.

---

## Configuração Firebase (Google Login)

1. Crie um projeto em [console.firebase.google.com](https://console.firebase.google.com)
2. Ative **Authentication → Google**
3. Em **Configurações do projeto → Geral** → copie as credenciais Web para o `.env`
4. Em **Configurações → Contas de Serviço** → gere e baixe o JSON da service account
5. Coloque o JSON na raiz do projeto e defina `FIREBASE_SERVICE_ACCOUNT_JSON=nome-do-arquivo.json`
6. Em **Authentication → Settings → Domínios autorizados** → adicione seu domínio

```env
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=meu-projeto.firebaseapp.com
FIREBASE_PROJECT_ID=meu-projeto
FIREBASE_STORAGE_BUCKET=meu-projeto.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abc123
FIREBASE_SERVICE_ACCOUNT_JSON=firebase-service-account.json
```

---

## Configuração Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Em **Storage** → crie os buckets `produtos` e `banners` (público)
3. Copie as credenciais para o `.env`

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIs...
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=sua-senha
DB_HOST=db.xxxx.supabase.co
DB_PORT=5432
```

---

## Logo

Coloque o arquivo `logo_lj.jpeg` em `static/img/` e configure no painel admin.

---

## Identidade Visual

| Variável | Cor | Uso |
|----------|-----|-----|
| `--cor-fundo` | `#050A1F` | Background geral |
| `--cor-primaria` | `#2200FF` | Botões, destaques |
| `--cor-secundaria` | `#0A1A6B` | Cards, navbar |
| `--cor-acento` | `#4D6AFF` | Links, badges, ícones |
| `--cor-sucesso` | `#00C48C` | Confirmações |
| `--cor-alerta` | `#FFB800` | Frete, avisos |

Tipografia: **Playfair Display** (títulos) + **DM Sans** (corpo)

---

## Estrutura

```
lj_utilitarios/
├── core/           # Homepage + Configurações + SupabaseStorage
├── produtos/       # Catálogo com categorias
├── carrinho/       # Carrinho em sessão com AJAX
├── pedidos/        # Checkout + redirect WhatsApp
├── painel/         # Admin customizado dark mode
├── autenticacao/   # Firebase Auth + PerfilCliente
├── templates/      # 20 templates HTML
└── static/         # CSS dark premium + JS + Firebase SDK
```
