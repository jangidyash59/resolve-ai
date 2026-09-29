# 🔧 Deployment Troubleshooting Guide

## Common Errors and Solutions

### ❌ Error: "timeout of 90000ms exceeded"

**Cause:** FAISS index building takes longer than 90 seconds (typically 3-5 minutes for 228 chunks)

**Solution Option 1: Pre-build Index Locally (RECOMMENDED)**

```bash
cd ai-service

# Ensure .env has GEMINI_API_KEY
cat .env | grep GEMINI_API_KEY

# Run pre-build script
./prebuild.sh

# Commit the pre-built index
git add faiss_store/
git commit -m "feat: add pre-built FAISS index for faster deployment"
git push origin main
```

**Benefits:**
- ✅ Deployment startup: 5 seconds (vs 5 minutes)
- ✅ No timeout errors
- ✅ Predictable deployment times

**Solution Option 2: Increase Timeout in Render**

1. Go to Render Dashboard → Your Service
2. Settings → Advanced → Health Check Path
3. Set: "Start Period" to `300` seconds (5 minutes)
4. Click "Save Changes"

---

### ❌ Error: "GEMINI_API_KEY not set"

**Cause:** Environment variable missing in Render

**Solution:**

1. Go to Render Dashboard → `resolveai-ai-service`
2. Click "Environment" tab
3. Add variable:
   ```
   Key: GEMINI_API_KEY
   Value: <your-gemini-api-key>
   ```
4. Click "Save Changes" (triggers redeploy)

**Get API Key:**
- Visit: https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy and paste into Render

---

### ❌ Error: "Failed to generate embedding after 3 attempts"

**Cause:** Gemini API rate limiting or network issues

**Solution 1: Check API Quota**
```bash
# Visit Gemini API Console
https://aistudio.google.com/app/apikey

# Check quota limits:
# Free tier: 1500 requests/minute
# Your usage: 228 requests for full index build
```

**Solution 2: Retry with Exponential Backoff (ALREADY IMPLEMENTED)**

The code now includes automatic retry logic:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Attempt 4: Wait 6 seconds

**Solution 3: Use Pre-built Index**

Avoid API calls entirely by committing the index (see Option 1 above)

---

### ❌ Error: "ModuleNotFoundError: No module named 'google'"

**Cause:** Missing dependency

**Solution:**

Check `requirements.txt` includes:
```txt
google-genai>=0.2.0
```

If missing, add it:
```bash
cd ai-service
echo "google-genai>=0.2.0" >> requirements.txt
git add requirements.txt
git commit -m "fix: add google-genai dependency"
git push origin main
```

---

### ❌ Error: "Connection refused" or "Service Unavailable"

**Cause:** Service not fully started or crashed

**Solution 1: Check Logs**

```bash
# In Render Dashboard:
1. Go to your service
2. Click "Logs" tab
3. Look for errors near the bottom
```

**Common Log Patterns:**

**✅ Healthy:**
```
INFO: Loading pre-built FAISS index...
✓ Loaded 228 policy vectors from pre-built index.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**❌ Problem:**
```
ERROR: Failed to build FAISS index: <error message>
```

**Solution 2: Manual Redeploy**

1. Render Dashboard → Your Service
2. Click "Manual Deploy" → "Clear build cache & deploy"

---

### ❌ Error: "Health check failed"

**Cause:** Service taking too long to start

**Solution:**

Update Dockerfile health check (ALREADY DONE):
```dockerfile
HEALTHCHECK --interval=30s --timeout=15s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

`--start-period=300s` = Allow 5 minutes for initial startup

---

## 🚀 Optimal Deployment Workflow

### **Pre-Deployment Checklist**

```bash
cd /home/jangidworld/Desktop/resolve-ai

# 1. Build index locally
cd ai-service
./prebuild.sh

# 2. Verify index files exist
ls -lh faiss_store/
# Should show:
#   index.faiss (varies, typically 500KB-2MB)
#   metadata.json (200-500KB)

# 3. Test locally
python build_index.py  # Should load pre-built index instantly
python -c "from src.orchestrator_simple import search_policies; print(search_policies('return policy', 3))"

# 4. Commit and push
git add faiss_store/ ai-service/
git commit -m "feat: optimize deployment with pre-built index and retry logic"
git push origin main
```

### **Deployment Timeline**

**Without Pre-built Index:**
```
0:00 - Deploy starts
0:30 - Dependencies installed
1:00 - Application starts
1:05 - FAISS index building begins...
4:30 - Index building completes
4:35 - Service ready ✓
```

**With Pre-built Index:**
```
0:00 - Deploy starts
0:30 - Dependencies installed
1:00 - Application starts
1:05 - Loads pre-built index (5 seconds)
1:10 - Service ready ✓
```

**Time Saved: 3 minutes 25 seconds**

---

## 🔍 Monitoring & Debugging

### Check Service Health

```bash
# Replace with your Render URL
AI_SERVICE_URL="https://resolveai-ai-service.onrender.com"

# Test health endpoint
curl $AI_SERVICE_URL/health

# Expected response:
{
  "status": "healthy",
  "service": "ResolveAI AI Service",
  "version": "1.0.0",
  "faiss_initialized": true
}
```

### Test Circuit Breaker

```bash
# Test out-of-domain query (should auto-escalate)
curl -X POST $AI_SERVICE_URL/api/resolve-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "customer_name": "Test",
    "customer_email": "test@test.com",
    "customer_tier": "gold",
    "ticket_text": "What is the capital of France?"
  }' | jq '.requires_escalation'

# Expected: true
```

### Check Metrics

```bash
curl $AI_SERVICE_URL/api/metrics | jq

# Expected:
{
  "total_tickets": 0,
  "error": "No events recorded"
}
# (Will populate as tickets are processed)
```

---

## 🔄 Rollback Strategy

If deployment fails:

```bash
# Option 1: Revert to previous commit
git log --oneline -5  # Find working commit hash
git revert <commit-hash>
git push origin main

# Option 2: Redeploy previous version in Render
# Render Dashboard → Service → "Deploys" tab → Select previous deploy → "Redeploy"
```

---

## 📊 Performance Benchmarks

**Expected Metrics After Deployment:**

| Metric | Target | Check |
|--------|--------|-------|
| Service Startup | <2 minutes | Check Render logs |
| Index Load Time | <10 seconds | Look for "Loaded 228 policy vectors" |
| Health Check Response | <100ms | `curl <url>/health` |
| Search Query | <20ms | Check logs for "Semantic search" |
| LLM Response | 3-5 seconds | End-to-end ticket resolution |
| Circuit Breaker | <50ms | Auto-escalation queries |

---

## 🆘 Still Having Issues?

### Collect Debug Information

```bash
# Check environment
cd ai-service
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import faiss; print(f'FAISS: {faiss.__version__}')"
python -c "from google import genai; print('Gemini: OK')"

# Check files
ls -lah faiss_store/
cat .env | grep -v "KEY"  # Don't print secrets

# Test imports
python -c "from src.orchestrator_simple import build_policy_index; print('Imports: OK')"
```

### Contact Support

If all else fails, provide these details:

1. **Error Message:** Full error from Render logs
2. **Deployment Platform:** Render / Vercel / Other
3. **Python Version:** (from debug commands above)
4. **Index Status:** Does `faiss_store/` exist locally?
5. **API Key Status:** Is GEMINI_API_KEY set in Render?
6. **Last Working Commit:** `git log --oneline -1`

---

## ✅ Success Indicators

You'll know deployment succeeded when:

1. ✅ Render service shows "Live" status (green dot)
2. ✅ Logs show: "✓ Loaded 228 policy vectors from pre-built index"
3. ✅ Health endpoint returns `{"status": "healthy"}`
4. ✅ Test query completes in <5 seconds
5. ✅ Frontend can submit tickets without errors

---

**Remember:** The pre-built index approach is the recommended solution. It eliminates timeout issues and makes deployments predictable.
