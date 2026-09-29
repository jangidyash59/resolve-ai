# 🔧 Quick Fix - MongoDB Connection Error

## Problem
```
MongoDB connection error: ENOTFOUND _mongodb._tcp.resolveai-cluster.nvwry4v.mongodb.net
```

## Solution: Set MongoDB URI in Render

### Step 1: Get MongoDB Atlas Connection String

1. Go to https://cloud.mongodb.com/
2. Click "Database" → Your Cluster → "Connect"
3. Choose "Connect your application"
4. Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/resolveai?retryWrites=true&w=majority
   ```
5. **Replace `<password>` with your actual password**
6. **Replace `<username>` if needed**

### Step 2: Add to Render Environment

1. Go to: https://dashboard.render.com/
2. Click on `resolveai-api-gateway` service
3. Go to "Environment" tab
4. Find `MONGODB_URI` or click "Add Environment Variable"
5. Paste your connection string from Step 1
6. Click "Save Changes"

**This will trigger an automatic redeploy** ✓

### Step 3: Verify

After redeploy (2-3 minutes), check logs:
- Should see: `✓ Connected to MongoDB`
- No more `ENOTFOUND` errors

## Alternative: Use Free MongoDB Atlas

If you don't have MongoDB Atlas:

1. Visit: https://cloud.mongodb.com/
2. Sign up (free)
3. Create free cluster (M0 - FREE tier)
4. Create database user (username + password)
5. Add IP: `0.0.0.0/0` (allow all - for Render)
6. Get connection string
7. Add to Render as above

**Takes 5 minutes to setup!**
