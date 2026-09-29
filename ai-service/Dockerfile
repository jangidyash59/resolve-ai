# FastAPI AI Service Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create faiss_store directory (index will be built on first run)
RUN mkdir -p faiss_store

# Expose port
EXPOSE 8000

# Health check (allow 5 minutes for initial index building)
HEALTHCHECK --interval=30s --timeout=15s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (index builds automatically on startup)
# Increase timeout for Render deployment
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "300"]
