#!/bin/bash
# CodeArena Security Fixes - Quick Deployment for Azure Linux
# Run these commands in your project directory

echo "=================================================="
echo "  CodeArena Security Fixes - Azure Linux Deploy"
echo "=================================================="
echo ""

# Step 1: Ensure you're in the project directory
pwd
echo ""

# Step 2: Check if virtual environment exists, create if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Step 3: Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 4: Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r backend/requirements.txt > /dev/null
echo "✓ Dependencies installed"
echo ""

# Step 5: Run database migrations
echo "Running database migrations..."
cd backend
alembic upgrade head
cd ..
echo "✓ Migrations complete"
echo ""

# Step 6: Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  IMPORTANT: Create .env file with:"
    echo "   JWT_SECRET_KEY=<your-32-char-secret>"
    echo "   DATABASE_URL=<your-postgres-url>"
    echo "   REDIS_URL=<your-redis-url>"
    echo "   SPECTATOR_REQUIRE_AUTH=true"
else
    echo "✓ .env file exists"
fi
echo ""

echo "=================================================="
echo "  ✅ DEPLOYMENT READY"
echo "=================================================="
echo ""
echo "Start the API:"
echo "  cd backend && uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
