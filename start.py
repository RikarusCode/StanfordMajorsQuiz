#!/usr/bin/env python3
"""
Start both FastAPI backend and Next.js frontend in one go.
Works on Windows, Linux, and Mac.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# Store process IDs for cleanup
processes = []


def cleanup():
    """Stop all running processes."""
    print("\nShutting down services...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            try:
                proc.kill()
            except:
                pass
    sys.exit(0)


def signal_handler(sig, frame):
    """Handle Ctrl+C."""
    cleanup()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Check if we're in the project root
project_root = Path(__file__).parent
os.chdir(project_root)

print("=" * 60)
print("Starting Stanford Major Quiz")
print("=" * 60)
print()

# Check Python
try:
    subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
except:
    print("ERROR: Python not found")
    sys.exit(1)

# Check Node.js
try:
    subprocess.run(["node", "--version"], check=True, capture_output=True)
except:
    print("ERROR: Node.js not found. Please install Node.js.")
    sys.exit(1)

# Start backend
print("[1/2] Starting FastAPI backend...")
backend_cmd = [
    sys.executable,
    "-m",
    "uvicorn",
    "api.main:app",
    "--reload",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
]

# IMPORTANT: run from project root so `api` package is importable
backend_proc = subprocess.Popen(
    backend_cmd,
    cwd=project_root,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
processes.append(backend_proc)

# Wait for backend to start
time.sleep(3)

# Start frontend
print("[2/2] Starting Next.js frontend...")
frontend_cmd = ["npm", "run", "dev"]

frontend_proc = subprocess.Popen(
    frontend_cmd,
    cwd=project_root / "frontend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
processes.append(frontend_proc)

print()
print("=" * 60)
print("Both services are running!")
print("=" * 60)
print()
print("Backend:  http://localhost:8000")
print("Frontend: http://localhost:3000")
print("API Docs: http://localhost:8000/docs")
print()
print("Press Ctrl+C to stop both services")
print()

# Wait for processes (with output streaming)
try:
    # Stream output from both processes
    import threading

    def stream_output(proc, name):
        for line in proc.stdout:
            print(f"[{name}] {line.decode().rstrip()}")
        for line in proc.stderr:
            print(f"[{name}] {line.decode().rstrip()}", file=sys.stderr)

    backend_thread = threading.Thread(
        target=stream_output, args=(backend_proc, "Backend"), daemon=True
    )
    frontend_thread = threading.Thread(
        target=stream_output, args=(frontend_proc, "Frontend"), daemon=True
    )
    backend_thread.start()
    frontend_thread.start()

    # Wait for processes
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    cleanup()
