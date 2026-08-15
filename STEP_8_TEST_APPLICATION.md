# Step 8: Test the Application Locally 🧪

All services are running! Now let's test the complete end-to-end flow with Grok API.

---

## 🎯 Testing Overview

You'll test:
1. ✅ Frontend loads correctly
2. ✅ Submit a support ticket
3. ✅ AI processes with Grok API
4. ✅ FAISS retrieves policies
5. ✅ Database saves ticket
6. ✅ AI provides resolution

---

## 🚀 Test 1: Access Frontend

### Step 1A: Open Browser

```
Open: http://localhost:5173
```

You should see:
- ResolveAI ticket submission form
- Input fields: Title, Description, Customer Tier
- Submit button

### Step 1B: Verify UI Components

Check that you can see:
- ✅ Ticket title input field
- ✅ Ticket description textarea
- ✅ Customer tier dropdown (Standard/Premium/VIP)
- ✅ Submit button
- ✅ Clear button

---

## 🎫 Test 2: Submit a Support Ticket

### Step 2A: Fill in the Form

```
Title: "Damaged item received - order #12345"

Description: "I received my order today but the product 
arrived damaged. The packaging was also torn. I would 
like to get a replacement or refund."

Customer Tier: "Standard"
```

### Step 2B: Click Submit

Click the **"Submit"** button and wait...

**Expected behavior:**
- Button becomes disabled (shows loading state)
- Submit button text changes to "Processing..."
- You should see logs in the terminal

---

## ⏳ Wait for Processing

The ticket will be processed through the entire pipeline:

1. **Frontend** → Sends to API Gateway
2. **Express API** → Validates and saves to MongoDB
3. **Express API** → Forwards to AI Service
4. **AI Service** → 
   - Retrieves relevant policies (FAISS search)
   - Sends to Grok API for analysis
   - Generates resolution
5. **Express API** → Updates MongoDB
6. **Frontend** → Displays response

**Time to complete:** 10-30 seconds (depends on Grok API response time)

---

## ✅ Test 3: Verify Response

After processing, you should see:

### On Frontend:
```
✓ Resolution message from AI
✓ Recommended actions
✓ Policy references
✓ Ticket status: "resolved"
```

### Example Response:
```
"Based on our returns policy, we can offer you:

Option 1: Full refund (process within 5-7 business days)
Option 2: Replacement shipping (expedited at no extra cost)

Please reference your ticket ID for tracking."
```

### In MongoDB:
```
{
  _id: ObjectId(...),
  title: "Damaged item received...",
  description: "I received my order today...",
  status: "resolved",
  resolution: "Based on our returns policy...",
  createdAt: 2026-08-14T...,
  ticketId: "ticket_xxx"
}
```

---

## 🔍 Test 4: Check Logs

### AI Service Log (FastAPI)
Watch the terminal for:
```
INFO: POST /api/resolve
INFO: Retrieving policies...
INFO: Grok API call initiated
INFO: Resolution generated
INFO: Response 200 OK
```

### API Gateway Log (Express)
Watch the terminal for:
```
✓ Ticket received: Damaged item received...
✓ Forwarding to AI service
✓ Ticket updated with resolution
✓ Response sent to client
```

### Frontend Log (React/Vite)
Watch browser console for:
```
✓ Ticket submitted
✓ Response received
✓ UI updated
```

---

## 📊 Test 5: Verify Database

### Option A: Check MongoDB Atlas UI
1. Go to https://cloud.mongodb.com
2. Login to your account
3. Select cluster "resolveai-cluster"
4. Go to Collections
5. Select database "resolveai"
6. View "tickets" collection
7. Should see your submitted ticket

### Option B: Query via MongoDB Shell
```bash
mongosh "your-mongodb-connection-string"

use resolveai
db.tickets.find().pretty()
```

---

## 🎬 Full Test Scenario

### Scenario: Customer wants refund for defective product

**1. Submit Ticket:**
- Title: "Device not charging - needs replacement"
- Description: "Purchased laptop 3 days ago. Battery doesn't charge. Still under warranty."
- Tier: "Premium"

**2. Watch Processing:**
- FAISS retrieves: warranty_policy.md, returns_refunds.md
- Grok analyzes: "This is within warranty, eligible for replacement"
- Database saves resolution

**3. Expected Resolution:**
```
"Your device is covered under our 1-year warranty. 
We'll send a replacement unit immediately with 
prepaid shipping for the defective unit. 
Estimated delivery: 2-3 business days."
```

---

## ⚠️ Troubleshooting

### Issue: "Cannot reach server" (ERR_CONNECTION_REFUSED)

**Cause:** Services not running
**Fix:** 
```bash
# Check if services are running
ps aux | grep -E "uvicorn|npm"

# Restart services if needed
cd ai-service && source venv/bin/activate && uvicorn main:app --reload --port 8000
cd web-api && npm run dev
cd client && npm run dev
```

### Issue: "Cannot find Grok API key"

**Cause:** GROK_API_KEY not set in ai-service/.env
**Fix:**
```bash
# Edit ai-service/.env
cat ai-service/.env | grep GROK_API_KEY

# Should show: GROK_API_KEY=xai-xxxxx...
```

### Issue: "MongoDB connection error"

**Cause:** MONGODB_URI incorrect
**Fix:**
```bash
# Check connection string
cat web-api/.env | grep MONGODB_URI

# Test connection manually
mongosh "your-connection-string"
```

### Issue: "Frontend loads but buttons don't work"

**Cause:** API Gateway not responding
**Fix:**
```bash
# Check API Gateway logs
# Terminal running web-api should show connection logs

# Test API manually
curl http://localhost:5000/health
```

### Issue: "AI service responds but no resolution text"

**Cause:** Grok API rate limit or key issue
**Fix:**
1. Check Grok API key in ai-service/.env
2. Verify at console.x.ai that key is active
3. Wait 1 minute and try again
4. Check AI service logs for errors

---

## 📈 Expected Performance

- **Frontend Load:** < 2 seconds
- **API Response:** 5-15 seconds (Grok API latency)
- **Database Save:** < 1 second
- **Total End-to-End:** 10-30 seconds

---

## ✨ Success Criteria

✅ Frontend loads without errors  
✅ Can submit a ticket form  
✅ AI processes the ticket  
✅ See AI-generated resolution  
✅ Ticket saved to MongoDB  
✅ No errors in any service logs  

---

## 🎯 Next Steps

After successful local testing:

**Step 9:** Deploy AI Service to Render  
**Step 10:** Deploy API Gateway to Render  
**Step 11:** Deploy Frontend to Vercel  
**Step 12:** Test production deployment  

---

## 💡 Tips

1. **Keep terminals visible** - Watch logs in real-time
2. **Browser DevTools** - Press F12 to see console logs
3. **Test multiple tickets** - Try different scenarios
4. **Check MongoDB** - Verify data is persisting
5. **Monitor services** - Watch for errors or warnings

---

## ✅ Ready to Test!

Open http://localhost:5173 and submit a test ticket!

**Let me know when testing is complete!** ✨

