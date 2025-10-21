# Multi-stage Docker build for production deployment
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=love_chat.settings_production
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        curl \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy project files
COPY . .
RUN chown -R app:app /app

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R app:app /app/staticfiles /app/media /app/logs

# Copy nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Switch to app user
USER app

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose ports
EXPOSE 8000 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Switch back to root for supervisor
USER root

# Start services with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]