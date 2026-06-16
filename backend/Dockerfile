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

# Download actual model files (replaces LFS pointers with real data)
RUN python download_models.py

# HF Spaces uses port 7860 by default
ENV PORT=7860
EXPOSE 7860

# Start the FastAPI server
CMD ["sh", "-c", "python download_models.py && uvicorn fastapi_backend:app --host 0.0.0.0 --port 7860"]
