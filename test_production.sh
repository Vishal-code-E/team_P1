#!/bin/bash
# Full Stack Production Test

echo "🧪 Testing MemOrg AI Production Deployment"
echo "=========================================="
echo ""

# Test 1: Frontend
echo "1️⃣ Testing Frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://enterprise-rag-frontend.vercel.app)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend: WORKING (https://enterprise-rag-frontend.vercel.app)"
else
    echo "   ❌ Frontend: FAILED (Status: $FRONTEND_STATUS)"
fi
echo ""

# Test 2: Backend Health
echo "2️⃣ Testing Backend Health..."
BACKEND_HEALTH=$(curl -s https://memorg-ai.onrender.com/api/health)
if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo "   ✅ Backend Health: WORKING"
    echo "   Response: $BACKEND_HEALTH"
else
    echo "   ❌ Backend Health: FAILED"
    echo "   Response: $BACKEND_HEALTH"
fi
echo ""

# Test 3: End-to-End Chat Test
echo "3️⃣ Testing End-to-End Chat..."
CHAT_RESPONSE=$(curl -s -X POST https://memorg-ai.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is AWS Budget policy?"}' \
  --max-time 45)

if echo "$CHAT_RESPONSE" | grep -q "answer"; then
    echo "   ✅ Chat API: WORKING"
    echo "   Response contains answer field"
    # Extract first 100 chars of answer
    ANSWER=$(echo "$CHAT_RESPONSE" | grep -o '"answer":"[^"]*"' | head -c 150)
    echo "   Preview: $ANSWER..."
else
    echo "   ❌ Chat API: FAILED"
    echo "   Response: $CHAT_RESPONSE"
fi
echo ""

echo "=========================================="
echo "✨ Production Test Complete!"
echo ""
echo "🌐 Production URLs:"
echo "   Frontend: https://enterprise-rag-frontend.vercel.app"
echo "   Backend: https://memorg-ai.onrender.com"
echo ""
echo "📝 Notes:"
echo "   - Frontend deployed from MAIN branch ✅"
echo "   - Using GPT-4 Turbo model"
echo "   - OpenAI embeddings (1536D)"
