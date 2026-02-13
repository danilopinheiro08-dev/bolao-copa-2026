# Bolão da Firma - Copa 2026 com IA

Uma aplicação completa de bolão da Copa do Mundo 2026 com integração de IA (Groq/Llama), rankings em tempo real e suporte a múltiplos grupos.

## Características

✅ **Autenticação:**
- Login/Cadastro com e-mail e senha
- OAuth com Google e Facebook (scaffold)
- Proteção contra brute force
- JWT tokens

✅ **Palpites:**
- Interface intuitiva para palpitar em jogos
- Travamento automático 10 minutos antes do jogo
- Sugestões de placar com IA (Groq/Llama)
- Quota de 10 sugestões por dia por usuário

✅ **Grupos/Bolões:**
- Criar grupos públicos e privados
- Códigos de acesso para grupos privados
- Rankings por grupo e ranking global
- Sistema de pontuação justo e balanceado

✅ **Pontuação:**
- 5 pts: placar exato
- 3 pts: resultado + saldo de gols
- 2 pts: apenas resultado (V/E)
- 0 pts: erro

✅ **Copa 2026:**
- Suporte a 48 seleções e 104 jogos
- Fase de grupos + mata-mata (R32, R16, QF, SF, Final, 3º lugar)
- Atualização de resultados via API ou admin manual
- Seed de fixtures inicial em JSON

✅ **Segurança (OWASP):**
- SQL Injection: ORM com SQLAlchemy
- XSS: Templates com Jinja2 escape
- CSRF: Tokens CSRF
- Rate Limiting: Por IP e por usuário
- Headers de segurança: CSP, HSTS, etc.
- Brute force protection com lockout progressivo
- Auditoria completa de ações

✅ **Observabilidade:**
- Logs estruturados
- Health checks
- Status checks
- Auditoria de ações

## Stack Tecnológico

- **Backend:** FastAPI (Python)
- **Banco:** PostgreSQL
- **Cache:** Redis (opcional)
- **IA:** Groq API (Llama 3.1)
- **Jobs:** APScheduler
- **ORM:** SQLAlchemy 2.0
- **Auth:** Argon2 + JWT
- **Frontend:** Jinja2 + HTMX + Tailwind (TBD)

## Instalação

### Pré-requisitos

- Python 3.11+
- PostgreSQL 12+
- Redis (opcional)

### Setup Local

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/bolao-copa-2026.git
cd bolao-copa-2026
```

2. **Crie virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências**
```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente**
```bash
cp .env.example .env
# Edite .env com suas configurações
```

5. **Inicialize o banco**
```bash
python -m app.cli init-db
```

6. **Importe fixtures iniciais**
```bash
python -m app.cli seed-fixtures --file fixtures_2026.json
```

7. **Crie usuário admin**
```bash
python -m app.cli create-admin
# Email: admin@bolao.com
# Nome: Admin
# Senha: (insira uma senha forte)
```

8. **Rode a aplicação**
```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`

## Documentação da API

Acesse `http://localhost:8000/docs` para visualizar a documentação interativa.

### Endpoints Principais

**Autenticação:**
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/password-reset` - Solicitar reset de senha

**Jogos:**
- `GET /api/matches` - Listar jogos
- `GET /api/matches/{match_id}` - Detalhes do jogo
- `GET /api/my/upcoming` - Próximos jogos sem palpite

**Palpites:**
- `POST /api/predictions` - Criar palpite
- `PUT /api/predictions/{prediction_id}` - Atualizar palpite
- `GET /api/my/predictions` - Meus palpites

**Grupos:**
- `POST /api/groups` - Criar grupo
- `GET /api/groups` - Meus grupos
- `GET /api/groups/{group_id}` - Detalhes do grupo
- `POST /api/groups/{group_id}/join` - Entrar em grupo
- `GET /api/groups/{group_id}/standings` - Ranking do grupo

**IA:**
- `GET /api/ai/suggest/{match_id}` - Sugestão de placar com IA

**Rankings:**
- `GET /api/users/rankings/global` - Ranking global

**Admin:**
- `PUT /api/admin/matches/{match_id}` - Atualizar resultado manualmente
- `POST /api/admin/fixtures/import-json` - Importar fixtures
- `POST /api/admin/fixtures/update-results` - Atualizar resultados da API
- `POST /api/admin/recalculate-rankings` - Recalcular rankings

## Configuração

### Variáveis Importantes

```env
# Banco
DATABASE_URL=postgresql://user:password@localhost:5432/bolao_copa_2026

# Groq AI
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-70b-versatile

# Sports API
SPORTS_API_PROVIDER=manual  # ou api-football
SPORTS_API_KEY=your-key

# Segurança
SECRET_KEY=change-this-to-random-string
BRUTE_FORCE_LOCKOUT_THRESHOLD=5
BRUTE_FORCE_LOCKOUT_MINUTES=15

# Jobs
ENABLE_JOBS=True
UPDATE_MATCHES_INTERVAL_SECONDS=300  # 5 min
RECALC_RANKINGS_INTERVAL_SECONDS=3600  # 1 hora
```

## CLI Útil

```bash
# Inicializar banco
python -m app.cli init-db

# Criar admin
python -m app.cli create-admin

# Importar fixtures
python -m app.cli seed-fixtures --file fixtures_2026.json

# Listar usuários
python -m app.cli list-users

# Listar jogos
python -m app.cli list-fixtures

# Verificar fixtures
python -m app.cli check-fixtures

# Verificar conexão DB
python -m app.cli check-db
```

## Estrutura do Projeto

```
bolao-copa-2026/
├── app/
│   ├── main.py              # Aplicação FastAPI
│   ├── config.py            # Configurações
│   ├── db.py                # Setup do banco
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── cli.py               # CLI
│   ├── security/
│   │   ├── crypto.py        # Criptografia, JWT
│   │   └── middleware.py    # Security middleware
│   ├── services/
│   │   ├── business.py      # Lógica de negócio
│   │   ├── ranking.py       # Cálculo de rankings
│   │   └── ai.py            # Integração Groq
│   ├── routes/
│   │   ├── auth.py          # Autenticação
│   │   ├── predictions.py   # Palpites
│   │   ├── groups.py        # Grupos
│   │   ├── users.py         # Usuários
│   │   ├── admin.py         # Admin
│   │   └── ai.py            # IA
│   ├── providers/
│   │   └── data.py          # Provedores de dados
│   ├── jobs/
│   │   └── scheduler.py     # Jobs agendados
│   └── templates/           # HTML (TBD)
├── migrations/              # Alembic migrations
├── fixtures_2026.json       # Seed de fixtures
├── requirements.txt         # Dependências
├── .env.example             # Variáveis exemplo
├── Dockerfile               # Containerização
└── README.md               # Este arquivo
```

## Deploy

### Docker

```bash
# Build
docker build -t bolao-copa-2026 .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e GROQ_API_KEY=... \
  bolao-copa-2026
```

### Railway/Heroku

1. Configure variáveis de ambiente
2. Rode migrations: `python -m app.cli init-db`
3. Deploy

## Segurança

### Implementações

- ✅ SQL Injection: ORM com parameterização
- ✅ XSS: Templates com escape automático
- ✅ CSRF: Tokens CSRF em forms
- ✅ Rate Limiting: Limiter por IP e por usuário
- ✅ Brute Force: Lockout progressivo após N tentativas
- ✅ Password: Argon2 hashing
- ✅ Sessions: JWT com expiração
- ✅ Headers: CSP, HSTS, X-Frame-Options, etc.
- ✅ Auditoria: Logs de todas as ações
- ✅ CORS: Whitelist de origins

### Headers de Segurança

Todos os endpoints retornam:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: ...`

## Roadmap

- [ ] Templates HTML (Jinja2 + HTMX + Tailwind)
- [ ] Integração OAuth completa (Google, Facebook)
- [ ] Email verification
- [ ] Notificações em tempo real (WebSocket)
- [ ] Dashboard Admin completo
- [ ] Estatísticas avançadas
- [ ] Monetização (Stripe)
- [ ] Marketplace de prêmios
- [ ] App mobile (React Native)

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

MIT License - veja LICENSE.md

## Suporte

- 📧 Email: suporte@bolao.com
- 🐛 Issues: https://github.com/seu-usuario/bolao-copa-2026/issues
- 💬 Discussões: https://github.com/seu-usuario/bolao-copa-2026/discussions

## Changelog

### v1.0.0 (2026-02-13)
- ✅ Versão inicial
- ✅ Autenticação com e-mail/senha
- ✅ Sistema de palpites com travamento
- ✅ Sugestões de IA
- ✅ Grupos e rankings
- ✅ Segurança OWASP completa
- ✅ API REST com 30+ endpoints
- ✅ CLI administrativo

---

**Desenvolvido com ❤️ para a Copa 2026**
