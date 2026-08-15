#!/bin/bash

# ResolveAI Setup Script
# This script sets up the development environment for all three services

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         ResolveAI Development Environment Setup          ║"
echo "║    MERN Stack + FastAPI Microservices Architecture       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print colored message
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.12+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    print_error "npm not found. Please install npm"
    exit 1
fi

# Check Docker (optional)
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    print_success "Docker $DOCKER_VERSION found (optional)"
    HAS_DOCKER=true
else
    print_warning "Docker not found (optional, but recommended)"
    HAS_DOCKER=false
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Setup AI Service
print_status "Setting up AI Service (FastAPI + Python)..."
cd ai-service

if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit ai-service/.env and add your OPENAI_API_KEY"
fi

print_status "Creating Python virtual environment..."
python3 -m venv venv

print_status "Activating virtual environment..."
source venv/bin/activate || . venv/bin/activate

print_status "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

print_success "AI Service setup complete!"
echo ""

cd ..

# Setup API Gateway
print_status "Setting up API Gateway (Express + Node.js)..."
cd web-api

if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit web-api/.env and configure MONGODB_URI"
fi

print_status "Installing Node.js dependencies..."
npm install --silent

print_success "API Gateway setup complete!"
echo ""

cd ..

# Setup Frontend
print_status "Setting up Frontend (React + Vite)..."
cd client

if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
fi

print_status "Installing Node.js dependencies..."
npm install --silent

print_success "Frontend setup complete!"
echo ""

cd ..

# Summary
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Configure environment variables:"
echo "   ${YELLOW}• ai-service/.env${NC} - Add your OPENAI_API_KEY"
echo "   ${YELLOW}• web-api/.env${NC} - Configure MONGODB_URI"
echo ""
echo "2️⃣  Build FAISS index (required for AI service):"
echo "   ${BLUE}cd ai-service${NC}"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo "   ${BLUE}python build_index.py${NC}"
echo ""
echo "3️⃣  Start services:"
echo ""

if [ "$HAS_DOCKER" = true ]; then
    echo "   ${GREEN}Option A: Docker Compose (Recommended)${NC}"
    echo "   ${BLUE}docker-compose up -d${NC}"
    echo ""
fi

echo "   ${GREEN}Option B: Manual (3 terminals)${NC}"
echo ""
echo "   Terminal 1 - AI Service:"
echo "   ${BLUE}cd ai-service && source venv/bin/activate && uvicorn main:app --reload --port 8000${NC}"
echo ""
echo "   Terminal 2 - API Gateway:"
echo "   ${BLUE}cd web-api && npm run dev${NC}"
echo ""
echo "   Terminal 3 - Frontend:"
echo "   ${BLUE}cd client && npm run dev${NC}"
echo ""
echo "4️⃣  Open your browser:"
echo "   ${BLUE}http://localhost:3000${NC}"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "   • README_NEW.md - Project overview and quick start"
echo "   • DEPLOYMENT.md - Production deployment guide"
echo "   • API_SPEC.md - Complete API documentation"
echo "   • SYSTEM_DESIGN.md - Architecture deep dive"
echo ""
echo "🎓 For resume bullets and interview prep, see README_NEW.md"
echo ""
echo "Happy coding! 🚀"
echo ""
