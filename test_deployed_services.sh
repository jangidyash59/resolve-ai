#!/bin/bash
# Test deployed ResolveAI services on Render

echo "=================================================="
echo "Testing ResolveAI Deployed Services"
echo "=================================================="
echo ""

# Set your Render service URLs here
AI_SERVICE_URL="https://resolveai-ai-service.onrender.com"
API_GATEWAY_URL="https://resolveai-api-gateway.onrender.com"

echo "1. Testing AI Service Health"
echo "   URL: $AI_SERVICE_URL/health"
echo "   ---"
AI_HEALTH=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$AI_SERVICE_URL/health" 2>&1)
AI_HTTP_CODE=$(echo "$AI_HEALTH" | grep "HTTP_CODE:" | cut -d: -f2)
AI_RESPONSE=$(echo "$AI_HEALTH" | grep -v "HTTP_CODE:")

if [ "$AI_HTTP_CODE" = "200" ]; then
    echo "   ✓ AI Service is healthy"
    echo "   Response: $AI_RESPONSE"
else
    echo "   ❌ AI Service is NOT healthy"
    echo "   HTTP Code: $AI_HTTP_CODE"
    echo "   Response: $AI_RESPONSE"
    echo ""
    echo "   DIAGNOSIS: AI service is down or not deployed correctly"
    echo "   ACTION: Check Render dashboard → resolveai-ai-service → Logs"
fi

echo ""
echo "=================================================="
echo "2. Testing API Gateway Health"
echo "   URL: $API_GATEWAY_URL/health"
echo "   ---"
API_HEALTH=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_GATEWAY_URL/health" 2>&1)
API_HTTP_CODE=$(echo "$API_HEALTH" | grep "HTTP_CODE:" | cut -d: -f2)
API_RESPONSE=$(echo "$API_HEALTH" | grep -v "HTTP_CODE:")

if [ "$API_HTTP_CODE" = "200" ]; then
    echo "   ✓ API Gateway is healthy"
    echo "   Response: $API_RESPONSE"
else
    echo "   ❌ API Gateway is NOT healthy"
    echo "   HTTP Code: $API_HTTP_CODE"
    echo "   Response: $API_RESPONSE"
    echo ""
    echo "   DIAGNOSIS: API Gateway is down or misconfigured"
    echo "   ACTION: Check Render dashboard → resolveai-api-gateway → Logs"
fi

echo ""
echo "=================================================="
echo "3. Testing AI Service Search Endpoint (if healthy)"
echo "   ---"
if [ "$AI_HTTP_CODE" = "200" ]; then
    echo "   Testing policy search..."
    SEARCH_TEST=$(curl -s -X POST "$AI_SERVICE_URL/api/search-policies?query=return+policy&k=1" \
        -H "Content-Type: application/json" 2>&1)
    
    if echo "$SEARCH_TEST" | grep -q "results"; then
        echo "   ✓ Policy search working"
        echo "   Sample: $(echo "$SEARCH_TEST" | head -c 100)..."
    else
        echo "   ❌ Policy search failed"
        echo "   Response: $SEARCH_TEST"
    fi
else
    echo "   ⚠️  Skipped (AI service not healthy)"
fi

echo ""
echo "=================================================="
echo "4. Summary & Next Steps"
echo "=================================================="
echo ""

if [ "$AI_HTTP_CODE" = "200" ] && [ "$API_HTTP_CODE" = "200" ]; then
    echo "✅ All services are running!"
    echo ""
    echo "Your application should be working at:"
    echo "   https://resolve-ai-frontend.vercel.app/"
    echo ""
    echo "If you're still seeing errors, the issue might be:"
    echo "   1. Render environment variables (GROQ_API_KEY, GEMINI_API_KEY)"
    echo "   2. Frontend pointing to wrong API URL"
    echo "   3. CORS configuration issue"
else
    echo "❌ Service health check failed"
    echo ""
    echo "IMMEDIATE ACTIONS:"
    echo ""
    
    if [ "$AI_HTTP_CODE" != "200" ]; then
        echo "1. Check AI Service Logs:"
        echo "   → Render Dashboard → resolveai-ai-service → Logs"
        echo "   Look for: 'Service Ready!' or error messages"
        echo ""
        echo "2. Verify Environment Variables:"
        echo "   → Render Dashboard → resolveai-ai-service → Environment"
        echo "   Required: GROQ_API_KEY, GEMINI_API_KEY"
        echo ""
        echo "3. Check if service is sleeping (free tier):"
        echo "   → First request after 15min inactivity takes 30-60s"
        echo "   → Try accessing $AI_SERVICE_URL again in 60 seconds"
        echo ""
    fi
    
    if [ "$API_HTTP_CODE" != "200" ]; then
        echo "4. Check API Gateway Logs:"
        echo "   → Render Dashboard → resolveai-api-gateway → Logs"
        echo "   Look for connection errors or crashes"
        echo ""
        echo "5. Verify API Gateway Environment:"
        echo "   → MONGODB_URI (should be Atlas connection string)"
        echo "   → AI_SERVICE_URL (should be: $AI_SERVICE_URL)"
        echo ""
    fi
fi

echo ""
echo "=================================================="
echo "For detailed troubleshooting, see:"
echo "   DEPLOYMENT_FIX.md"
echo "   FIXES_APPLIED.md"
echo "=================================================="
