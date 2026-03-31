@echo off
REM CodeArena Security Fixes - Deployment Script (Windows)
REM Run this in the project root directory

cls
echo ================================================================
echo   CodeArena Security Fixes - Deployment (Windows)
echo ================================================================
echo.

REM Step 1: Check Python version
echo [Step 1] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+ from https://www.python.org
    exit /b 1
)
python --version
echo.

REM Step 2: Create virtual environment (if needed)
if not exist "venv\" (
    if not exist ".venv\" (
        echo [Step 2] Creating virtual environment...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo    Virtual environment created and activated
    ) else (
        echo [Step 2] Virtual environment exists, activating...
        call .venv\Scripts\activate.bat
    )
) else (
    echo [Step 2] Virtual environment exists, activating...
    call venv\Scripts\activate.bat
)
echo.

REM Step 3: Upgrade pip
echo [Step 3] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo    pip upgraded
echo.

REM Step 4: Install dependencies
echo [Step 4] Installing Python dependencies...
pip install -r backend\requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo    Dependencies installed
echo.

REM Step 5: Check for .env file
echo [Step 5] Checking configuration...
if not exist ".env" (
    echo    WARNING: .env file not found!
    echo    You MUST create .env with configuration before running the app
    echo    At minimum, set: JWT_SECRET_KEY (32+ characters^)
) else (
    echo    .env file found
)
echo.

REM Step 6: Run migrations
echo [Step 6] Running database migrations...
cd backend
alembic upgrade head
if errorlevel 1 (
    echo ERROR: Migration failed
    cd ..
    exit /b 1
)
cd ..
echo    Migrations completed
echo.

REM Step 7: Show next steps
echo ================================================================
echo   DEPLOYMENT COMPLETE
echo ================================================================
echo.
echo NEXT STEPS:
echo.
echo 1. Update .env with security configuration:
echo    - JWT_SECRET_KEY=^<32+ character secret^>
echo    - DATABASE_URL=^<your-postgres-url^>
echo    - REDIS_URL=^<your-redis-url^>
echo    - SPECTATOR_REQUIRE_AUTH=true ^(default^)
echo.
echo 2. Start the application:
echo    cd backend
echo    uvicorn main:app --reload
echo.
echo 3. Test security features:
echo    - Try spectator WebSocket: should require token
echo    - Try rapid room code requests: should rate limit
echo    - Try non-admin problem creation: should return 403
echo.
echo 4. Monitor logs for security events:
echo    - [SECURITY] tags for suspicious activity
echo    - 429 responses for rate limit hits
echo    - 403 responses for authorization failures
echo.
echo See DEPLOYMENT_CHECKLIST.md for complete verification steps
echo.
pause
