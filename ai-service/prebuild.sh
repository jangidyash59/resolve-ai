#!/bin/bash
# Pre-build FAISS index before deployment to avoid timeout issues

echo "=================================================="
echo "  Pre-building FAISS Index for Deployment"
echo "=================================================="

# Check if index already exists
if [ -f "faiss_store/index.faiss" ] && [ -f "faiss_store/metadata.json" ]; then
    echo "✓ FAISS index already exists. Skipping build."
    echo "  Location: faiss_store/"
    echo "  To rebuild, delete the faiss_store directory first."
    exit 0
fi

# Check for required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set"
    echo "   Please set it in .env file or environment"
    exit 1
fi

echo ""
echo "Starting index build..."
echo "This will take 3-5 minutes for 228 policy chunks."
echo ""

# Run the build script
python build_index.py

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "  ✓ Index Pre-built Successfully!"
    echo "=================================================="
    echo "Files created:"
    ls -lh faiss_store/
    echo ""
    echo "Next steps:"
    echo "  1. Commit faiss_store/ to git"
    echo "  2. Push to GitHub"
    echo "  3. Render deployment will use pre-built index"
    echo "  4. Startup time reduced from 5 min to 5 seconds"
else
    echo ""
    echo "=================================================="
    echo "  ❌ Index Build Failed"
    echo "=================================================="
    echo "Check error messages above and:"
    echo "  1. Verify GEMINI_API_KEY is correct"
    echo "  2. Check internet connection"
    echo "  3. Check API quota at: https://aistudio.google.com/"
    exit 1
fi
