#!/bin/bash
# 🔍 Docker Deployment Validation Script

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Bolão Copa 2026 - Docker Deployment Validator            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1 exists"
        ((PASSED++))
        return 0
    else
        echo "❌ $1 NOT FOUND"
        ((FAILED++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/ exists"
        ((PASSED++))
        return 0
    else
        echo "❌ $1/ NOT FOUND"
        ((FAILED++))
        return 1
    fi
}

echo "📋 CHECKING FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file "nginx.conf"
check_file "supervisord.conf"
check_file ".dockerignore"
check_file "railway.json"
check_file "requirements.txt"
check_file "DEPLOYMENT.md"
check_file "DOCKER_DEPLOYMENT_SUMMARY.md"
check_file "QUICK_COMMANDS.sh"
echo ""

echo "📁 CHECKING DIRECTORIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "app"
check_dir "frontend"
echo ""

echo "🔧 CHECKING KEY FILES IN SUBDIRECTORIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file "frontend/package.json"
check_file "frontend/vite.config.ts"
check_file "app/main.py"
echo ""

echo "📝 CHECKING FILE SYNTAX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Dockerfile structure
if grep -q "FROM node:20-alpine as frontend-builder" Dockerfile && \
   grep -q "FROM python:3.11-slim" Dockerfile && \
   grep -q "COPY --from=frontend-builder" Dockerfile; then
    echo "✅ Dockerfile has multi-stage build"
    ((PASSED++))
else
    echo "❌ Dockerfile missing multi-stage build"
    ((FAILED++))
fi

# Check docker-compose services
if grep -q "postgres:" docker-compose.yml && \
   grep -q "image: postgres:15-alpine" docker-compose.yml; then
    echo "✅ docker-compose.yml has PostgreSQL service"
    ((PASSED++))
else
    echo "❌ docker-compose.yml missing PostgreSQL"
    ((FAILED++))
fi

if grep -q "app:" docker-compose.yml && \
   grep -q "build: ." docker-compose.yml; then
    echo "✅ docker-compose.yml has app service"
    ((PASSED++))
else
    echo "❌ docker-compose.yml missing app service"
    ((FAILED++))
fi

# Check nginx config
if grep -q "upstream backend" nginx.conf && \
   grep -q "listen 8080" nginx.conf && \
   grep -q "try_files.*index.html" nginx.conf; then
    echo "✅ nginx.conf is properly configured"
    ((PASSED++))
else
    echo "❌ nginx.conf is incomplete"
    ((FAILED++))
fi

# Check supervisord
if grep -q "\[program:backend\]" supervisord.conf && \
   grep -q "uvicorn app.main:app" supervisord.conf && \
   grep -q "\[program:nginx\]" supervisord.conf; then
    echo "✅ supervisord.conf manages both services"
    ((PASSED++))
else
    echo "❌ supervisord.conf is incomplete"
    ((FAILED++))
fi

# Check railway.json
if grep -q "projectName" railway.json && \
   grep -q "postgresql" railway.json && \
   grep -q "Dockerfile" railway.json; then
    echo "✅ railway.json is properly configured"
    ((PASSED++))
else
    echo "❌ railway.json is incomplete"
    ((FAILED++))
fi

echo ""

echo "🔐 CHECKING ENVIRONMENT SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check docker-compose env setup
if grep -q "DATABASE_PUBLIC_URL" docker-compose.yml && \
   grep -q "VITE_API_BASE_URL" docker-compose.yml; then
    echo "✅ Environment variables configured in docker-compose"
    ((PASSED++))
else
    echo "❌ Environment variables missing in docker-compose"
    ((FAILED++))
fi

# Check .dockerignore
if grep -q "node_modules" .dockerignore && \
   grep -q "__pycache__" .dockerignore && \
   grep -q ".git" .dockerignore; then
    echo "✅ .dockerignore excludes build artifacts"
    ((PASSED++))
else
    echo "❌ .dockerignore is incomplete"
    ((FAILED++))
fi

echo ""

echo "📦 CHECKING DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python requirements
if grep -q "fastapi" requirements.txt && \
   grep -q "uvicorn" requirements.txt && \
   grep -q "psycopg2-binary" requirements.txt; then
    echo "✅ requirements.txt has core dependencies"
    ((PASSED++))
else
    echo "❌ requirements.txt missing core dependencies"
    ((FAILED++))
fi

# Check package.json dependencies
if grep -q "react" frontend/package.json && \
   grep -q "axios" frontend/package.json && \
   grep -q "vite" frontend/package.json; then
    echo "✅ frontend/package.json has core dependencies"
    ((PASSED++))
else
    echo "❌ frontend/package.json missing core dependencies"
    ((FAILED++))
fi

echo ""

echo "🏗️ CHECKING BUILD STRATEGY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check frontend build in Dockerfile
if grep -q "npm run build" Dockerfile; then
    echo "✅ Frontend build step included"
    ((PASSED++))
else
    echo "❌ Frontend build missing"
    ((FAILED++))
fi

# Check dist copy
if grep -q "COPY --from=frontend-builder /app/frontend/dist" Dockerfile; then
    echo "✅ Frontend dist copy configured"
    ((PASSED++))
else
    echo "❌ Frontend dist copy missing"
    ((FAILED++))
fi

# Check static file serving
if grep -q "root /app/frontend/dist" nginx.conf; then
    echo "✅ Static file serving configured"
    ((PASSED++))
else
    echo "❌ Static file serving missing"
    ((FAILED++))
fi

echo ""

echo "🔌 CHECKING PORTS & NETWORKING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check nginx port
if grep -q "listen 8080" nginx.conf; then
    echo "✅ Nginx configured for port 8080"
    ((PASSED++))
else
    echo "❌ Nginx port not configured"
    ((FAILED++))
fi

# Check backend port
if grep -q "127.0.0.1:8000" nginx.conf; then
    echo "✅ Backend proxy configured for port 8000"
    ((PASSED++))
else
    echo "❌ Backend proxy not configured"
    ((FAILED++))
fi

# Check postgres port in compose
if grep -q "5432:5432" docker-compose.yml; then
    echo "✅ PostgreSQL port exposed"
    ((PASSED++))
else
    echo "❌ PostgreSQL port not exposed"
    ((FAILED++))
fi

echo ""

echo "📊 FINAL REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "✅ Passed:  $PASSED/$TOTAL"
echo "❌ Failed:  $FAILED/$TOTAL"
echo "📈 Score:   $PERCENTAGE%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED - DEPLOYMENT READY!"
    echo ""
    echo "Next steps:"
    echo "1. Review DEPLOYMENT.md for detailed instructions"
    echo "2. Test locally: docker-compose up"
    echo "3. Deploy to Railway: railway login && railway up"
    exit 0
else
    echo "⚠️  SOME CHECKS FAILED - REVIEW ABOVE"
    exit 1
fi
