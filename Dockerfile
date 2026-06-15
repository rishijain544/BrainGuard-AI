# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for some Python packages like OpenCV headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY backend/requirements.txt ./backend/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend code
COPY backend/ ./backend/

# Expose the port Railway provides via $PORT
EXPOSE $PORT

# Run the FastAPI server via Uvicorn
CMD ["sh", "-c", "uvicorn backend.fastapi_backend:app --host 0.0.0.0 --port ${PORT:-8000}"]
