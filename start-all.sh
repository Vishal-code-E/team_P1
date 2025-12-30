#!/bin/bash

# Enterprise RAG System - Unified Startup Script
# Starts both backend and frontend services

set -e

echo "=========================================="
echo "Starting Enterprise RAG System"
echo "=========================================="

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Backend already running on port 8000"
    echo "   Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Check if frontend is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Frontend already running on port 3000"
    echo "   Killing existing process..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo ""
echo "🐍 Starting Backend (Python Flask)..."
cd enterprise-rag
source venv/bin/activate 2>/dev/null || . venv/bin/activate
python api_server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Logs: /tmp/backend.log"

# Wait for backend to be ready
echo "   Waiting for backend to start..."
for i in {1..15}; do
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "   ✅ Backend ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ❌ Backend failed to start. Check /tmp/backend.log"
        exit 1
    fi
    sleep 1
done

cd ..

echo ""
echo "⚛️  Starting Frontend (Next.js)..."
cd enterprise-rag-frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: /tmp/frontend.log"

# Wait for frontend to be ready
echo "   Waiting for frontend to start..."
for i in {1..15}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "   ✅ Frontend ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ❌ Frontend failed to start. Check /tmp/frontend.log"
        exit 1
    fi
    sleep 1
done

echo ""
echo "=========================================="
echo "✅ System Ready!"
echo "=========================================="
echo ""
echo "🌐 Frontend:  http://localhost:3000"
echo "🔌 Backend:   http://127.0.0.1:8000"
echo ""
echo "📋 Backend PID:  $BACKEND_PID"
echo "📋 Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to view logs (services will keep running)"
echo "=========================================="

# Follow logs
tail -f /tmp/backend.log /tmp/frontend.log
