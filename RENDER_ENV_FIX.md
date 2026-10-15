# URGENT: Fix Render Environment Variables

## The Problem

Your AI service is failing because the environment variables don't match what the code expects.

## Required Fixes in Render Dashboard

### Service: `resolve-ai-service` (AI Service)

Go to: Render Dashboard → `resolve-ai-service` → Environment → Edit

**Fix these variables:**

1. ❌ **EMBEDDING_MODEL** 
   - Current: `sentence-transformers/all-MiniLM-L6-v2`
   - **Change to**: `gemini-embedding-001`
   - Reason: FAISS index was built with Gemini embeddings

2. ❌ **GROQ_MODEL**
   - Current: `llama-3.3-70b-versatile`
   - **Change to**: `openai/gpt-oss-120b`
   - Reason: This is the model you're using in local .env

3. ✅ **Add missing variables** (if not present):
   ```
   SIMILARITY_THRESHOLD=0.65
   RETRIEVER_K=3
   DEBUG_MODE=false
   ```

### Service: `resolveai-api-gateway` (API Gateway)

Go to: Render Dashboard → `resolveai-api-gateway` → Environment

**Verify these are correct:**

1. ✅ **AI_SERVICE_URL**
   - Should be: `https://resolve-ai-service.onrender.com`
   - Currently shows: `https://resolve-ai-service.onrender.com` ✓

2. ✅ **MONGODB_URI**
   - Should start with: `mongodb+srv://jangidyash1259_db_user:...`
   - Appears to be set ✓

3. ✅ **FRONTEND_URL**
   - Should be: `https://resolve-ai-frontend.vercel.app` or `https://your-frontend-url.vercel.app`
   - Currently: Needs verification

## Step-by-Step Fix Instructions

### Step 1: Fix AI Service Environment
1. Go to https://dashboard.render.com
2. Click on `resolve-ai-service`
3. Click "Environment" in left sidebar
4. Click "Edit" button
5. Find `EMBEDDING_MODEL` and change value to: `gemini-embedding-001`
6. Find `GROQ_MODEL` and change value to: `openai/gpt-oss-120b`
7. Click "Save Changes"
8. Service will automatically redeploy (takes 3-5 minutes)

### Step 2: Monitor Deployment
1. Go to "Logs" tab
2. Wait for these messages:
   ```
   Building...
   Starting...
   Loading pre-built FAISS index...
   ✓ Loaded 228 policy vectors in 0.XX s
   Service Ready!
   ```

### Step 3: Test
Once deployed (5 minutes), test at:
https://resolve-ai-frontend.vercel.app/

## Why This Fixes It

**Current State:**
```
AI Service env: EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
Code expects: gemini-embedding-001
FAISS index: Built with gemini-embedding-001 (768 dims)
Result: ❌ Dimension mismatch → Service fails to start
```

**After Fix:**
```
AI Service env: EMBEDDING_MODEL=gemini-embedding-001
Code expects: gemini-embedding-001
FAISS index: Built with gemini-embedding-001 (768 dims)
Result: ✓ Perfect match → Service starts in 5 seconds
```

## Complete Environment Variable Reference

### resolve-ai-service (AI Service)
```bash
# LLM Configuration
GROQ_API_KEY=<your-groq-key>                    # ✓ Already set
GROQ_MODEL=openai/gpt-oss-120b                  # ❌ FIX THIS

# Embeddings Configuration
GEMINI_API_KEY=<your-gemini-key>                # ✓ Already set
EMBEDDING_MODEL=gemini-embedding-001            # ❌ FIX THIS (currently wrong)

# Vector Store Configuration
VECTOR_STORE_PATH=./faiss_store                 # ✓ Already set
RETRIEVER_K=3                                   # ⚠️ Add if missing
SIMILARITY_THRESHOLD=0.65                       # ⚠️ Add if missing

# Python Configuration
PYTHON_VERSION=3.12.0                           # ✓ Already set

# Debug
DEBUG_MODE=false                                # ⚠️ Add if missing
```

### resolveai-api-gateway (API Gateway)
```bash
# Service URLs
AI_SERVICE_URL=https://resolve-ai-service.onrender.com        # ✓ Verify
FRONTEND_URL=https://resolve-ai-frontend.vercel.app           # ✓ Verify

# Database
MONGODB_URI=mongodb+srv://jangidyash...                       # ✓ Already set

# Server
NODE_ENV=production                             # ✓ Already set
PORT=5000                                       # ✓ Already set
```

## After Fixing

1. **Wait 5 minutes** for redeployment
2. **Check logs** for "Service Ready!"
3. **Test health**: Visit https://resolve-ai-service.onrender.com/health
   - Should return: `{"status":"healthy","faiss_initialized":true}`
4. **Test frontend**: Submit a ticket at your Vercel URL
   - Should work without "Failed to process" error

## If Still Not Working

If the fix doesn't work after deployment:

1. **Check exact error in logs:**
   - Dashboard → resolve-ai-service → Logs
   - Look for the first error message after "Starting..."

2. **Verify FAISS index exists:**
   - Logs should show: "Loading pre-built FAISS index..."
   - If it says "Building from scratch..." → Problem with git deployment

3. **Test API keys:**
   - Groq: https://console.groq.com/keys
   - Gemini: https://aistudio.google.com/apikey

4. **Verify model names:**
   ```bash
   # Test Groq model exists
   curl https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer YOUR_GROQ_KEY" | grep gpt-oss-120b
   ```

## Timeline

- **Environment update**: Instant
- **Redeploy trigger**: Automatic
- **Build time**: 2-3 minutes
- **Service start**: 10-15 seconds
- **Total**: ~5 minutes from save to working

---

**CRITICAL**: The main issue is `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2` 
This must be changed to `gemini-embedding-001` for the service to start.

**Last Updated**: 2026-10-14 23:30 IST
