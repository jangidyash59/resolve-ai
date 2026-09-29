#!/bin/bash

# ResolveAI Deployment Script
# This script prepares and deploys the project to Render and Vercel

set -e

echo "========================================"
echo "   ResolveAI Deployment Script"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${RED}✗ Git repository not initialized${NC}"
    echo "Run: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

echo -e "${GREEN}✓ Git repository found${NC}"

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠ You have uncommitted changes${NC}"
    echo "Commit your changes before deploying:"
    git status -s
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check required environment files
echo ""
echo "Checking environment files..."

if [ ! -f ai-service/.env ]; then
    echo -e "${RED}✗ ai-service/.env not found${NC}"
    echo "Copy from .env.example and configure"
    exit 1
fi

if [ ! -f web-api/.env ]; then
    echo -e "${RED}✗ web-api/.env not found${NC}"
    echo "Copy from .env.example and configure"
    exit 1
fi

if [ ! -f client/.env ]; then
    echo -e "${RED}✗ client/.env not found${NC}"
    echo "Copy from .env.example and configure"
    exit 1
fi

echo -e "${GREEN}✓ All .env files present${NC}"

# Check FAISS index
if [ ! -f ai-service/faiss_store/index.faiss ]; then
    echo -e "${YELLOW}⚠ FAISS index not found${NC}"
    echo "Building index..."
    cd ai-service
    python build_index.py
    cd ..
    echo -e "${GREEN}✓ FAISS index built${NC}"
else
    echo -e "${GREEN}✓ FAISS index found${NC}"
fi

echo ""
echo "========================================"
echo "   Ready to Deploy!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. BACKEND (Render):"
echo "   • Go to https://dashboard.render.com/"
echo "   • Connect your GitHub repository"
echo "   • Click 'New Blueprint Instance'"
echo "   • Select your repo (render.yaml will auto-configure)"
echo "   • Add environment variables:"
echo "     - GROQ_API_KEY (from your Groq account)"
echo "     - GEMINI_API_KEY (from Google AI Studio)"
echo "     - MONGODB_URI (from MongoDB Atlas)"
echo "     - FRONTEND_URL (will be Vercel URL)"
echo ""
echo "2. FRONTEND (Vercel):"
echo "   • Go to https://vercel.com/new"
echo "   • Import your GitHub repository"
echo "   • Framework: Vite"
echo "   • Root Directory: client"
echo "   • Build Command: npm run build"
echo "   • Output Directory: dist"
echo "   • Add environment variable:"
echo "     - VITE_API_URL=https://your-api-gateway.onrender.com"
echo ""
echo "3. UPDATE FRONTEND_URL in Render:"
echo "   • After Vercel deployment, copy your Vercel URL"
echo "   • Update FRONTEND_URL in both Render services"
echo ""
echo "========================================"
echo ""

# Offer to commit and push
read -p "Commit and push changes to GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit -m "Deployment ready: Updated configuration"
    
    # Check if remote exists
    if git remote | grep -q origin; then
        git push origin main || git push origin master
        echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
    else
        echo -e "${YELLOW}⚠ No remote repository configured${NC}"
        echo "Add remote: git remote add origin <your-repo-url>"
    fi
fi

echo ""
echo -e "${GREEN}✓ Deployment preparation complete!${NC}"
echo ""
