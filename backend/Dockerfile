FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Set environment variables
ENV RAILWAY_ENVIRONMENT=production

EXPOSE $PORT

# Start command
CMD ["sh", "-c", "uvicorn fastapi_backend:app --host 0.0.0.0 --port ${PORT:-8000}"]
