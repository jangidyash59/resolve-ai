#!/bin/bash

# ResolveAI - Start All Services Script
# This script helps you start all services in one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         ResolveAI - Starting All Services                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if .env files exist
echo -e "${BLUE}[1/4]${NC} Checking environment files..."

if [ ! -f "ai-service/.env" ]; then
    echo -e "${YELLOW}⚠ Creating ai-service/.env from template${NC}"
    cp ai-service/.env.example ai-service/.env
    echo -e "${RED}✗ Please edit ai-service/.env and add your OPENAI_API_KEY${NC}"
    exit 1
fi

if [ ! -f "web-api/.env" ]; then
    echo -e "${YELLOW}⚠ Creating web-api/.env from template${NC}"
    cp web-api/.env.example web-api/.env
    echo -e "${RED}✗ Please edit web-api/.env and configure MONGODB_URI${NC}"
    exit 1
fi

if [ ! -f "client/.env" ]; then
    echo -e "${YELLOW}⚠ Creating client/.env from template${NC}"
    cp client/.env.example client/.env
fi

echo -e "${GREEN}✓ Environment files ready${NC}"
echo ""

# Check if OpenAI key is set
echo -e "${BLUE}[2/4]${NC} Checking OpenAI API key..."
if grep -q "sk-proj-" ai-service/.env || grep -q "sk-" ai-service/.env; then
    echo -e "${GREEN}✓ OpenAI API key found${NC}"
else
    echo -e "${RED}✗ OpenAI API key not configured${NC}"
    echo -e "${YELLOW}Please edit ai-service/.env and add your OPENAI_API_KEY${NC}"
    exit 1
fi

echo ""

# Check if FAISS index exists
echo -e "${BLUE}[3/4]${NC} Checking FAISS index..."
if [ ! -d "ai-service/faiss_store" ]; then
    echo -e "${YELLOW}⚠ FAISS index not found. Building it now...${NC}"
    echo -e "${YELLOW}This will take ~30 seconds${NC}"
    cd ai-service
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -q -r requirements.txt
    python build_index.py
    cd ..
    echo -e "${GREEN}✓ FAISS index built successfully${NC}"
else
    echo -e "${GREEN}✓ FAISS index found${NC}"
fi

echo ""
echo -e "${BLUE}[4/4]${NC} Starting services..."
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}IMPORTANT: This will open 3 new terminal windows${NC}"
echo -e "${YELLOW}Keep all terminals open while using the application${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo ""

# Get the absolute path
BASEDIR=$(pwd)

# Function to start services in new terminal
start_service() {
    local service_name=$1
    local command=$2
    
    # Try gnome-terminal first
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="ResolveAI - $service_name" -- bash -c "$command; exec bash"
    # Try xterm
    elif command -v xterm &> /dev/null; then
        xterm -title "ResolveAI - $service_name" -e "$command; bash" &
    # Try konsole (KDE)
    elif command -v konsole &> /dev/null; then
        konsole --title "ResolveAI - $service_name" -e "$command; bash" &
    else
        echo -e "${RED}✗ Could not find a suitable terminal emulator${NC}"
        echo -e "${YELLOW}Please run these commands manually in 3 separate terminals:${NC}"
        echo ""
        echo -e "${BLUE}Terminal 1:${NC}"
        echo "$command"
        echo ""
        return 1
    fi
}

echo -e "${GREEN}Starting AI Service (FastAPI)...${NC}"
start_service "AI Service" "cd '$BASEDIR/ai-service' && source venv/bin/activate && echo '╔══════════════════════════════════════╗' && echo '║   AI Service (FastAPI + FAISS)       ║' && echo '║   http://localhost:8000              ║' && echo '╚══════════════════════════════════════╝' && echo '' && uvicorn main:app --reload --port 8000"

sleep 2

echo -e "${GREEN}Starting API Gateway (Express)...${NC}"
start_service "API Gateway" "cd '$BASEDIR/web-api' && echo '╔══════════════════════════════════════╗' && echo '║   API Gateway (Express + MongoDB)    ║' && echo '║   http://localhost:5000              ║' && echo '╚══════════════════════════════════════╝' && echo '' && npm run dev"

sleep 2

echo -e "${GREEN}Starting Frontend (React)...${NC}"
start_service "Frontend" "cd '$BASEDIR/client' && echo '╔══════════════════════════════════════╗' && echo '║   React Frontend (Vite)              ║' && echo '║   http://localhost:3000              ║' && echo '╚══════════════════════════════════════╝' && echo '' && npm run dev"

sleep 3

echo ""
echo -e "${GREEN}✓ All services started!${NC}"
echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 ResolveAI is now running!${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${YELLOW}Frontend:${NC}    http://localhost:3000"
echo -e "  ${YELLOW}API Gateway:${NC} http://localhost:5000"
echo -e "  ${YELLOW}AI Service:${NC}  http://localhost:8000"
echo ""
echo -e "${YELLOW}📝 Tips:${NC}"
echo -e "  • Wait 10-15 seconds for all services to start"
echo -e "  • Keep all terminal windows open"
echo -e "  • Open http://localhost:3000 in your browser"
echo -e "  • Submit a ticket and wait ~30 seconds for AI response"
echo ""
echo -e "${YELLOW}⚠ To stop all services:${NC}"
echo -e "  • Press Ctrl+C in each terminal window"
echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════${NC}"
echo ""
