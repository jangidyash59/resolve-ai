# 🚀 How to Get Your FREE Grok API Key

Grok API (by xAI) is **completely FREE** with generous rate limits! Perfect for this project.

---

## ⚡ Quick Steps (2 minutes)

### Step 1: Sign Up for xAI Console

1. Go to: **https://console.x.ai**
2. Click **"Sign Up"** or **"Sign In"**
3. You can sign in with:
   - Google account
   - GitHub account
   - Email address

### Step 2: Generate API Key

1. Once logged in, you'll see the xAI Console dashboard
2. Click on **"API Keys"** in the left sidebar
3. Click **"Create New Key"** button
4. Give it a name (e.g., "ResolveAI")
5. Click **"Generate"**
6. **Copy your API key** (starts with `xai-...`)

⚠️ **Important:** Save your key immediately! You won't be able to see it again.

### Step 3: Add to Your Project

```bash
cd /home/jangidworld/Desktop/resolve-ai
nano ai-service/.env
```

Add your key:
```env
GROK_API_KEY=xai-your-actual-key-here
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## 🎯 Why Grok API?

| Feature | Grok (xAI) | OpenAI |
|---------|------------|--------|
| **Cost** | 🟢 **FREE** | 🟡 Paid (after trial) |
| **Rate Limits** | 🟢 **Very Generous** | 🟡 Limited on free tier |
| **Speed** | 🟢 **Fast** | 🟢 Fast |
| **Quality** | 🟢 **Excellent** | 🟢 Excellent |
| **Sign Up** | 🟢 **Easy** | 🟢 Easy |

---

## 🆓 Free Tier Limits (Grok)

Grok offers generous free tier:
- **100+ requests per minute**
- **No credit card required**
- **No expiration date**
- **Perfect for development & demos**

---

## 🔑 What About Embeddings?

**Grok doesn't have embedding models yet**, so we still use OpenAI's embedding API for the FAISS vector search.

You have 2 options:

### Option 1: Use OpenAI Free Trial (Recommended)

1. Go to: https://platform.openai.com
2. Sign up for free account
3. Get **$5 free credits** (no credit card needed)
4. Copy your API key
5. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

**Note:** Embeddings are very cheap (~$0.0001 per request). $5 = ~50,000 requests!

### Option 2: Use Alternative Embedding API (Future)

When Grok releases embeddings, we'll update the code. For now, OpenAI embeddings work great!

---

## 📝 Complete .env File Example

```env
# Grok API (xAI) - FREE and Main LLM
GROK_API_KEY=xai-your-actual-key-here
GROK_MODEL=grok-beta

# OpenAI API - Only for embeddings (very cheap)
OPENAI_API_KEY=sk-proj-your-openai-key-here
EMBEDDING_MODEL=text-embedding-3-small

# Vector Store Config
VECTOR_STORE_PATH=./faiss_store
RETRIEVER_K=3
MINIMUM_POLICY_SIMILARITY=0.25
DEBUG_MODE=false
```

---

## 🧪 Test Your API Key

After adding your key, test it:

```bash
cd ai-service
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Test Grok API
grok_client = OpenAI(
    api_key=os.getenv('GROK_API_KEY'),
    base_url='https://api.x.ai/v1'
)

response = grok_client.chat.completions.create(
    model='grok-beta',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)

print('✓ Grok API works!')
print(f'Response: {response.choices[0].message.content}')
"
```

Expected output:
```
✓ Grok API works!
Response: Hello! How can I help you today?
```

---

## 🐛 Troubleshooting

### Error: "API key not found"

**Problem:** Key not set in .env file

**Solution:**
```bash
nano ai-service/.env
# Add: GROK_API_KEY=xai-your-key
# Save and restart service
```

### Error: "Invalid API key"

**Problem:** Wrong key or typo

**Solution:**
1. Go back to https://console.x.ai
2. Create a new API key
3. Copy it carefully
4. Update `.env` file

### Error: "Rate limit exceeded"

**Problem:** Too many requests (rare on free tier)

**Solution:**
- Wait a minute
- Free tier has very high limits, this should be rare

---

## 💡 Pro Tips

1. **Don't share your API key** - Keep it secret!
2. **Use .gitignore** - Never commit `.env` files
3. **Regenerate if exposed** - Create new key if accidentally shared
4. **Monitor usage** - Check xAI console for usage stats

---

## 🔗 Useful Links

- **xAI Console:** https://console.x.ai
- **Grok API Docs:** https://docs.x.ai
- **OpenAI Platform:** https://platform.openai.com
- **Get Help:** File an issue on GitHub

---

## 📊 Cost Comparison

### Total Cost for This Project:

**Using Grok (Recommended):**
- Grok API: **$0/month** (FREE)
- OpenAI Embeddings: **~$0.01/month** (100 requests)
- **Total: ~$0.01/month** 🎉

**Using Only OpenAI:**
- OpenAI API: **~$5-10/month** (100 requests/day)
- **Total: ~$5-10/month**

**💰 Savings: 99.9% by using Grok!**

---

## ✅ Ready to Go!

Once you have:
- [x] Grok API key added to `ai-service/.env`
- [x] OpenAI key added (for embeddings)
- [x] Tested the connection

You're ready to run the application!

```bash
cd /home/jangidworld/Desktop/resolve-ai
./start-services.sh
```

---

**🎉 Enjoy your FREE, fast AI-powered support system!**

Made with ❤️ using Grok AI (xAI)
