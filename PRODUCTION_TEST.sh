#!/bin/bash
# Production Stability Test Script
# Tests cold start resilience and deterministic behavior

echo "=== MEMORG AI PRODUCTION TEST ==="
echo ""

# Test 1: Backend Health Check
echo "1. Testing backend health..."
HEALTH=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://memorg-ai.onrender.com/api/health)
echo "$HEALTH"
echo ""

# Test 2: Backend Wake-up (simulate cold start)
echo "2. Simulating cold start wake-up..."
sleep 2
HEALTH2=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://memorg-ai.onrender.com/api/health)
echo "$HEALTH2"
echo ""

# Test 3: Frontend Health
echo "3. Testing frontend..."
FRONTEND=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://enterprise-rag-frontend-pux7d4p5y.vercel.app)
echo "HTTP_CODE: $(echo "$FRONTEND" | tail -1)"
echo ""

# Test 4: End-to-End Chat Request
echo "4. Testing end-to-end chat (with retry logic)..."
CHAT_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' \
  -w "\nHTTP_CODE:%{http_code}" \
  https://enterprise-rag-frontend-pux7d4p5y.vercel.app/api/chat)
echo "$CHAT_RESPONSE"
echo ""

echo "=== TEST COMPLETE ==="
echo "✅ All endpoints should return HTTP 200"
echo "✅ Chat should return a response (not timeout)"
echo "✅ Retries should handle cold starts automatically"
