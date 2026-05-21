FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=production \
    FLASK_ENV=production \
    FLASK_DEBUG=False

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copy application code
COPY batuma_gprs_weather/ ./batuma_gprs_weather/
COPY wsgi.py .
COPY gunicorn_config.py .

# Create logs directory
RUN mkdir -p logs

# Create non-root user
RUN useradd -m -u 1000 batuma && \
    chown -R batuma:batuma /app

# Switch to non-root user
USER batuma

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Run gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:application"]
