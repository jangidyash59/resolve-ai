# Step 3: Create and Configure .env Files 🔐

Now we'll create the actual `.env` files using your Grok API key and MongoDB connection string.

You need to have:
- ✅ Grok API key from console.x.ai
- ✅ MongoDB connection string from Step 2

---

## 📍 Three .env Files to Configure

The project has **3 services**, each needs its own `.env` file:

1. **ai-service/.env** - FastAPI (Grok + FAISS)
2. **web-api/.env** - Express API Gateway (MongoDB)
3. **client/.env** - React Frontend (API endpoint)

---

## 🔧 File 1: ai-service/.env

This file configures the AI service with your **FREE Grok API key**.

**Create file:** `ai-service/.env`

```env
# ═══════════════════════════════════════════════════════════════════
# 100% FREE - Only Grok API (xAI)
# ═══════════════════════════════════════════════════════════════════

GROK_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROK_MODEL=grok-beta

# ═══════════════════════════════════════════════════════════════════
# Embeddings: FREE local HuggingFace (no API cost)
# ═══════════════════════════════════════════════════════════════════

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ═══════════════════════════════════════════════════════════════════
# Vector Store Configuration
# ═══════════════════════════════════════════════════════════════════

VECTOR_STORE_PATH=./faiss_store
CHUNK_SIZE=800
CHUNK_OVERLAP=200
RETRIEVER_K=3
MINIMUM_POLICY_SIMILARITY=0.25
DEBUG_MODE=false
```

### ⚠️ IMPORTANT: Replace `GROK_API_KEY`

Your Grok API key looks like: `xai-xxxxxxxxxxxxxxxxxxxxxxxxxx...`

Replace the placeholder with your **actual Grok API key** from console.x.ai.

---

## 🔧 File 2: web-api/.env

This file configures the Express API gateway with your **MongoDB connection string**.

**Create file:** `web-api/.env`

```env
# Server Configuration
PORT=5000
NODE_ENV=development

# MongoDB Connection - REPLACE WITH YOUR CONNECTION STRING
MONGODB_URI=mongodb://localhost:27017/resolveai

# AI Service URL (local development)
AI_SERVICE_URL=http://localhost:8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### ⚠️ IMPORTANT: Replace `MONGODB_URI`

**If you chose MongoDB Atlas:**
```
MONGODB_URI=mongodb+srv://resolveai:YOUR_PASSWORD@cluster.mongodb.net/resolveai?retryWrites=true&w=majority
```

**If you chose Local MongoDB:**
```
MONGODB_URI=mongodb://localhost:27017/resolveai
```

---

## 🔧 File 3: client/.env

This file configures the React frontend to connect to your API gateway.

**Create file:** `client/.env`

```env
# API Gateway URL (local development)
VITE_API_URL=http://localhost:5000
```

This stays the same for local development.

---

## ✅ Step 3 Checklist

After creating all three files:

- [ ] Created `ai-service/.env` with your Grok API key
- [ ] Created `web-api/.env` with your MongoDB connection string
- [ ] Created `client/.env` with API URL
- [ ] All three files are in the correct directories
- [ ] All sensitive values are replaced (GROK_API_KEY, MONGODB_URI)

---

## 📂 Verify File Locations

Your project should look like this:

```
resolve-ai/
├── ai-service/
│   ├── .env ✅ (newly created)
│   ├── .env.example
│   ├── requirements.txt
│   └── main.py
├── web-api/
│   ├── .env ✅ (newly created)
│   ├── .env.example
│   ├── server.js
│   └── package.json
├── client/
│   ├── .env ✅ (newly created)
│   ├── .env.example
│   ├── package.json
│   └── src/
```

---

## 🚀 Next Steps After Configuration

Once you've created all three `.env` files:

**Step 4:** Install Python dependencies
**Step 5:** Build FAISS vector index
**Step 6:** Install Node.js dependencies
**Step 7:** Start local services
**Step 8:** Test the application

---

## ❓ Common Issues

### "GROK_API_KEY not found"
- Make sure `GROK_API_KEY=xai-...` is in `ai-service/.env`
- Check for typos in the key
- Make sure the file is named exactly `.env` (not `.env.txt`)

### "MongoDB connection failed"
- Check your connection string in `web-api/.env`
- If using Atlas: verify username, password, and cluster name
- If using Local: make sure MongoDB is running
- Try connecting manually first: `mongosh "your-connection-string"`

### "API request fails"
- Make sure `VITE_API_URL` in `client/.env` matches your Express port
- Make sure `AI_SERVICE_URL` in `web-api/.env` matches your FastAPI port

---

## ✨ You're Ready!

**Tell me when you've created all three `.env` files, and we'll move to Step 4!** ✅

