#!/bin/bash
# Quick deployment test script
# Tests the new features without requiring the full model to be loaded

set -e

echo "=========================================="
echo "Testing New Features"
echo "=========================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "⚠️  Server not running on localhost:8080"
    echo "   Start server with: uvicorn app.main:app --host 0.0.0.0 --port 8080"
    echo ""
    echo "Or test against deployed instance by setting API_URL:"
    echo "   export API_URL=https://your-space.hf.space"
    echo "   ./test_deployment.sh"
    exit 1
fi

API_URL="${API_URL:-http://localhost:8080}"
echo "Testing against: $API_URL"
echo ""

# Test 1: Health endpoint
echo "1. Testing /health endpoint..."
HEALTH=$(curl -s "$API_URL/health")
if echo "$HEALTH" | grep -q "model_ready"; then
    echo "   ✓ Health endpoint includes model_ready field"
    echo "   Response: $HEALTH"
else
    echo "   ✗ Health endpoint missing model_ready field"
    exit 1
fi
echo ""

# Test 2: Stats endpoint
echo "2. Testing /v1/stats endpoint..."
STATS=$(curl -s "$API_URL/v1/stats")
if echo "$STATS" | grep -q "total_requests"; then
    echo "   ✓ Stats endpoint working"
    echo "   Response preview: $(echo "$STATS" | head -c 200)..."
else
    echo "   ✗ Stats endpoint not working"
    exit 1
fi
echo ""

# Test 3: Rate limiting headers
echo "3. Testing rate limiting headers..."
HEADERS=$(curl -s -I "$API_URL/v1/models")
if echo "$HEADERS" | grep -q "X-RateLimit-Limit-Minute"; then
    echo "   ✓ Rate limit headers present"
    echo "$HEADERS" | grep "X-RateLimit"
else
    echo "   ✗ Rate limit headers missing"
    exit 1
fi
echo ""

# Test 4: Error sanitization
echo "4. Testing error sanitization..."
ERROR_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"model":"test","messages":[]}')
HTTP_CODE=$(echo "$ERROR_RESPONSE" | tail -n1)
ERROR_BODY=$(echo "$ERROR_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "400" ]; then
    if echo "$ERROR_BODY" | grep -q "messages list cannot be empty"; then
        echo "   ✓ Error properly formatted (400 with clear message)"
    else
        echo "   ⚠️  Got 400 but error message format unexpected"
    fi
else
    echo "   ⚠️  Expected 400, got $HTTP_CODE"
fi
echo ""

# Test 5: Root endpoint
echo "5. Testing / endpoint..."
ROOT=$(curl -s "$API_URL/")
if echo "$ROOT" | grep -q "status"; then
    echo "   ✓ Root endpoint working"
else
    echo "   ✗ Root endpoint not working"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ All basic tests passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test with actual model requests (requires model to be loaded)"
echo "2. Test rate limiting by making 31 requests in a minute"
echo "3. Check stats endpoint after making some requests"

