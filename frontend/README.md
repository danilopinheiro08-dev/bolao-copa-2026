# ⚽ Bolão Copa 2026 - Frontend

Frontend React Vite para o Bolão da Copa do Mundo 2026.

## Features

- ✅ Autenticação (Google, Facebook, E-mail)
- ✅ Dashboard com próximos jogos
- ✅ Lista de jogos com filtros
- ✅ Sistema de palpites
- ✅ Sugestões de IA
- ✅ Gerenciamento de grupos
- ✅ Rankings global e por grupo
- ✅ Perfil de usuário
- ✅ Admin panel (para usuários admin)

## Tech Stack

- **React 18** + TypeScript
- **Vite** (dev server rápido)
- **React Router** (navegação)
- **React Query** (cache de dados)
- **Tailwind CSS** (estilos)
- **React Hook Form** + Zod (validação)
- **Axios** (HTTP client)
- **Dayjs** (datas com timezone)
- **Lucide Icons** (ícones)

## Setup Local

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env.local
```

Editar `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Rodar dev server

```bash
npm run dev
```

Acessar: http://localhost:3000

## Build para Produção

```bash
npm run build
```

Output em `dist/`

## Autenticação

### Login Social

Botões de **Google** e **Facebook** redirecionam para:
- `${API_BASE_URL}/auth/google/login`
- `${API_BASE_URL}/auth/facebook/login`

Backend define cookie HttpOnly `session` com token JWT.

### Login por E-mail

Credenciais de teste:
- Email: `test@bolao.com`
- Senha: `Test123456!`

## Estrutura de Pastas

```
src/
├── api/
│   ├── client.ts         # Axios instance com interceptors
│   ├── hooks.ts          # React Query hooks (useMatches, useMe, etc)
│   └── queryClient.ts    # Configuração React Query
├── components/
│   ├── AppLayout.tsx     # Layout privado (sidebar + header)
│   ├── ProtectedRoute.tsx # Rota protegida
│   └── MatchCard.tsx     # Componente de jogo
├── pages/
│   ├── Landing.tsx       # Página inicial
│   ├── Login.tsx         # Login
│   ├── Register.tsx      # Cadastro
│   ├── Dashboard.tsx     # Dashboard privado
│   ├── Matches.tsx       # Lista de jogos
│   ├── Picks.tsx         # Meus palpites
│   ├── Groups.tsx        # Grupos
│   ├── Rankings.tsx      # Ranking global
│   ├── Profile.tsx       # Perfil
│   └── Admin.tsx         # Admin panel
├── providers/
│   └── AuthProvider.tsx  # Contexto de autenticação
├── types/
│   └── index.ts          # TypeScript tipos
├── styles/
│   └── globals.css       # Estilos globais + Tailwind
├── router.tsx            # Configuração React Router
└── main.tsx              # Entry point
```

## API Endpoints Esperados

Backend deve fornecer:

```
GET    /auth/me
POST   /auth/login
POST   /auth/register
POST   /auth/logout

GET    /matches?status=&stage=
POST   /predictions
PUT    /predictions/:id
GET    /predictions/me

GET    /groups
POST   /groups
GET    /groups/:id
POST   /groups/:id/join

GET    /rankings/global
GET    /rankings/group/:id

POST   /ai/suggest
POST   /ai/suggest/bulk

POST   /admin/fixtures/import-json
POST   /admin/matches/refresh
```

## Deploy

### Vercel

```bash
npm run build
vercel deploy
```

### Railway

```bash
railway up
```

Configurar variável de ambiente:
```
VITE_API_BASE_URL=https://seu-backend.railway.app
```

## Notas

- Cookies HttpOnly são enviados automaticamente (`withCredentials: true`)
- Não armazenar tokens em localStorage
- Token JWT vem via cookie seguro do backend
- Proteção contra CSRF automática (cookies)

## Problemas Comuns

### CORS Error

Certifique-se que backend tem CORS configurado para `http://localhost:3000`

### API não encontra

Verificar `VITE_API_BASE_URL` em `.env.local`

### Login não funciona

- Backend deve estar rodando em `http://localhost:8000` (ou URL configurada)
- Cookie `session` deve estar sendo setado
- Check browser DevTools → Application → Cookies

## Licença

MIT
