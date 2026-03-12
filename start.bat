@echo off
REM Start both FastAPI backend and Next.js frontend

echo ========================================
echo Starting Stanford Major Quiz
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js.
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI backend...
REM IMPORTANT: Run from project root so `api` package is importable
start "FastAPI Backend" cmd /k "python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo [2/2] Starting Next.js frontend...
start "Next.js Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both services are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this window (services will keep running)...
pause >nul
