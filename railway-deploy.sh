#!/bin/bash

# Bolão Copa 2026 - Railway Deployment Script

set -e

echo "🚀 Iniciando deployment no Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI não está instalado"
    echo "📖 Instale com: npm i -g @railway/cli"
    exit 1
fi

# Link to Railway project
echo "🔗 Conectando ao projeto Railway..."
railway link

# Set environment variables if needed
echo "🔐 Configurando variáveis de ambiente..."
railway variables set VITE_API_BASE_URL="https://\$(railway whoami --json | jq -r '.domain')/api" 2>/dev/null || true

# Deploy
echo "📦 Fazendo deploy..."
railway up

echo "✅ Deploy concluído com sucesso!"
echo ""
echo "🌐 Sua aplicação estará disponível em:"
railway open --service=web

exit 0
