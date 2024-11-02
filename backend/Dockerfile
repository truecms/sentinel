FROM python:3.11-slim as builder

WORKDIR /install

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and alembic
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir alembic==1.12.1 Mako>=1.2.2 python-editor>=1.0.4

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create necessary directories
RUN mkdir -p /app/alembic/versions

# Copy application code
COPY . .

# Development mode with hot reload
CMD ["sh", "-c", "python scripts/init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]