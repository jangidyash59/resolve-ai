# Step 7: Start All Local Services 🚀

Now we'll start all three services: FastAPI (AI), Express (API Gateway), and React (Frontend).

---

## 📋 Prerequisites

Before starting, make sure:
- ✅ Step 6 complete (Node dependencies installed)
- ✅ `ai-service/.env` has GROK_API_KEY
- ✅ `web-api/.env` has MONGODB_URI
- ✅ FAISS index built (`ai-service/faiss_store/` exists)

---

## 🎯 Three Services to Start

| Service | Type | Port | Purpose |
|---------|------|------|---------|
| FastAPI | Python | 8000 | AI service (Grok + FAISS) |
| Express | Node.js | 5000 | API Gateway (MongoDB) |
| React | Vite | 3000 | Frontend (User interface) |

---

## 🚀 Option A: Automatic Start (Recommended)

If you have a terminal emulator (gnome-terminal, xterm, or konsole):

```bash
cd /home/jangidworld/Desktop/resolve-ai
bash start-services.sh
```

This will:
- ✅ Check .env files
- ✅ Build FAISS index if needed
- ✅ Open 3 terminal windows automatically
- ✅ Start all services in parallel

---

## 🚀 Option B: Manual Start (3 Separate Terminals)

### Terminal 1: AI Service (FastAPI)

```bash
cd /home/jangidworld/Desktop/resolve-ai/ai-service
source venv/bin/activate
uvicorn main:py --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: API Gateway (Express)

```bash
cd /home/jangidworld/Desktop/resolve-ai/web-api
npm run dev
```

**You should see:**
```
Server running on port 5000
✓ Connected to MongoDB
```

### Terminal 3: Frontend (React)

```bash
cd /home/jangidworld/Desktop/resolve-ai/client
npm run dev
```

**You should see:**
```
VITE v5.x.x ready in XXX ms

➜  Local:   http://localhost:3000/
```

---

## ⏱️ Startup Sequence

Services usually start in this order:
1. **AI Service** (5-10 seconds) - FastAPI loads FAISS index
2. **API Gateway** (3-5 seconds) - Express connects to MongoDB
3. **Frontend** (5-10 seconds) - React dev server starts

**Total time:** ~20-30 seconds for all services to be ready

---

## ✅ Verification

When all services are running, you'll see:

```
🎉 All Services Running:
  ✓ Frontend:    http://localhost:3000
  ✓ API Gateway: http://localhost:5000
  ✓ AI Service:  http://localhost:8000
```

Test each service:

```bash
# Test AI Service (FastAPI)
curl http://localhost:8000/docs

# Test API Gateway (Express)
curl http://localhost:5000/health

# Test Frontend
Open http://localhost:3000 in browser
```

---

## 📊 Service Health Checks

### AI Service (FastAPI)
- Endpoint: `http://localhost:8000/docs`
- Shows: Swagger UI with all API endpoints
- Status: "Application startup complete"

### API Gateway (Express)
- Endpoint: `http://localhost:5000/health`
- Response: JSON with status
- Check: MongoDB connection status

### Frontend (React)
- Endpoint: `http://localhost:3000`
- Shows: Ticket submission form
- Check: Can see UI with no errors in console

---

## ⚠️ Common Issues

### "Port already in use"
```bash
# Kill process on port (example: 3000)
lsof -i :3000
kill -9 <PID>
```

### "Cannot connect to MongoDB"
- Check MongoDB is running (local or Atlas accessible)
- Verify MONGODB_URI in `web-api/.env`
- Test connection: `mongosh "your-connection-string"`

### "GROK_API_KEY not found"
- Check `ai-service/.env` has GROK_API_KEY
- Verify it's the correct format: `xai-xxxxxx...`
- Make sure no extra spaces

### "FAISS index not found"
```bash
cd ai-service
source venv/bin/activate
python build_index.py
```

### "npm: command not found"
- Node.js not installed
- Install from: https://nodejs.org/

---

## 🛑 Stop All Services

To stop all services gracefully:

1. In each terminal window, press: **Ctrl+C**
2. Wait for service to shutdown (2-3 seconds)
3. Close terminal windows

---

## 📝 Next Step

**Step 8: Test the Application Locally**

Once all services are running:
1. Open http://localhost:3000
2. Submit a support ticket
3. Watch the AI process it with Grok API
4. See the resolution

---

## 🔍 Debugging

### View logs in real-time
Each terminal shows live logs as you use the app.

### Check database
```bash
mongosh "your-connection-string"
db.tickets.find()
```

### Test API manually
```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Test ticket","customer_tier":"standard"}'
```

---

## ✨ Ready?

Start the services using Option A or B, then move to **Step 8: Test the Application Locally**!

