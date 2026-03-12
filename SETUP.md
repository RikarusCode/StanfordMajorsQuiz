# Setup Instructions

## First Time Setup

### Step 1: Install Backend Dependencies

Open PowerShell or Command Prompt and navigate to the project folder, then:

```bash
cd api
pip install -r requirements.txt
cd ..
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Starting the Application

After setup, you can start everything with:

```bash
start.bat
```

Or:

```bash
python start.py
```

## Verify Installation

Make sure you have:
- **Python 3.8+**: Check with `python --version`
- **Node.js 18+**: Check with `node --version`
- **npm**: Comes with Node.js, check with `npm --version`

## Troubleshooting

### "Python not found"
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### "Node.js not found"
- Install Node.js from https://nodejs.org/
- This will also install npm

### "pip not found"
- Try `python -m pip` instead of just `pip`
- Or reinstall Python with PATH option checked

### "npm not found"
- Reinstall Node.js
- Restart your terminal after installation
