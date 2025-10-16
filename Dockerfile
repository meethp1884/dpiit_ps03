# PS-03 Visual Search Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libspatialindex-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY engine/ ./engine/
COPY api/ ./api/
COPY scripts/ ./scripts/
COPY configs/ ./configs/

# Create data directories
RUN mkdir -p data/training_set data/testing_set data/sample_set \
    cache outputs models/checkpoints chips

# Expose API port
EXPOSE 8000

# Default command (run API)
CMD ["python", "api/main.py"]
