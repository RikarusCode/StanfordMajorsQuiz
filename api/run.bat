@echo off
REM Run the FastAPI server on Windows
REM IMPORTANT: run from project root so `api` package is importable

cd /d %~dp0..
set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
)

%PYTHON_EXE% -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
