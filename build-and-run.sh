#!/bin/bash

# Build and run script for the gin calculator Docker container

echo "🍸 Building Gin Calculator Docker Image..."

# Stop and remove existing container if it exists
if [ "$(docker ps -q -f name=gin-calculator-app)" ]; then
    echo "🛑 Stopping existing container..."
    docker stop gin-calculator-app
fi

if [ "$(docker ps -aq -f name=gin-calculator-app)" ]; then
    echo "🗑️ Removing existing container..."
    docker rm gin-calculator-app
fi

# Build the Docker image
echo "🔨 Building image..."
docker build -t gin-calculator .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "🚀 Starting container..."
    
    # Run the container with proper volume mounting
    docker run -d \
        --name gin-calculator-app \
        -p 8000:8000 \
        -v gin-calculator-db:/app/db_data \
        -v gin-calculator-media:/app/media \
        -e DATABASE_PATH=/app/db_data/db.sqlite3 \
        --restart unless-stopped \
        gin-calculator
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo ""
        echo "🎉 Setup complete!"
        echo "🌐 Application: http://localhost:8000"
        echo "🔧 Admin panel: http://localhost:8000/admin"
        echo "👤 Default admin: admin / admin123"
        echo ""
        echo "📋 Useful commands:"
        echo "  View logs:         docker logs -f gin-calculator-app"
        echo "  Stop container:    docker stop gin-calculator-app"
        echo "  Remove container:  docker rm gin-calculator-app"
        echo "  Shell access:      docker exec -it gin-calculator-app sh"
        echo "  Health check:      docker ps (look for 'healthy' status)"
        echo ""
        echo "⏱️ Waiting for startup (this may take a few seconds)..."
        sleep 5
        
        # Check if container is healthy
        if [ "$(docker ps -q -f name=gin-calculator-app -f health=healthy)" ]; then
            echo "💚 Container is healthy and ready!"
        else
            echo "⚠️ Container started but health check pending..."
            echo "📜 Check logs with: docker logs gin-calculator-app"
        fi
    else
        echo "❌ Failed to start container"
        echo "📜 Check logs with: docker logs gin-calculator-app"
        exit 1
    fi
else
    echo "❌ Build failed"
    echo "💡 Try building without cache: docker build --no-cache -t gin-calculator ."
    exit 1
fi
