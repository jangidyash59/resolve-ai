# ⚡ Quick Start - Get Running in 5 Minutes

## 🎯 Goal
Get ResolveAI running locally with all 3 services.

---

## 📋 Prerequisites Check

Run these commands to verify you have everything:

```bash
python3 --version    # Should be 3.12+
node --version       # Should be 18+
npm --version        # Should be installed
```

---

## 🚀 Easy Start (Automated)

### Option 1: One-Command Start (Recommended)

```bash
cd /home/jangidworld/Desktop/resolve-ai
./start-services.sh
```

This will:
1. Check environment files
2. Build FAISS index if needed
3. Open 3 terminal windows automatically
4. Start all services

**Then open:** http://localhost:3000

---

## 🔧 Manual Start (If automated doesn't work)

### Step 1: Create Environment Files (Once)

```bash
cd /home/jangidworld/Desktop/resolve-ai

# Create env files
cp ai-service/.env.example ai-service/.env
cp web-api/.env.example web-api/.env
cp client/.env.example client/.env
```

### Step 2: Add Your OpenAI API Key

```bash
nano ai-service/.env
```

Change this line:
```env
OPENAI_API_KEY=your_key_here
```

To:
```env
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Configure MongoDB

```bash
nano web-api/.env
```

**For local MongoDB:**
```env
MONGODB_URI=mongodb://localhost:27017/resolveai
```

**For MongoDB Atlas (Free Cloud):**
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/resolveai
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## 🎬 Start Services (3 Terminals)

Open 3 terminal windows and run:

### Terminal 1️⃣ : AI Service

```bash
cd /home/jangidworld/Desktop/resolve-ai/ai-service

# Create virtual environment (first time only)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages (first time only)
pip install -r requirements.txt

# Build FAISS index (first time only)
python build_index.py

# Start server
uvicorn main:app --reload --port 8000
```

**✅ Success:** You'll see "Application startup complete"

**Test:** http://localhost:8000/health

---

### Terminal 2️⃣ : API Gateway

```bash
cd /home/jangidworld/Desktop/resolve-ai/web-api

# Install packages (first time only)
npm install

# Start server
npm run dev
```

**✅ Success:** You'll see "🚀 ResolveAI API Gateway"

**Test:** http://localhost:5000/health

---

### Terminal 3️⃣ : Frontend

```bash
cd /home/jangidworld/Desktop/resolve-ai/client

# Install packages (first time only)
npm install

# Start server
npm run dev
```

**✅ Success:** You'll see "Local: http://localhost:3000"

**Test:** http://localhost:3000

---

## 🎉 Use the Application

1. **Open browser:** http://localhost:3000
2. **Fill form** (or use default values)
3. **Click "Submit Ticket"**
4. **Wait ~30 seconds** (AI processing)
5. **See AI response** with citations!

---

## 🐛 Common Issues & Fixes

### "Network Error" when submitting ticket

**Cause:** Services not running

**Fix:**
```bash
# Check if services are running
curl http://localhost:8000/health  # AI Service
curl http://localhost:5000/health  # API Gateway

# If not running, start them in separate terminals
```

---

### "OPENAI_API_KEY not found"

**Cause:** API key not configured

**Fix:**
```bash
# Edit the file
nano ai-service/.env

# Add: OPENAI_API_KEY=sk-proj-xxxxx

# Restart Terminal 1 (AI Service)
```

---

### "MongoDB connection failed"

**Cause:** MongoDB not running

**Fix Option 1 - Local MongoDB:**
```bash
# Start MongoDB
mongod --dbpath ~/data/db

# In another terminal, start web-api
```

**Fix Option 2 - Use MongoDB Atlas (Easier):**
1. Go to https://mongodb.com/cloud/atlas
2. Create FREE account
3. Create FREE cluster (M0)
4. Get connection string
5. Update `web-api/.env`

---

### "Port already in use"

**Cause:** Port occupied by another process

**Fix:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

---

### "FAISS index not found"

**Cause:** Index not built

**Fix:**
```bash
cd ai-service
source venv/bin/activate
python build_index.py
```

---

## 📊 Verify Everything Works

### Check Services Status:

```bash
# AI Service (should return {"status": "healthy"})
curl http://localhost:8000/health

# API Gateway (should return {"status": "OK"})
curl http://localhost:5000/health

# Frontend (should load a webpage)
# Open: http://localhost:3000
```

### Test API Directly:

```bash
# Submit a test ticket
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "customer_tier": "bronze",
    "ticket_text": "My package was damaged"
  }'
```

---

## 🛑 Stop Services

In each terminal, press:
```
Ctrl + C
```

---

## 🔄 Restart Services

Just run the start commands again in each terminal.

No need to reinstall packages or rebuild index!

---

## 📚 Next Steps

Once running successfully:

1. ✅ Try different ticket scenarios
2. ✅ Check the Dashboard (http://localhost:3000/dashboard)
3. ✅ Read API_SPEC.md for API details
4. ✅ Read DEPLOYMENT.md to deploy to cloud

---

## 🎓 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | User interface |
| Dashboard | http://localhost:3000/dashboard | Admin panel |
| API Gateway | http://localhost:5000 | REST API |
| API Health | http://localhost:5000/health | Check status |
| AI Service | http://localhost:8000 | AI processing |
| AI Health | http://localhost:8000/health | Check status |
| API Docs | http://localhost:8000/docs | FastAPI docs |

---

## ✅ Success Checklist

Before submitting a ticket, ensure:

- [ ] Terminal 1: "Application startup complete"
- [ ] Terminal 2: "Connected to MongoDB"
- [ ] Terminal 3: "Local: http://localhost:3000"
- [ ] http://localhost:8000/health works
- [ ] http://localhost:5000/health works
- [ ] http://localhost:3000 loads

---

**🎉 That's it! You're ready to go!**

For detailed documentation, see:
- **START_HERE.md** - Comprehensive guide
- **README.md** - Full project documentation
- **DEPLOYMENT.md** - Deploy to production
