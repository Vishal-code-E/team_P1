#!/bin/bash

# Test script to verify backend-frontend connectivity

echo "=========================================="
echo "Testing Enterprise RAG System"
echo "=========================================="
echo ""

# Test 1: Backend Health
echo "1️⃣  Testing Backend Health..."
HEALTH=$(curl -s http://127.0.0.1:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Backend is healthy"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Backend health check failed"
    echo "   Response: $HEALTH"
    exit 1
fi

echo ""

# Test 2: Backend Chat Endpoint
echo "2️⃣  Testing Backend Chat Endpoint..."
CHAT_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello"}' \
    --max-time 30)

if echo "$CHAT_RESPONSE" | grep -q "answer"; then
    echo "   ✅ Backend chat endpoint working"
    echo "   Response preview: $(echo "$CHAT_RESPONSE" | head -c 100)..."
else
    echo "   ❌ Backend chat endpoint failed"
    echo "   Response: $CHAT_RESPONSE"
    exit 1
fi

echo ""

# Test 3: Frontend Health
echo "3️⃣  Testing Frontend..."
FRONTEND=$(curl -s http://localhost:3000 --max-time 5)
if [ $? -eq 0 ]; then
    echo "   ✅ Frontend is accessible"
else
    echo "   ❌ Frontend not accessible"
    exit 1
fi

echo ""

# Test 4: Frontend API Route
echo "4️⃣  Testing Frontend API Route..."
API_RESPONSE=$(curl -s -X POST http://localhost:3000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Test"}' \
    --max-time 30)

if echo "$API_RESPONSE" | grep -q "answer"; then
    echo "   ✅ Frontend API route connected to backend"
    echo "   Response preview: $(echo "$API_RESPONSE" | head -c 100)..."
else
    echo "   ❌ Frontend API route failed"
    echo "   Response: $API_RESPONSE"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All Tests Passed!"
echo "=========================================="
echo ""
echo "System is ready to use:"
echo "🌐 Open http://localhost:3000 in your browser"
echo ""
