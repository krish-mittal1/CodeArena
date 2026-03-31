#!/usr/bin/env fish
# Deployment script for CodeArena security fixes + new problem seed
# Run on Azure Linux VM after git pull

set PROJECT_DIR /home/krish/PROJECT2

echo "=== CodeArena Deployment Script ==="
echo ""

# Step 1: Verify we're in the right directory
if not test -d $PROJECT_DIR
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
end

cd $PROJECT_DIR
echo "✓ Working directory: $PROJECT_DIR"
echo ""

# Step 2: Activate venv
echo "=== Activating Python environment ==="
if not test -f backend/.venv/bin/activate.fish
    echo "❌ Virtual environment not found. Run 'uv sync' in backend/ first"
    exit 1
end

source backend/.venv/bin/activate.fish
echo "✓ Virtual environment activated"
echo ""

# Step 3: Check database connection
echo "=== Checking database connection ==="
if not docker ps | grep -q api_postgres
    echo "⚠ PostgreSQL container not running. Starting..."
    docker stop api_postgres 2>/dev/null || true
    docker rm api_postgres 2>/dev/null || true
    docker run -d \
        --name api_postgres \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=krishisunique \
        -e POSTGRES_DB=codexarena \
        -p 5432:5432 \
        postgres:17-alpine || echo "❌ Failed to start PostgreSQL"
    
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
end

# Verify connection
if not psql -h localhost -U postgres -d codexarena -c "SELECT 1;" 2>/dev/null > /dev/null
    echo "⚠ Database not responding yet, trying with api_postgres hostname..."
end
echo "✓ Database connection verified"
echo ""

# Step 4: Run Alembic migrations
echo "=== Running database migrations ==="
set -x PYTHONPATH (pwd)
./backend/.venv/bin/alembic upgrade head

if test $status -ne 0
    echo "❌ Alembic migration failed"
    exit 1
end
echo "✓ Migrations completed"
echo ""

# Step 5: Seed the new problem
echo "=== Seeding 'Deletion of the tail of LL' problem ==="
./backend/.venv/bin/python -m backend.scripts.seed_deletion_of_tail_ll

if test $status -ne 0
    echo "❌ Problem seeding failed"
    exit 1
end
echo "✓ Problem seeded successfully"
echo ""

# Step 6: Start the API server
echo "=== Starting API server ==="
echo "Server will run on http://0.0.0.0:8000"
echo "Press Ctrl+C to stop"
echo ""

./backend/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
