# Docker Deployment Guide

This guide covers how to build and deploy the Gin Calculator using Docker with Alpine Linux.

## Quick Start

### Option 1: Using the build script (Recommended)
```bash
# Make the script executable
chmod +x build-and-run.sh

# Build and run
./build-and-run.sh
```

### Option 2: Manual Docker commands
```bash
# Build the image
docker build -t gin-calculator .

# Run the container
docker run -d --name gin-calculator-app -p 8000:8000 gin-calculator
```

### Option 3: Using Docker Compose
```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Access the Application

- **Main App**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **Default Credentials**: admin / admin123

## Docker Image Details

- **Base Image**: python:3.11-alpine
- **Size**: ~150MB (optimized Alpine build)
- **Architecture**: Multi-platform support
- **Security**: Runs as non-root user

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | (default) | Django secret key |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0` | Comma-separated allowed hosts |

## Production Deployment

### Using the production script:
```bash
# Make executable
chmod +x deploy-production.sh

# Deploy to production
./deploy-production.sh
```

### Manual production deployment:
```bash
# Build production image
docker build -t gin-calculator:production .

# Run production container
docker run -d \
  --name gin-calculator-prod \
  -p 80:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-super-secret-key \
  -e ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com \
  --restart unless-stopped \
  gin-calculator:production
```

## Container Management

### Useful Commands
```bash
# View running containers
docker ps

# View logs
docker logs gin-calculator-app

# Access container shell
docker exec -it gin-calculator-app sh

# Stop container
docker stop gin-calculator-app

# Remove container
docker rm gin-calculator-app

# Remove image
docker rmi gin-calculator
```

### Data Persistence
The container includes a default SQLite database with sample data. For production, consider:

1. **Volume mounting** for database persistence:
```bash
docker run -d \
  --name gin-calculator-app \
  -p 8000:8000 \
  -v gin_data:/app \
  gin-calculator
```

2. **External database** (PostgreSQL, MySQL) for scalability

## Security Considerations

### For Production:
1. **Change default credentials** immediately
2. **Set custom SECRET_KEY** environment variable
3. **Use HTTPS** with a reverse proxy (nginx, traefik)
4. **Regular security updates** of the base image
5. **Limit container privileges**

### Example with custom secret:
```bash
docker run -d \
  --name gin-calculator-prod \
  -p 8000:8000 \
  -e SECRET_KEY=$(openssl rand -base64 32) \
  -e DEBUG=False \
  gin-calculator
```

## Troubleshooting

### Common Issues:

1. **Port already in use**:
   ```bash
   # Use different port
   docker run -d -p 8080:8000 gin-calculator
   ```

2. **Permission denied**:
   ```bash
   # Make scripts executable
   chmod +x *.sh
   ```

3. **Build fails**:
   ```bash
   # Clean build (no cache)
   docker build --no-cache -t gin-calculator .
   ```

4. **Container won't start**:
   ```bash
   # Check logs
   docker logs gin-calculator-app
   ```

## Multi-platform Builds

For deployment across different architectures:

```bash
# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t gin-calculator:latest \
  --push .
```

## Docker Compose for Development

For development with auto-reload:

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  gin-calculator:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=True
    command: python manage.py runserver 0.0.0.0:8000
```

Run with: `docker-compose -f docker-compose.dev.yml up`

## Performance Optimization

1. **Multi-stage builds** for smaller images
2. **Alpine packages** for minimal footprint
3. **Static file serving** via nginx in production
4. **Health checks** for container monitoring

## Monitoring

Add health checks to your deployment:

```bash
docker run -d \
  --name gin-calculator-app \
  -p 8000:8000 \
  --health-cmd="curl -f http://localhost:8000/ || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  gin-calculator
```
