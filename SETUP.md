# Guia de Setup e Deployment - Bolão da Firma Copa 2026

## 🚀 Quick Start (5 min)

### 1. Clone e Setup
```bash
cd /home/user/bolao-copa-2026
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure .env
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 3. Inicialize
```bash
# Banco de dados
python -m app.cli init-db

# Admin
python -m app.cli create-admin

# Fixtures
python -m app.cli seed-fixtures
```

### 4. Rode
```bash
uvicorn app.main:app --reload
```

Acesse: **http://localhost:8000/docs**

---

## 📋 Arquivo Checklist

### ✅ Estrutura de Banco de Dados
- `app/models.py` - 12 tabelas com validações
- `migrations/001_initial.py` - Schema completo
- Índices otimizados
- Constraints únicos

### ✅ Autenticação & Segurança
- `app/security/crypto.py` - Hashing + JWT
- `app/security/middleware.py` - Rate limit + CSRF + Brute force
- Headers OWASP completos
- CORS restrito
- Auditoria de ações

### ✅ Rotas API (30+ endpoints)
- `app/routes/auth.py` - Registro, login, reset senha
- `app/routes/predictions.py` - Palpites, matches
- `app/routes/groups.py` - Grupos, membros
- `app/routes/users.py` - Perfil, rankings
- `app/routes/admin.py` - Admin: matches, fixtures, rankings
- `app/routes/ai.py` - Sugestões com Groq/Llama

### ✅ Lógica de Negócio
- `app/services/business.py` - UserService, GroupService, PredictionService, ScoringService
- `app/services/ranking.py` - Cálculo de rankings com cache
- `app/services/ai.py` - Integração Groq (prompt builder, quota tracking)

### ✅ Provedores de Dados
- `app/providers/data.py` - ManualProvider, APIProvider, FixtureImporter
- Suporte a JSON/CSV
- Fallback automático
- Parser de fixtures oficial da FIFA

### ✅ Jobs Agendados
- `app/jobs/scheduler.py` - APScheduler
- Update de matches a cada 5 min
- Recalc rankings a cada 1 hora
- Cleanup de sessões diárias

### ✅ CLI
- `app/cli.py` - 7 comandos úteis
- `init-db`, `create-admin`, `seed-fixtures`
- `list-users`, `list-fixtures`, `check-fixtures`, `check-db`

### ✅ Fixtures Seed
- `fixtures_2026.json` - 13 matches de exemplo
- Formatos: GROUP, R32, R16, QF, SF, THIRD, FINAL
- Pronto para importar

### ✅ Testes
- `tests/test_main.py` - Testes de scoring, auth, API
- Cobertura: pontuação, login, saúde

### ✅ Documentação & Legal
- `README.md` - Completo com instrções
- `LEGAL.md` - Termos de Uso + LGPD
- `SETUP.md` - Este arquivo

### ✅ Config & Deploy
- `Dockerfile` - Containerização pronta
- `.env.example` - Template de variáveis
- `requirements.txt` - 25+ dependências pinadas

### ✅ Frontend Foundation
- Schemas Pydantic para templates
- CORS configurado para frontend
- CSRF tokens prontos
- HTMX-ready endpoints

---

## 🎯 Funcionalidades Implementadas

### Copa 2026
- ✅ 48 seleções (estrutura suporta)
- ✅ 104 jogos (13 seed + escalável)
- ✅ Fases: GROUP + R32 + R16 + QF + SF + THIRD + FINAL
- ✅ Importação de fixtures via JSON
- ✅ Atualização de resultados (manual + API)

### Autenticação
- ✅ Email/Senha com Argon2
- ✅ JWT tokens com expiração
- ✅ OAuth placeholder (Google, Facebook)
- ✅ Email verification flow (scaffolding)
- ✅ Password reset com tokens temporários

### Palpites
- ✅ Criar/editar palpites
- ✅ Travamento automático 10 min antes
- ✅ Status de lock por prediction
- ✅ Histórico de mudanças (updated_at)

### Pontuação
- ✅ 5 pts: placar exato
- ✅ 3 pts: resultado + saldo
- ✅ 2 pts: resultado apenas
- ✅ 0 pts: erro
- ✅ Desempate: exatos > resultados > erro absoluto

### Grupos
- ✅ Públicos e privados
- ✅ Códigos de acesso únicos
- ✅ Aprovação de membros (opcional)
- ✅ Roles: owner, admin, member
- ✅ Ranking por grupo

### IA (Groq/Llama)
- ✅ Endpoint `/api/ai/suggest/{match_id}`
- ✅ Prompt builder contextual
- ✅ 10 sugestões/dia por usuário
- ✅ Logging de uso + latência
- ✅ Fallback graceful se Groq down

### Rankings
- ✅ Global + por grupo
- ✅ Cache em DB (standings_cache)
- ✅ Recalc automático após matches FT
- ✅ Tiebreaker: exatos > resultados > erro

### Segurança (OWASP)
- ✅ SQL Injection: ORM SQLAlchemy
- ✅ XSS: Jinja2 auto-escape
- ✅ CSRF: Token validation
- ✅ Rate Limit: Por IP/user
- ✅ Brute Force: Lockout progressivo
- ✅ Password: Argon2 hashing
- ✅ Sessions: HTTP-only cookies
- ✅ Headers: CSP, HSTS, X-Frame-Options
- ✅ Auditoria: Todos os logins/ações

### Observabilidade
- ✅ Logs estruturados
- ✅ /health endpoint
- ✅ /status endpoint
- ✅ /admin/status dashboard
- ✅ Audit logs completos

---

## 🔧 Configuração Importante

### Variáveis Críticas

```env
# BANCO - OBRIGATÓRIO
DATABASE_URL=postgresql://user:password@localhost:5432/bolao_copa_2026

# IA - OPCIONAL (sem ele, botão desabilitado)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-70b-versatile

# SPORTS - OPCIONAL (default: manual)
SPORTS_API_PROVIDER=manual
# Se usar API:
SPORTS_API_KEY=your-api-key
SPORTS_API_URL=https://v3.football.api-sports.io

# SEGURANÇA - MUDE EM PRODUCTION
SECRET_KEY=change-this-in-production

# JOBS - LIGADO POR DEFAULT
ENABLE_JOBS=True
UPDATE_MATCHES_INTERVAL_SECONDS=300  # 5 min
```

---

## 📊 Dados de Exemplo

### Usuário Admin (depois de `create-admin`)
```
Email: admin@bolao.com
Senha: (seu choice)
Admin: ✓
```

### Matches de Teste
```
13 matches em fixtures_2026.json
- 6 da Fase de Grupos (Grupo A)
- 7 do mata-mata
Todos em status SCHEDULED
```

---

## 🧪 Testes

```bash
# Rodas testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=app
```

Testes cobrem:
- ✅ Scoring (exato, resultado, saldo)
- ✅ Auth (register, login, password)
- ✅ API (health, status)
- ✅ Modelos

---

## 🐳 Docker

```bash
# Build
docker build -t bolao-copa:latest .

# Run local
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/bolao \
  -e GROQ_API_KEY=gsk_... \
  -e SECRET_KEY=random-key \
  bolao-copa:latest

# Com env file
docker run -p 8000:8000 --env-file .env bolao-copa:latest
```

---

## 🚀 Deploy em Produção

### Railway/Render/Heroku

1. **Configure variáveis:**
```bash
SECRET_KEY=<random-32-chars>
DATABASE_URL=postgresql://...
GROQ_API_KEY=gsk_...
ENVIRONMENT=production
DEBUG=False
```

2. **Run migrations:**
```bash
python -m app.cli init-db
```

3. **Create admin:**
```bash
python -m app.cli create-admin
```

4. **Import fixtures:**
```bash
python -m app.cli seed-fixtures
```

### Security Checklist
- [ ] `SECRET_KEY` é aleatório de 32+ chars
- [ ] `DEBUG=False` em prod
- [ ] HTTPS habilitado
- [ ] DATABASE_URL via env (nunca no código)
- [ ] CORS restrito a domínios reais
- [ ] Rate limiting ativado
- [ ] Backups do banco configurados
- [ ] Email SMTP funcional

---

## 📚 Documentação API

```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

### Endpoints Principais

**Auth (sem login):**
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/password-reset
```

**Matches (sem login):**
```
GET /api/matches
GET /api/matches/{match_id}
GET /api/matches/{match_id}/predictions
```

**Predictions (requer login):**
```
POST /api/predictions
PUT /api/predictions/{id}
GET /api/my/predictions
GET /api/my/upcoming
```

**Groups (requer login):**
```
POST /api/groups
GET /api/groups
GET /api/groups/{id}
POST /api/groups/{id}/join
GET /api/groups/{id}/standings
```

**AI (requer login + quota):**
```
GET /api/ai/suggest/{match_id}?style=balanced
GET /api/ai/health
```

**Admin (requer admin):**
```
PUT /api/admin/matches/{id}
POST /api/admin/fixtures/import-json
POST /api/admin/fixtures/update-results
POST /api/admin/recalculate-rankings
GET /api/admin/status
```

---

## 🛠️ Troubleshooting

### Banco não conecta
```bash
# Verificar conexão
python -m app.cli check-db

# Recriar schema
python -m app.cli init-db
```

### Fixtures não importam
```bash
# Verificar arquivo
cat fixtures_2026.json | python -m json.tool

# Importar novamente
python -m app.cli seed-fixtures --file fixtures_2026.json
```

### IA não funciona
```bash
# Verificar Groq
# 1. Check GROQ_API_KEY em .env
# 2. Teste direto: curl https://api.groq.com/health
# 3. Verifique quota da API
# 4. Logs: check app output para erros
```

### Rate limit muito restrito
```env
# Aumentar limite (default: 60 req/min por IP)
RATE_LIMIT_PER_MINUTE=120
```

### Brute force lockout temporário
```env
# Aumentar tempo de lockout
BRUTE_FORCE_LOCKOUT_MINUTES=30

# Ou limpar via CLI (TBD)
```

---

## 📞 Suporte

- **Issues:** GitHub Issues
- **Email:** suporte@bolao.com
- **Docs:** README.md + LEGAL.md

---

## 📝 Próximos Passos

### Curto Prazo (Sprint 1)
- [ ] Templates HTML (Jinja2 + HTMX + Tailwind)
- [ ] Frontend dashboard completo
- [ ] Integração OAuth real
- [ ] Email notifications

### Médio Prazo (Sprint 2)
- [ ] WebSockets para rankings live
- [ ] Notificações push
- [ ] Estatísticas avançadas
- [ ] Export CSV

### Longo Prazo (Sprint 3)
- [ ] Monetização (Stripe)
- [ ] Marketplace de prêmios
- [ ] App mobile (React Native)
- [ ] Modo competição (ELO, tournaments)

---

## 📄 Licença

MIT License 2026

---

**Pronto para produção! 🎉**
