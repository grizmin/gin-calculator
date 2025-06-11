#!/bin/bash

# Simple build and run script for development (no persistent volumes)

echo "🍸 Building Gin Calculator Docker Image (Development Mode)..."

# Stop and remove existing container if it exists
if [ "$(docker ps -q -f name=gin-calculator-dev)" ]; then
    echo "🛑 Stopping existing container..."
    docker stop gin-calculator-dev
fi

if [ "$(docker ps -aq -f name=gin-calculator-dev)" ]; then
    echo "🗑️ Removing existing container..."
    docker rm gin-calculator-dev
fi

# Build the Docker image
echo "🔨 Building image..."
docker build -t gin-calculator .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "🚀 Starting container (development mode - no persistent data)..."
    
    # Run the container without volume mounting for development
    docker run -d \
        --name gin-calculator-dev \
        -p 8000:8000 \
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
        echo "⚠️  Note: This is development mode - data will not persist between container restarts"
        echo ""
        echo "📋 Useful commands:"
        echo "  View logs:         docker logs -f gin-calculator-dev"
        echo "  Stop container:    docker stop gin-calculator-dev"
        echo "  Remove container:  docker rm gin-calculator-dev"
        echo "  Shell access:      docker exec -it gin-calculator-dev sh"
        echo ""
        echo "⏱️ Waiting for startup (this may take a few seconds)..."
        sleep 5
        
        # Check if container is still running
        if [ "$(docker ps -q -f name=gin-calculator-dev)" ]; then
            echo "💚 Container is running!"
        else
            echo "❌ Container stopped unexpectedly"
            echo "📜 Check logs with: docker logs gin-calculator-dev"
        fi
    else
        echo "❌ Failed to start container"
        echo "📜 Check logs with: docker logs gin-calculator-dev"
        exit 1
    fi
else
    echo "❌ Build failed"
    echo "💡 Try building without cache: docker build --no-cache -t gin-calculator ."
    exit 1
fi
