# Use Python Alpine as base image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=gin_calculator.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    sqlite \
    sqlite-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Create necessary directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/db_data
RUN chmod 755 /app/staticfiles /app/media /app/db_data

# Create a non-root user
RUN adduser -D -s /bin/sh gin_user
RUN chown -R gin_user:gin_user /app

# Switch to non-root user
USER gin_user

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
