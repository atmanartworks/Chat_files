#!/bin/bash
# Startup script for Render deployment
set -e

echo "Starting FounderGPT Backend..."
echo "PORT: $PORT"
echo "Python version: $(python --version)"

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Start the server
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1
