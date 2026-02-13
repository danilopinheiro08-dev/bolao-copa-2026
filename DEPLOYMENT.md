# 🚀 Guia de Deployment - Bolão Copa 2026

## Versões Disponíveis

### 1. Docker Local (Development)
### 2. Docker Compose (Full Local Stack)
### 3. Railway (Production)
### 4. Vercel + Railway (Separado)

---

## 1️⃣ Docker Local (Apenas Backend)

```bash
# Build
docker build -t bolao:latest .

# Run
docker run -p 8000:8000 \
  -e DATABASE_PUBLIC_URL="postgresql://user:pass@host:5432/db" \
  bolao:latest

# Acesso: http://localhost:8000/docs
```

---

## 2️⃣ Docker Compose (Full Stack Local)

**Sobe tudo junto: PostgreSQL + Backend + Frontend + Nginx**

```bash
# Build e start
docker-compose up -d

# Logs
docker-compose logs -f app

# Stop
docker-compose down
```

**Acesso:**
- 🌐 Frontend: http://localhost:8080
- 📚 API Docs: http://localhost:8080/docs
- 🗄️ PgAdmin: http://localhost:5050 (admin@bolao.com / admin)

**Credenciais Teste:**
- Email: `test@bolao.com`
- Senha: `Test123456!`

---

## 3️⃣ Railway (Production Full-Stack)

### Prerequisitos
- Conta Railway (https://railway.app)
- Railway CLI instalado

### Método 1: GitHub Connection (Recomendado)

```bash
# 1. Push ao GitHub
git push origin main

# 2. Conectar Railway
railway login
railway link

# 3. Deploy automático
# Railway detectará changes e fará deploy automaticamente
```

### Método 2: Manual Deploy

```bash
# 1. Link ao projeto
railway link

# 2. Deploy
railway up

# 3. Verificar
railway open
```

### Método 3: Script Automático

```bash
./railway-deploy.sh
```

### Variáveis de Ambiente Necessárias

Railway cria automaticamente:
- `DATABASE_PUBLIC_URL` - PostgreSQL connection string
- `PORT` - Porta (8080)

Adicione se necessário:
- `VITE_API_BASE_URL=https://seu-dominio-railway.app/api`
- `ENVIRONMENT=production`

### URL da Aplicação

Após deploy:
```
https://seu-projeto-railway.app/
```

---

## 4️⃣ Vercel + Railway (Separado)

### Frontend no Vercel

```bash
cd frontend

# Build
npm run build

# Deploy (com Vercel CLI ou Git)
vercel deploy

# Configure env var
vercel env add VITE_API_BASE_URL https://seu-backend-railway.app/api
```

### Backend no Railway

```bash
railway login
railway link
railway up
```

---

## 📊 Arquitetura Docker

### Dockerfile Multi-Stage

```
Stage 1: Node.js (Build Frontend)
  ├── npm install --legacy-peer-deps
  └── npm run build → /app/frontend/dist

Stage 2: Python + Nginx + Supervisor
  ├── pip install -r requirements.txt
  ├── Copy /app (backend code)
  ├── Copy /app/frontend/dist (frontend built)
  ├── Nginx config (reverse proxy)
  ├── Supervisor config (manage services)
  └── Expose port 8080
```

### docker-compose.yml

```yaml
Services:
  - PostgreSQL (5432)
    - Volume: postgres_data
  - App (Full Stack)
    - Port 8080
    - Backend: Uvicorn @ 8000
    - Frontend: Nginx @ 8080
  - PgAdmin (opcional)
    - Port 5050
```

---

## 🔧 Configuração Nginx

**nginx.conf** proxy setup:

```nginx
# Frontend: /
location / {
    root /app/frontend/dist;
    try_files $uri $uri/ /index.html;
}

# API: /api/*
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
}

# Docs: /docs, /redoc
location /docs {
    proxy_pass http://127.0.0.1:8000/docs;
}
```

---

## 👀 Monitoramento com Supervisor

**supervisord.conf** gerencia:

```ini
[program:backend]
command=uvicorn app.main:app --host 127.0.0.1 --port 8000
autostart=true
autorestart=true

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
```

**Logs:**
```bash
docker-compose logs app

# ou dentro do container
tail -f /var/log/supervisor/backend.log
tail -f /var/log/supervisor/nginx.log
```

---

## 🐛 Troubleshooting

### Docker Build falha

```bash
# Limpar cache
docker system prune -a

# Rebuild com detalhes
docker build --no-cache -t bolao:latest .
```

### Conexão PostgreSQL falha

```bash
# Verificar variável
docker-compose config | grep DATABASE

# Usar connectionstring correta para Railway
postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/railway
```

### Frontend não carrega

1. Verificar build: `npm run build` localmente
2. Verificar nginx config
3. Testar localhost:8080 vs localhost:8080/docs

### Backend retorna 502

```bash
# Verificar se backend está rodando
docker-compose exec app ps aux

# Verificar logs
docker-compose logs app
```

---

## 📈 Performance

### Otimizações Aplicadas

✅ Multi-stage Dockerfile (reduz tamanho final)
✅ Alpine Linux (base mínima)
✅ Node.js Alpine (build rápido)
✅ Nginx como reverse proxy (static + API)
✅ Supervisor (gerenciamento de processos)
✅ Health checks (auto-restart)
✅ Gzip compression (Nginx)
✅ Cache headers (frontend assets)

### Tamanho da Imagem

```
Sem otimização: ~1.5GB
Com multi-stage: ~450MB
```

---

## 🔐 Segurança

✅ Non-root user (appuser)
✅ HTTPS ready (Railway auto-SSL)
✅ CORS configurado
✅ Rate limiting
✅ Environment vars (não hardcoded)
✅ Health checks
✅ Nginx WAF ready

---

## 📝 Comandos Úteis

```bash
# Local development
docker-compose up

# Production build
docker build -t bolao:prod -f Dockerfile .

# Test locally
docker run -p 8080:8080 bolao:latest

# Check logs
docker logs -f [container_id]

# Shell access
docker exec -it [container_id] /bin/bash

# Railway login
railway login

# Railway deployment
railway up

# Railway logs
railway logs
```

---

## ✅ Checklist de Deploy

- [ ] Código commitado no GitHub
- [ ] `.env` configurado localmente
- [ ] `npm run build` funciona (frontend)
- [ ] `docker build` funciona
- [ ] `docker-compose up` funciona
- [ ] Railway account criado
- [ ] Railway linked
- [ ] Database vars configuradas
- [ ] Frontend build testado
- [ ] API conectando ao banco
- [ ] SSL funcionando
- [ ] Health checks respondendo
- [ ] Logs OK

---

## 🎯 Next Steps

1. **Local Testing**
   ```bash
   docker-compose up
   ```

2. **Railway Deploy**
   ```bash
   railway link
   railway up
   ```

3. **Verify Production**
   - Acesse https://seu-projeto.railway.app
   - Login com test@bolao.com
   - Teste endpoints

4. **Monitor**
   - Railway dashboard
   - Logs em tempo real
   - Alertas

---

## 📞 Suporte

- GitHub Issues: https://github.com/danilopinheiro08-dev/bolao-copa-2026/issues
- Railway Docs: https://docs.railway.app
- Docker Docs: https://docs.docker.com

