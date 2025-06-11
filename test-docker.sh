#!/bin/bash

echo "🧪 Testing Gin Calculator Docker Container..."

# Function to check if container is running
check_container() {
    if [ "$(docker ps -q -f name=gin-calculator-app)" ]; then
        return 0
    else
        return 1
    fi
}

# Function to test HTTP response
test_http() {
    local url=$1
    local expected_code=$2
    
    echo "Testing $url..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" = "$expected_code" ]; then
        echo "✅ $url responded with $response"
        return 0
    else
        echo "❌ $url responded with $response (expected $expected_code)"
        return 1
    fi
}

# Check if container is running (try both development and production names)
if check_container; then
    container_name="gin-calculator-app"
    echo "✅ Container gin-calculator-app is running"
elif [ "$(docker ps -q -f name=gin-calculator-dev)" ]; then
    container_name="gin-calculator-dev"
    echo "✅ Container gin-calculator-dev is running"
else
    echo "❌ No gin calculator container is running"
    echo "Run ./build-and-run.sh or ./build-dev.sh first"
    exit 1
fi

# Wait a bit for the server to start
echo "⏱️ Waiting for server to start..."
sleep 10

# Test main application
test_http "http://localhost:8000" "200"

# Test admin page
test_http "http://localhost:8000/admin/" "302"

# Test API endpoint (should redirect or return error without proper data)
test_http "http://localhost:8000/calculate/" "405"

echo ""
echo "🎉 Basic tests completed!"
echo "🌐 Visit http://localhost:8000 to use the application"
echo "🔧 Visit http://localhost:8000/admin to access admin panel"
