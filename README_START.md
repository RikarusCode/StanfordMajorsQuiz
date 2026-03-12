# Quick Start Guide

## 🚀 Start Everything at Once

You have several options to start both the backend and frontend together:

### Option 1: Windows Batch File (Easiest for Windows)
```bash
start.bat
```
This opens two separate windows - one for the backend and one for the frontend.

### Option 2: Python Script (Cross-platform)
```bash
python start.py
```
Works on Windows, Linux, and Mac. Shows output from both services in one terminal.

### Option 3: Shell Script (Linux/Mac)
```bash
chmod +x start.sh
./start.sh
```
Runs both services in the background. Press Ctrl+C to stop both.

### Option 4: Manual Start (If scripts don't work)

**Terminal 1 - Backend:**
```bash
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📍 URLs

Once started:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ⚠️ Prerequisites

Make sure you have:
- **Python 3.8+** installed
- **Node.js 18+** installed
- **npm** (comes with Node.js)

## 🔧 First Time Setup

If this is your first time running the project:

1. **Install backend dependencies:**
   ```bash
   cd api
   pip install -r requirements.txt
   cd ..
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Then use any of the start options above**

## 🛑 Stopping Services

- **Windows Batch File**: Close the two windows that opened
- **Python Script**: Press `Ctrl+C` in the terminal
- **Shell Script**: Press `Ctrl+C` in the terminal
- **Manual**: Press `Ctrl+C` in each terminal
