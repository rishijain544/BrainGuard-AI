FROM python:3.10-slim

# Create a non-root user (required by HF Spaces)
RUN useradd -m -u 1000 user
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python packages (cached layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Download actual model files (replaces LFS pointers with real data from GitHub)
RUN python download_models.py

# Switch to non-root user
RUN chown -R user:user /app
USER user

# HF Spaces expects port 7860
EXPOSE 7860

CMD ["uvicorn", "fastapi_backend:app", "--host", "0.0.0.0", "--port", "7860"]
