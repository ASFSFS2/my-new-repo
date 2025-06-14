#!/bin/bash

# Neo AI Global Deployment Script
# This script sets up Neo AI for global access

echo "🚀 Neo AI Global Deployment"
echo "============================"

# Check if running in production mode
if [ "$1" = "prod" ]; then
    echo "📦 Using production configuration..."
    COMPOSE_FILE="docker-compose.prod.yml"
else
    echo "🔧 Using development configuration..."
    COMPOSE_FILE="docker-compose.yaml"
fi

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Check required ports
echo ""
echo "🔍 Checking ports..."
check_port 3000 || exit 1
check_port 8000 || exit 1
check_port 6379 || exit 1
check_port 5672 || exit 1

# Check Docker
echo ""
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Please install Docker Desktop from https://docker.com"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "   Please start Docker Desktop"
    exit 1
fi

echo "✅ Docker is available"

# Check configuration files
echo ""
echo "📋 Checking configuration..."
if [ ! -f "backend/.env" ]; then
    echo "❌ Backend .env file not found"
    echo "   Please create backend/.env with required configuration"
    exit 1
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "❌ Frontend .env.local file not found"
    echo "   Please create frontend/.env.local with required configuration"
    exit 1
fi

echo "✅ Configuration files found"

# Build and start services
echo ""
echo "🏗️ Building and starting services..."
docker-compose -f $COMPOSE_FILE down --remove-orphans
docker-compose -f $COMPOSE_FILE build --no-cache
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

# Check Redis
if docker-compose -f $COMPOSE_FILE exec redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not responding"
fi

# Check RabbitMQ
if docker-compose -f $COMPOSE_FILE exec rabbitmq rabbitmq-diagnostics ping | grep -q "Ping succeeded"; then
    echo "✅ RabbitMQ is healthy"
else
    echo "❌ RabbitMQ is not responding"
fi

# Check Backend
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi

# Check Frontend
if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🌐 Neo AI is now running!"
echo "========================"
echo ""
echo "📱 Local Access:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   RabbitMQ Management: http://localhost:15672"
echo ""

# Global access options
echo "🌍 Global Access Options:"
echo ""
echo "1. 🔗 Ngrok (Recommended for testing):"
echo "   Install: https://ngrok.com/download"
echo "   Run: ngrok http 3000"
echo "   Share the https://xxx.ngrok.io URL"
echo ""
echo "2. ☁️ Cloud Deployment:"
echo "   - Deploy to DigitalOcean, AWS, or Google Cloud"
echo "   - Use docker-compose.prod.yml for production"
echo "   - Configure domain and SSL certificates"
echo ""
echo "3. 🏠 Port Forwarding:"
echo "   - Configure router to forward port 3000"
echo "   - Access via your public IP"
echo "   - Note: Security considerations apply"
echo ""

# Ngrok setup if available
if command -v ngrok &> /dev/null; then
    echo "🔗 Ngrok detected! Setting up global access..."
    echo ""
    echo "Starting ngrok tunnel..."
    echo "Press Ctrl+C to stop ngrok and return to terminal"
    echo ""
    ngrok http 3000
else
    echo "💡 To enable global access with ngrok:"
    echo "   1. Download ngrok: https://ngrok.com/download"
    echo "   2. Install and authenticate"
    echo "   3. Run: ngrok http 3000"
    echo "   4. Share the generated URL"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 View logs:"
echo "   docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f $COMPOSE_FILE down"