#!/bin/bash

# Simple Neo AI Startup Script
# Runs backend and frontend without Docker

echo "🚀 Starting Neo AI (Simple Mode)"
echo "================================="

# Check if ports are available
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

echo "🔍 Checking ports..."
check_port 3000 || exit 1
check_port 8000 || exit 1

# Check configuration
echo ""
echo "📋 Checking configuration..."
if [ ! -f "backend/.env" ]; then
    echo "❌ Backend .env file not found"
    exit 1
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "❌ Frontend .env.local file not found"
    exit 1
fi

echo "✅ Configuration files found"

# Start backend
echo ""
echo "🔧 Starting Backend..."
cd backend
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Check if backend is responding
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo ""
echo "🎨 Starting Frontend..."
cd ../frontend
npm run start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
sleep 10

# Check if frontend is responding
if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Neo AI is now running!"
echo "========================"
echo ""
echo "📱 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🌍 For global access, run in another terminal:"
echo "   ngrok http 3000"
echo ""
echo "🛑 To stop Neo AI:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 View logs:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""

# Save PIDs for cleanup
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

echo "Press Ctrl+C to stop all services..."

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo "✅ Services stopped"; exit 0' INT

# Keep script running
wait