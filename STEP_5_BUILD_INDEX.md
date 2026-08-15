# Step 5: Build FAISS Vector Index 📊

After Step 4 (Python dependencies) completes, you'll build the FAISS vector store from the policy documents.

---

## 🎯 What This Does

The FAISS index:
- ✅ Reads all policy files from `data/policies/`
- ✅ Chunks them into smaller pieces (for better retrieval)
- ✅ Converts chunks to embeddings using HuggingFace (FREE, local)
- ✅ Stores them in FAISS (local vector database)
- ✅ Creates `ai-service/faiss_store/` with the index

**Result:** Your AI can now retrieve relevant policies instantly! 🚀

---

## 📋 Step 5 Instructions

### 5A: Ensure .env is Configured

Make sure `ai-service/.env` has your **Grok API key**:

```bash
cat ai-service/.env | grep GROK_API_KEY
```

It should show: `GROK_API_KEY=xai-xxxxxx...`

### 5B: Run the Build Script

```bash
cd ai-service
source venv/bin/activate
python build_index.py
```

### 5C: Wait for Completion

The script will:
1. Load policies from `data/policies/` ✅
2. Show progress: "Loading 13 policy files..."
3. Chunk documents ✅
4. Embed chunks (first time takes 2-5 min for HuggingFace to download model)
5. Build FAISS index ✅
6. Save to `./faiss_store/`

**Expected output:**
```
✅ Loading 13 policy files from data/policies/
✅ Total documents loaded: 13
✅ Chunking documents...
✅ Building FAISS vector index from XXX chunks...
✅ FAISS index built with XXX vectors
✅ Vector store saved to ./faiss_store/
✅ Index successfully built and saved!
```

---

## ✅ What You'll See

After successful completion:

```bash
ls -la ai-service/faiss_store/
```

Should show:
- `index.faiss` - The vector index (~10-50MB)
- `index.pkl` - Index metadata

---

## ⏱️ Time Estimate

- **First run:** 5-10 minutes (HuggingFace downloads embedding model)
- **Subsequent runs:** 2-3 minutes

---

## ❌ If It Fails

### "ModuleNotFoundError: No module named 'sentence_transformers'"
- Make sure Step 4 completed successfully
- Check: `source venv/bin/activate && python -c "import sentence_transformers"`

### "FAISS Error"
- Delete old index: `rm -rf ai-service/faiss_store/`
- Run again: `python build_index.py`

### "No policies found"
- Check policies exist: `ls -la data/policies/`
- Should have `.md` files

---

## 🚀 Next Steps

After Step 5 completes successfully:

**Step 6:** Install Node.js dependencies (npm install)
**Step 7:** Start local services
**Step 8:** Test the application

---

## ✨ Ready!

When Step 4 (Python dependencies) finishes and you see no errors, run:

```bash
cd /home/jangidworld/Desktop/resolve-ai/ai-service
source venv/bin/activate
python build_index.py
```

**Tell me when the index is built!** ✅
