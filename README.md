# Stanford Major Quiz

An adaptive "Which Stanford major should I choose?" quiz using Bayesian inference and information theory. Features both a modern Next.js frontend with FastAPI backend and an original Streamlit app.

## 🚀 Quick Start

**Start everything at once:**
- **Windows**: Run `start.bat`
- **Linux/Mac**: Run `python start.py` or `./start.sh`
- **Manual**: See [README_START.md](README_START.md) for detailed instructions

This will start:
- FastAPI backend on http://localhost:8000
- Next.js frontend on http://localhost:3000

## Project Structure

- `api/` — FastAPI backend with REST endpoints
- `frontend/` — Next.js frontend with React/TypeScript
- `app.py` — Original Streamlit application (still works!)
- `src/` — Core inference logic (shared by all apps)
  - `inference.py` — Bayesian inference utilities
  - `model.py` — Data models and loading
- `data/` — JSON data files
  - `majors.json` — Major feature vectors
  - `questions.json` — Question bank with feature weights

## Setup

### First Time Setup

1. **Backend dependencies:**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Original Streamlit app (optional):**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Running

### Option 1: Use Start Scripts (Recommended)
- Windows: `start.bat`
- Cross-platform: `python start.py`
- Linux/Mac: `./start.sh`

### Option 2: Manual Start
See [README_START.md](README_START.md) for step-by-step instructions.

### Option 3: Streamlit App Only
```bash
streamlit run app.py
```

## Features

- **Adaptive Question Selection** - Uses information theory to select optimal questions
- **Bayesian Inference** - Updates probabilities using Bayes' Rule
- **Real-time Updates** - See top majors update as you answer
- **Modern UI** - Glassmorphism design with smooth animations
- **Educational** - Learn about entropy, information gain, and Bayesian inference

## Documentation

- [Quick Start Guide](README_START.md) - How to start everything
- [API Documentation](api/README.md) - FastAPI backend docs
- [Frontend README](frontend/README.md) - Next.js frontend docs
- [Project Status](PROJECT_STATUS.md) - Complete project overview
