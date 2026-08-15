# 🚀 Quick Start Guide - ResolveAI

Follow these steps to run the application locally.

---

## ⚠️ Prerequisites

Before starting, make sure you have:
- ✅ Python 3.12+
- ✅ Node.js 18+
- ✅ MongoDB (local or Atlas connection string)
- ✅ OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

---

## 🔧 Step 1: Environment Setup (5 minutes)

### 1.1 Create Environment Files

Run this command to create all .env files:

```bash
cd /home/jangidworld/Desktop/resolve-ai

# Create environment files from templates
cp ai-service/.env.example ai-service/.env
cp web-api/.env.example web-api/.env
cp client/.env.example client/.env
```

### 1.2 Configure AI Service

Edit `ai-service/.env`:
```bash
nano ai-service/.env
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=./faiss_store
RETRIEVER_K=3
MINIMUM_POLICY_SIMILARITY=0.25
DEBUG_MODE=false
```

**Press Ctrl+X, then Y, then Enter to save**

### 1.3 Configure API Gateway

Edit `web-api/.env`:
```bash
nano web-api/.env
```

For local MongoDB:
```env
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://localhost:27017/resolveai
AI_SERVICE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

OR for MongoDB Atlas (recommended):
```env
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/resolveai?retryWrites=true&w=majority
AI_SERVICE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

**Press Ctrl+X, then Y, then Enter to save**

### 1.4 Configure Frontend

Edit `client/.env`:
```bash
nano client/.env
```

```env
VITE_API_URL=http://localhost:5000
```

**Press Ctrl+X, then Y, then Enter to save**

---

## 🗄️ Step 2: MongoDB Setup (2 options)

### Option A: Local MongoDB (If installed)

```bash
# Start MongoDB
mongod --dbpath ~/data/db
```

Keep this terminal open.

### Option B: MongoDB Atlas (Recommended - FREE)

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up / Login
3. Create a FREE cluster (M0)
4. Create database user (username + password)
5. Whitelist IP: 0.0.0.0/0 (allow from anywhere)
6. Get connection string and update `web-api/.env`

---

## 🚀 Step 3: Start All Services (3 terminals)

### Terminal 1: AI Service (FastAPI)

```bash
cd /home/jangidworld/Desktop/resolve-ai/ai-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build FAISS index (REQUIRED - only run once)
python build_index.py

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

**✅ Success message:** "Application startup complete"

**Test:** Open http://localhost:8000/health

---

### Terminal 2: API Gateway (Express)

```bash
cd /home/jangidworld/Desktop/resolve-ai/web-api

# Install dependencies
npm install

# Start Express server
npm run dev
```

**✅ Success message:** "🚀 ResolveAI API Gateway"

**Test:** Open http://localhost:5000/health

---

### Terminal 3: Frontend (React)

```bash
cd /home/jangidworld/Desktop/resolve-ai/client

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

**✅ Success message:** "Local: http://localhost:3000"

**Test:** Open http://localhost:3000

---

## 🧪 Step 4: Test the Application

1. **Open browser:** http://localhost:3000
2. **Fill the form** with default values (already populated)
3. **Click "Submit Ticket"**
4. **Wait ~30 seconds** for AI processing
5. **See the result** with AI response and citations!

---

## 🐛 Troubleshooting

### Error: "Network Error" when submitting ticket

**Problem:** Services not running or wrong URLs

**Solution:**
1. Check all 3 terminals are running
2. Verify URLs in `.env` files
3. Test health endpoints:
   - http://localhost:8000/health (AI Service)
   - http://localhost:5000/health (API Gateway)

### Error: "OPENAI_API_KEY not found"

**Problem:** API key not set

**Solution:**
```bash
# Edit the file
nano ai-service/.env

# Add your key
OPENAI_API_KEY=sk-proj-xxxxx

# Restart Terminal 1 (AI Service)
```

### Error: "MongoDB connection failed"

**Problem:** MongoDB not running or wrong connection string

**Solution:**

For Local MongoDB:
```bash
# Make sure MongoDB is running
mongod --dbpath ~/data/db
```

For MongoDB Atlas:
```bash
# Verify connection string in web-api/.env
# Format: mongodb+srv://user:pass@cluster.mongodb.net/resolveai
```

### Error: "Port already in use"

**Problem:** Port 3000, 5000, or 8000 already occupied

**Solution:**
```bash
# Find and kill process on port
lsof -ti:5000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Error: "Module not found"

**Problem:** Dependencies not installed

**Solution:**
```bash
# AI Service
cd ai-service
pip install -r requirements.txt

# API Gateway
cd web-api
npm install

# Frontend
cd client
npm install
```

---

## 📊 What You Should See

### Terminal 1 (AI Service) Output:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 (API Gateway) Output:
```
🚀 ResolveAI API Gateway
Server: http://localhost:5000
✓ Connected to MongoDB
```

### Terminal 3 (Frontend) Output:
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:3000/
```

### Browser (http://localhost:3000):
You should see:
- Modern dark UI with glassmorphic design
- "ResolveAI" logo in navigation
- Form to submit support tickets
- Dashboard link in navigation

---

## 🎯 Quick Commands Reference

### Stop All Services
```bash
# Press Ctrl+C in each terminal
```

### Restart Services
```bash
# Just run the start commands again in each terminal
```

### Reset Everything
```bash
cd /home/jangidworld/Desktop/resolve-ai

# Clear all node_modules
rm -rf web-api/node_modules client/node_modules

# Clear Python virtual environment
rm -rf ai-service/venv

# Reinstall everything
cd ai-service && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../web-api && npm install
cd ../client && npm install
```

---

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | User interface |
| **API Gateway** | http://localhost:5000 | REST API |
| **AI Service** | http://localhost:8000 | AI processing |
| **API Docs** | http://localhost:8000/docs | FastAPI documentation |

---

## 📝 Example API Test (Optional)

Test API directly with curl:

```bash
# Test AI Service
curl http://localhost:8000/health

# Test API Gateway
curl http://localhost:5000/health

# Submit test ticket via API
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "customer_tier": "silver",
    "ticket_text": "My package was damaged"
  }'
```

---

## ✅ Success Checklist

Before submitting a ticket, verify:

- [ ] Terminal 1 shows "Application startup complete"
- [ ] Terminal 2 shows "Connected to MongoDB"
- [ ] Terminal 3 shows "Local: http://localhost:3000"
- [ ] http://localhost:8000/health returns `{"status": "healthy"}`
- [ ] http://localhost:5000/health returns `{"status": "OK"}`
- [ ] http://localhost:3000 loads the interface

---

## 🎓 Next Steps

Once everything is running:

1. ✅ Submit a test ticket
2. ✅ View results in Dashboard
3. ✅ Check the comprehensive documentation in README.md
4. ✅ Deploy to production using DEPLOYMENT.md

---

## 📞 Need Help?

- **Documentation:** See README.md for complete project overview
- **API Docs:** See API_SPEC.md for endpoint details
- **Deployment:** See DEPLOYMENT.md for cloud deployment

---

**Made with ❤️ - Happy Coding! 🚀**
