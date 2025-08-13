# Use Python 3.12 slim for better performance and security
FROM python:3.12-slim

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install system dependencies for stability
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt ./

# Install Python dependencies with improved settings
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app && \
    chown -R app:app /app && \
    chmod +x docker_server.py

# Create directories for logs
RUN mkdir -p /tmp/mcp-logs && \
    chown app:app /tmp/mcp-logs

# Switch to non-root user
USER app

# Add comprehensive health check
HEALTHCHECK --interval=20s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8083/health || exit 1

# Expone el puerto 8083 para evitar conflictos
EXPOSE 8083

# Use the robust Docker server with retry logic
CMD ["python", "docker_server.py"]
