# ⚽ Bolão da Firma - Copa 2026

Aplicação completa para bolão da Copa do Mundo 2026, com palpites, grupos e ranking em tempo real.

## 🏗️ Arquitetura

- **Backend**: FastAPI (Python) - `/app`
- **Frontend**: React 18 + Vite (TypeScript) - `/frontend`
- **Database**: PostgreSQL (Railway)
- **Deploy**: Railway

## 📁 Estrutura

```
bolao-copa-2026/
├── app/                      # Backend FastAPI
│   ├── routes/              # Endpoints (auth, predictions, groups, etc)
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── services/            # Lógica de negócio
│   ├── security/            # Autenticação, JWT, criptografia
│   ├── jobs/                # Background jobs (APScheduler)
│   ├── providers/           # Provedores de dados (IA, Fixtures)
│   ├── config.py            # Configurações
│   ├── db.py                # Database
│   ├── main.py              # FastAPI app
│   └── cli.py               # CLI commands
├── frontend/                 # Frontend React + Vite
│   ├── src/
│   │   ├── api/             # Cliente HTTP e hooks React Query
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── pages/           # Páginas (Dashboard, Matches, etc)
│   │   ├── providers/       # Context API (Auth)
│   │   ├── types/           # TypeScript types
│   │   ├── router.tsx       # React Router config
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── requirements.txt          # Dependências Python
├── Dockerfile               # Build Docker backend
├── docker-compose.yml       # Orquestração local
└── README.md               # Este arquivo
```

## 🚀 Quick Start

### Backend Local

```bash
# 1. Virtual env
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 2. Dependências
pip install -r requirements.txt

# 3. Database (local PostgreSQL)
export DATABASE_URL="postgresql://user:pass@localhost:5432/bolao"

# 4. Inicializar banco
python -m app.cli init-db

# 5. Rodar
python -m app.main

# Acesso: http://localhost:8000/docs
```

### Frontend Local

```bash
cd frontend

# 1. Instalar
npm install --legacy-peer-deps

# 2. Config
cp .env.example .env.local
# Editar VITE_API_BASE_URL=http://localhost:8000

# 3. Dev server
npm run dev

# Acesso: http://localhost:3000
```

## 🌐 Deploy Railway

### 1. Backend

```bash
# Conectar Railway
railway link

# Deploy automático (git push)
railway deploy
```

Railway cria:
- Container Python + FastAPI
- PostgreSQL database
- Variáveis de ambiente

### 2. Frontend

```bash
cd frontend

# Build
npm run build

# Deploy no Railway ou Vercel
railway deploy
```

## 🔐 Autenticação

### Sistema

- **Cookies HttpOnly**: JWT armazenado em cookie seguro
- **CSRF Protection**: Token automático
- **Social Login**: Google + Facebook (OAuth2)
- **Email/Password**: Registro e login por e-mail

## 📊 API Endpoints

### Auth
- `GET /auth/me` - Usuário atual
- `POST /auth/login` - Login email
- `POST /auth/register` - Cadastro
- `POST /auth/logout` - Logout

### Matches
- `GET /matches` - Lista (filtros: stage, status, date)
- `GET /matches/:id` - Detalhe

### Predictions
- `POST /predictions` - Criar palpite
- `PUT /predictions/:id` - Atualizar
- `GET /predictions/me` - Meus palpites

### Groups
- `GET /groups` - Meus grupos
- `POST /groups` - Criar
- `GET /groups/:id` - Detalhe
- `POST /groups/:id/join` - Entrar

### Rankings
- `GET /rankings/global` - Global
- `GET /rankings/group/:id` - Por grupo

### AI
- `POST /ai/suggest` - Sugestão IA
- `POST /ai/suggest/bulk` - Múltiplas

### Admin
- `POST /admin/fixtures/import-json` - Importar fixtures
- `POST /admin/matches/refresh` - Atualizar resultados

## 🛠️ Tecnologias

### Backend
- FastAPI (async web framework)
- SQLAlchemy (ORM)
- Pydantic (validation)
- PostgreSQL (database)
- APScheduler (background jobs)
- Groq API (AI - Llama 3)

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- React Router (navigation)
- React Query (data fetching)
- Tailwind CSS (styling)
- React Hook Form + Zod (forms)

## 📝 Credenciais de Teste

```
Email: test@bolao.com
Senha: Test123456!
```

## 🎯 Features

- ✅ Autenticação (Email, Google, Facebook)
- ✅ Dashboard com próximos jogos
- ✅ Sistema de palpites
- ✅ Sugestões de IA (Llama 3)
- ✅ Grupos de bolão
- ✅ Ranking global e por grupo
- ✅ Perfil de usuário
- ✅ Admin panel
- ✅ Background jobs (atualização de resultados)

## 📄 Licença

MIT

---

**Desenvolvido com ❤️ para a Copa do Mundo 2026**
