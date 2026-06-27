#!/bin/bash

# Production deployment script for the gin calculator

echo "Building Gin Calculator for Production..."

# Build the production image
docker build -t gin-calculator:production \
    --build-arg DJANGO_ENV=production \
    .

if [ $? -eq 0 ]; then
    echo "✅ Production build successful!"
    echo "🚀 Starting production container..."
    
    # Run the production container with proper volume mounting
    docker run -d \
        --name gin-calculator-prod \
        -p 80:8000 \
        -e DEBUG=False \
        -e ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com \
        -e DATABASE_PATH=/app/db_data/db.sqlite3 \
        -v gin-calculator-prod-db:/app/db_data \
        -v gin-calculator-prod-media:/app/media \
        --restart unless-stopped \
        gin-calculator:production
    
    if [ $? -eq 0 ]; then
        echo "✅ Production container started successfully!"
        echo "🌐 Application available at: http://localhost"
        echo "🔧 Admin interface at: http://localhost/admin"
        echo "👤 Default admin credentials: admin / admin123"
        echo ""
        echo "⚠️  IMPORTANT: Change the default admin password!"
        echo "🔒 Also update the SECRET_KEY in production!"
    else
        echo "❌ Failed to start production container"
        exit 1
    fi
else
    echo "❌ Production build failed"
    exit 1
fi
