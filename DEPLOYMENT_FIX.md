# Deployment Fix Guide - ResolveAI

## Problem Summary
The AI service is failing with "Failed to process ticket through AI service" because:
1. ✅ FAISS index is pre-built and in git (3MB file)
2. ✅ Code updated with better startup handling
3. ⚠️ Need to verify Render environment variables

## Immediate Fix Steps

### 1. Verify Render Environment Variables

Go to Render dashboard → `resolveai-ai-service` → Environment tab and ensure:

```bash
# CRITICAL: These must be set
GROQ_API_KEY=<YOUR_GROQ_KEY>  # Get from https://console.groq.com/keys
GEMINI_API_KEY=<YOUR_GEMINI_KEY>  # Get from https://aistudio.google.com/apikey - Must start with AQ.

# Model configuration (already in render.yaml)
GROQ_MODEL=openai/gpt-oss-120b
EMBEDDING_MODEL=gemini-embedding-001
VECTOR_STORE_PATH=./faiss_store
SIMILARITY_THRESHOLD=0.65

# Frontend URL for CORS
FRONTEND_URL=https://resolve-ai-frontend.vercel.app
```

### 2. Check Deployment Status

The code was just pushed and Render should auto-deploy. Monitor:
1. Go to Render dashboard → `resolveai-ai-service` → Logs
2. Look for these startup messages:
   ```
   ============================================================
   ResolveAI AI Service Starting...
   ============================================================
   Loading pre-built FAISS index...
   ✓ Loaded 228 policy vectors in 0.X s
   ✓ Orchestrator initialized in X.Xs
   Service Ready!
   ```

### 3. Test the AI Service Health

Once deployed, test:
```bash
curl https://resolveai-ai-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ResolveAI AI Service",
  "version": "1.0.0",
  "faiss_initialized": true
}
```

### 4. Test the Full Pipeline

From your frontend, submit a test ticket. If it still fails:

1. **Check Render logs** (most important):
   ```
   Dashboard → resolveai-ai-service → Logs
   ```
   Look for:
   - `❌ FAISS index loading failed` (means index not in deployment)
   - `ERROR: GEMINI_API_KEY not set` (missing env var)
   - `Error: 401 Unauthorized` (invalid API key)

2. **Check API Gateway logs**:
   ```
   Dashboard → resolveai-api-gateway → Logs
   ```
   Look for the AI service URL being called

## Common Issues and Fixes

### Issue 1: "Pre-built index not found"
**Fix**: The FAISS index should be in git. Verify locally:
```bash
cd ai-service
ls -lh faiss_store/
# Should show: index.faiss (2.7M), metadata.json (112K)
```

If missing, rebuild:
```bash
cd ai-service
source venv/bin/activate
python build_index.py
git add faiss_store/
git commit -m "Add pre-built FAISS index"
git push
```

### Issue 2: "Gemini API connection failed"
**Fix**: Verify your Gemini API key:
1. Go to https://aistudio.google.com/apikey
2. Copy the FULL key (starts with `AQ.`, ~60 characters)
3. Add to Render: Dashboard → Environment → `GEMINI_API_KEY`

### Issue 3: "Groq model not found"
**Fix**: The model name `openai/gpt-oss-120b` is correct. Verify:
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_GROQ_KEY"
```

### Issue 4: "Timeout during startup"
**Fix**: Already implemented! The new code loads index in <5 seconds instead of rebuilding (3-5 minutes).

### Issue 5: "Service unhealthy"
**Fix**: Check startup logs for errors. Most likely:
- Missing environment variables
- Invalid API keys
- FAISS index file corrupted

## Verification Checklist

After deployment completes:

- [ ] Health endpoint returns `"status": "healthy"`
- [ ] Render logs show: `✓ Loaded 228 policy vectors`
- [ ] Render logs show: `Service Ready!`
- [ ] Frontend can submit tickets without timeout
- [ ] Tickets get responses (not just "Failed to process")

## Still Not Working?

If the above steps don't fix it:

1. **Copy the full Render logs** (last 200 lines):
   ```
   Dashboard → resolveai-ai-service → Logs → Download
   ```

2. **Check the exact error** in logs:
   - Startup errors appear in first 30 seconds
   - Request errors appear when tickets are submitted

3. **Verify API keys** are valid:
   - Groq: https://console.groq.com/keys
   - Gemini: https://aistudio.google.com/apikey

4. **Check the deployed code** is latest:
   ```bash
   git log -1 --oneline
   # Should show: "Fix: Improve AI service startup performance..."
   ```

## Expected Timeline

- **Code push**: ✅ Done
- **Render auto-deploy**: ~5-8 minutes
- **Service startup**: ~10-15 seconds (with pre-built index)
- **First ticket**: Should work immediately after deployment

## Success Indicators

When everything is working:
- Gemini API usage: Small spike during first request (query embedding only)
- Groq API usage: Should show requests (1-2 per ticket)
- MongoDB: Tickets saved with status "resolved" or "escalated"
- Frontend: Displays customer response and internal notes

---

## Technical Details (for debugging)

### What Changed in the Fix

1. **Faster Index Loading** (orchestrator_simple.py):
   - Now loads pre-built index in <5s
   - Fails immediately if index missing (no 5-minute rebuild attempt)
   - Added timing metrics to startup logs

2. **Better Error Reporting** (main.py):
   - Startup now logs all environment variables
   - Health endpoint reports "unhealthy" if initialization fails
   - Detailed error messages in logs

3. **Deployment Config** (render.yaml):
   - Added `--timeout-keep-alive 300` to uvicorn
   - Build command verifies index exists
   - Explicit timeout values set

### Architecture Flow

```
Frontend (Vercel)
    ↓ POST /api/tickets
API Gateway (Render - Node.js)
    ↓ POST /api/resolve-ticket (360s timeout)
AI Service (Render - FastAPI)
    ↓ Load FAISS index (5s)
    ↓ Embed query (Gemini API)
    ↓ Semantic search (FAISS)
    ↓ Generate response (Groq API)
    ↓ Return resolution
API Gateway
    ↓ Save to MongoDB
    ↓ Return to Frontend
```

### Key Metrics to Monitor

- **Index load time**: Should be <5s (was 3-5 minutes)
- **Embedding time**: 200-500ms per request
- **LLM time**: 1-3s per request (Groq is fast)
- **Total latency**: 3-5s end-to-end

---

Last Updated: 2026-10-14
