#!/bin/sh
# Startup script for Railway deployment
# 1. Verify models are actual data (not LFS pointers), download if needed
# 2. Start the FastAPI server

echo "=== BrainGuard AI Startup ==="
echo "Checking model files..."
python download_models.py

echo "Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn fastapi_backend:app --host "::" --port ${PORT:-8000}
