#!/bin/sh
# Startup script for Railway deployment
# 1. Verify models are actual data (not LFS pointers), download if needed
# 2. Start the FastAPI server

echo "=== BrainGuard AI Startup ==="
echo "Checking model files..."
python download_models.py

echo "Starting Flask server on port 8080..."
exec gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 flask_backend:app
