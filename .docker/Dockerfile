FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal for production)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure WebSocket support is properly installed
RUN pip install --no-cache-dir websockets httptools uvloop

# Copy application code
COPY . .

# Set up entrypoint script
RUN mv /app/scripts/entrypoint.sh /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown appuser:appuser /entrypoint.sh && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Use entrypoint to run migrations before starting the app
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]