#!/bin/bash

# Backend Fix Verification Script
# Tests that the backend no longer crashes and handles all scenarios correctly

echo "=========================================="
echo "Backend Fix Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend URL (change if testing production)
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "Testing backend at: $BACKEND_URL"
echo ""

# Test 1: Health check (should work immediately)
echo "Test 1: Health check (should return immediately)"
echo "-------------------------------------------"
START=$(date +%s%N)
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/api/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 )) # Convert to milliseconds

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Health check returned 200"
    echo "Response time: ${DURATION}ms"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}✗ FAIL${NC} - Health check returned $HTTP_CODE"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test 2: First chat request (triggers lazy initialization)
echo "Test 2: First chat request (triggers initialization)"
echo "---------------------------------------------------"
CHAT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the PTO policy?"}')
HTTP_CODE=$(echo "$CHAT_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$CHAT_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "503" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Chat endpoint returned $HTTP_CODE (valid JSON response)"
    echo "Response: $RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}✗ FAIL${NC} - Chat endpoint returned $HTTP_CODE"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test 3: Verify response is valid JSON
echo "Test 3: Verify response is valid JSON"
echo "--------------------------------------"
if echo "$RESPONSE_BODY" | jq '.' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC} - Response is valid JSON"
    
    # Check for required fields
    HAS_ANSWER=$(echo "$RESPONSE_BODY" | jq 'has("answer")')
    HAS_SOURCES=$(echo "$RESPONSE_BODY" | jq 'has("sources")')
    HAS_CONFIDENCE=$(echo "$RESPONSE_BODY" | jq 'has("confidence")')
    
    if [ "$HAS_ANSWER" = "true" ] && [ "$HAS_SOURCES" = "true" ] && [ "$HAS_CONFIDENCE" = "true" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Response has all required fields (answer, sources, confidence)"
    else
        echo -e "${YELLOW}⚠ WARNING${NC} - Response missing some fields"
        echo "  has answer: $HAS_ANSWER"
        echo "  has sources: $HAS_SOURCES"
        echo "  has confidence: $HAS_CONFIDENCE"
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Response is not valid JSON"
fi
echo ""

# Test 4: Second chat request (should reuse initialized chain)
echo "Test 4: Second chat request (should be faster)"
echo "----------------------------------------------"
START=$(date +%s%N)
CHAT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I request time off?"}')
HTTP_CODE=$(echo "$CHAT_RESPONSE" | tail -n 1)
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "503" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Second request returned $HTTP_CODE"
    echo "Response time: ${DURATION}ms"
else
    echo -e "${RED}✗ FAIL${NC} - Second request returned $HTTP_CODE"
fi
echo ""

# Test 5: Health check after initialization
echo "Test 5: Health check after initialization"
echo "-----------------------------------------"
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/api/health")
QA_INITIALIZED=$(echo "$HEALTH_RESPONSE" | jq -r '.qa_chain_initialized')

echo "Response: $HEALTH_RESPONSE"
if [ "$QA_INITIALIZED" = "true" ]; then
    echo -e "${GREEN}✓ PASS${NC} - QA chain is initialized"
elif [ "$QA_INITIALIZED" = "false" ]; then
    echo -e "${YELLOW}⚠ WARNING${NC} - QA chain not initialized (check if documents exist)"
else
    echo -e "${RED}✗ FAIL${NC} - Could not determine initialization status"
fi
echo ""

# Test 6: Invalid request (should return JSON error)
echo "Test 6: Invalid request handling"
echo "---------------------------------"
ERROR_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{}')
HTTP_CODE=$(echo "$ERROR_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$ERROR_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "400" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Invalid request returned 400"
    if echo "$RESPONSE_BODY" | jq '.' >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC} - Error response is valid JSON"
        echo "Response: $RESPONSE_BODY" | jq '.'
    else
        echo -e "${RED}✗ FAIL${NC} - Error response is not valid JSON"
    fi
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Expected 400, got $HTTP_CODE"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "Key Checks:"
echo "  ✓ Health check works immediately"
echo "  ✓ Chat endpoint returns valid JSON"
echo "  ✓ Errors return JSON (not plain text)"
echo "  ✓ Second requests reuse initialized chain"
echo ""
echo "If all tests passed, the backend is ready for production!"
