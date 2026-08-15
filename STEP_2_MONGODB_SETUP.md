# Step 2: Setup MongoDB 🗄️

Choose **ONE** of the two options below:

---

## 📋 Option A: MongoDB Atlas (Cloud - RECOMMENDED ⭐)

### Why Choose This?
✅ No installation needed  
✅ Free 512MB storage forever  
✅ Works on any computer  
✅ Perfect for production  
✅ Takes 5 minutes  

### Instructions:

#### 2A.1: Go to MongoDB Atlas

```
Open: https://www.mongodb.com/cloud/atlas
```

#### 2A.2: Sign Up (Create Account)

1. Click **"Create Free Account"**
2. Sign up with:
   - Email address, OR
   - Google account, OR
   - GitHub account
3. Verify your email
4. Answer setup questions (basic info)

#### 2A.3: Create FREE Cluster

1. Click **"Create"** or **"Build a Database"**
2. Select **"M0 Sandbox"** (FREE tier - 512MB)
3. Choose cloud provider:
   - AWS (default, fine)
   - Or any you prefer
4. Choose region closest to you
5. Name it: `resolveai` (or any name)
6. Click **"Create"**

⏱️ **Wait 1-2 minutes** for cluster to be created

#### 2A.4: Allow Network Access

Your cluster is created. Now we need to allow connections:

1. Go to **"Network Access"** in left sidebar
2. Click **"Add IP Address"** button
3. Click **"Allow Access from Anywhere"** (select 0.0.0.0/0)
4. Click **"Confirm"**

⚠️ **Note:** For development/testing this is fine. For production, whitelist specific IPs.

#### 2A.5: Create Database User

1. Go to **"Database Access"** in left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Username: `resolveai`
5. Password: Create a strong password (save it!)
   - Example: `MySecure123!Pass`
6. Set privileges: **"Read and write to any database"**
7. Click **"Add User"**

#### 2A.6: Get Connection String

This is the most important part!

1. Click **"Connect"** button on your cluster
2. Select **"Connect your application"**
3. Choose:
   - Driver: **Node.js**
   - Version: **5.5 or later**
4. You'll see a connection string like:
   ```
   mongodb+srv://resolveai:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
5. **Copy this entire string**
6. Replace `PASSWORD` with your actual password
7. Change `/?retryWrites` to `/resolveai?retryWrites` to add database name

**Final connection string should look like:**
```
mongodb+srv://resolveai:MySecure123!Pass@cluster0.abc123.mongodb.net/resolveai?retryWrites=true&w=majority
```

✅ **Save this! You'll need it in Step 3!**

---

## 💻 Option B: Local MongoDB (Your Computer)

### Why Choose This?
✅ No cloud account needed  
✅ Works offline  
✅ Fastest for local development  
⚠️ Harder to use in production  

### Instructions:

#### 2B.1: Check if MongoDB is Installed

```bash
mongod --version
```

If you see a version number, MongoDB is installed! Skip to 2B.3.

If you see "command not found", continue to 2B.2.

#### 2B.2: Install MongoDB

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y mongodb
```

**On macOS (with Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
```

**On Windows:**
- Download from: https://www.mongodb.com/try/download/community
- Run installer
- Follow prompts

#### 2B.3: Create Data Directory

```bash
# Create data directory
mkdir -p ~/data/db

# Make sure you have permission
chmod 755 ~/data/db
```

#### 2B.4: Connection String

For local MongoDB, your connection string is:
```
mongodb://localhost:27017/resolveai
```

✅ **Save this! You'll need it in Step 3!**

---

## 🎯 Decision Time

### Choose ONE:

**Choose MongoDB Atlas if:**
- ✅ You prefer cloud database
- ✅ You want it to work everywhere
- ✅ You plan to deploy to production
- ✅ You don't want to install anything

**Choose Local MongoDB if:**
- ✅ You don't want to sign up for accounts
- ✅ You prefer everything on your computer
- ✅ You're only testing locally

---

## ✅ Step 2 Checklist

After choosing your option:

**For MongoDB Atlas:**
- [ ] Created MongoDB Atlas account
- [ ] Created M0 Sandbox cluster
- [ ] Allowed network access (0.0.0.0/0)
- [ ] Created database user (resolveai)
- [ ] Got connection string
- [ ] Saved connection string

**For Local MongoDB:**
- [ ] Installed MongoDB (or confirmed installed)
- [ ] Created ~/data/db directory
- [ ] Have connection string: `mongodb://localhost:27017/resolveai`

---

## 📝 Save Your Connection String

You'll need this in Step 3. Save it in a text file:

**If using Atlas:**
```
mongodb+srv://resolveai:YOUR_PASSWORD@cluster.mongodb.net/resolveai?retryWrites=true&w=majority
```

**If using Local:**
```
mongodb://localhost:27017/resolveai
```

---

## 🚀 Next Step

When you have your connection string saved, we'll move to **Step 3: Configure .env Files**

Let me know when you're ready! ✅

---

## ❓ Troubleshooting

### Atlas: "Can't create cluster"
- Check your email verification
- Try refreshing the page
- Try again in a few minutes

### Atlas: "Connection timeout"
- Make sure you whitelisted 0.0.0.0/0
- Check your username/password is correct

### Local: "mongod command not found"
- MongoDB not installed correctly
- Try reinstalling
- Or use MongoDB Atlas instead

### Local: "Permission denied on ~/data/db"
- Run: `sudo chown -R $USER ~/data/db`

---

**Ready? Tell me which option you chose and I'll help with Step 3!** 👇
