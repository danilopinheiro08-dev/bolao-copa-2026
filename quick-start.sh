#!/bin/bash
# quick-start.sh - Bolão da Firma Copa 2026

set -e

echo "🚀 Bolão da Firma Copa 2026 - Quick Start"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create venv
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment created"
echo ""

# Install deps
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Setup env
echo "🔧 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env (edit with your keys)"
else
    echo "✓ .env already exists"
fi
echo ""

# Update .env for local dev if needed
echo "📝 Updating .env for local development..."
# Minimal postgres for local test
sed -i 's|postgresql://.*@localhost.*|postgresql://postgres:password@localhost:5432/bolao_copa_2026|g' .env || true
echo "✓ .env updated for local dev"
echo ""

# Check if we can use SQLite for testing
echo "💾 Initializing database..."
# For local testing without Postgres, we can use SQLite
# But let's assume Postgres for production-like setup

echo ""
echo "⚠️  You need PostgreSQL running locally:"
echo "    Mac: brew install postgresql && brew services start postgresql"
echo "    Linux: sudo apt-get install postgresql && sudo service postgresql start"
echo "    Windows: Download from https://www.postgresql.org/download/windows/"
echo ""
echo "After PostgreSQL is running:"
echo ""

echo "🔨 Next steps:"
echo "  1. Ensure PostgreSQL is running"
echo "  2. Update DATABASE_URL in .env if needed"
echo "  3. Run: python -m app.cli init-db"
echo "  4. Run: python -m app.cli create-admin"
echo "  5. Run: python -m app.cli seed-fixtures"
echo "  6. Run: uvicorn app.main:app --reload"
echo ""
echo "✅ Then visit: http://localhost:8000/docs"
echo ""
