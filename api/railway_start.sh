#!/bin/bash
# Railway start script - ensures we run from project root
# This script should be used if Railway's Root Directory is set to 'api/'

# Change to project root (parent of api/)
cd "$(dirname "$0")/.." || exit 1

# Run uvicorn from project root
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
