FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (libgl1 for OpenCV, libglib for cv2)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python packages (cached layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Make startup script executable
RUN chmod +x start.sh

# Download actual model files (replaces LFS pointers with real data)
# This runs at BUILD TIME so models are baked into the image
RUN python download_models.py

# Set environment variables
ENV RAILWAY_ENVIRONMENT=production
ENV PORT=8080
EXPOSE 8080

# Use startup script which verifies models then starts uvicorn
CMD ["sh", "start.sh"]
