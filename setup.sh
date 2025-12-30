#!/bin/bash

# Enterprise RAG Frontend + Backend Startup Script
# Run this to start both servers with one command

echo "=================================================="
echo "Enterprise RAG - Starting Both Servers"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "enterprise-rag" ] || [ ! -d "enterprise-rag-frontend" ]; then
    echo -e "${RED}Error: Must be run from team_P1 directory${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking Python dependencies...${NC}"
cd enterprise-rag

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Installing Flask dependencies...${NC}"
    pip install flask flask-cors
fi

echo -e "${GREEN}✓ Python dependencies ready${NC}"
echo ""

echo -e "${YELLOW}Step 2: Checking Node.js dependencies...${NC}"
cd ../enterprise-rag-frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies (this may take a minute)...${NC}"
    npm install
fi

echo -e "${GREEN}✓ Node.js dependencies ready${NC}"
echo ""

echo "=================================================="
echo -e "${GREEN}Ready to start!${NC}"
echo "=================================================="
echo ""
echo "Open TWO terminal windows and run:"
echo ""
echo -e "${YELLOW}Terminal 1 (Backend):${NC}"
echo "  cd $(pwd)/../enterprise-rag"
echo "  python api_server.py"
echo ""
echo -e "${YELLOW}Terminal 2 (Frontend):${NC}"
echo "  cd $(pwd)"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "=================================================="
