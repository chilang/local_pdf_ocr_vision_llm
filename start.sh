#!/bin/bash

# PDF OCR Vision LLM - Startup Script
# This script starts the Streamlit application

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PDF OCR with Local Vision LLM${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    uv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not found. Installing...${NC}"
    uv pip install streamlit pdf2image mlx-vlm pillow ipykernel matplotlib torch torchvision
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Check for poppler (required by pdf2image)
if ! command -v pdftoppm &> /dev/null; then
    echo -e "${YELLOW}Warning: poppler-utils not found${NC}"
    echo -e "${YELLOW}PDF conversion requires poppler. Install with:${NC}"
    echo -e "${YELLOW}  brew install poppler${NC}"
    echo ""
fi

echo -e "${GREEN}✓ Environment ready${NC}"
echo ""
echo -e "${BLUE}Starting Streamlit app...${NC}"
echo -e "${BLUE}The app will open in your browser automatically${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

# Start Streamlit
streamlit run app.py
