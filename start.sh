#!/bin/bash

# Quick Start Script for AI Knowledge Base + Chatbot

echo "=========================================="
echo "AI Knowledge Base + Chatbot - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python found: $(python --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ .env file not found. Creating from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠ IMPORTANT: Please edit .env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=sk-your-api-key-here"
    echo ""
    read -p "Press Enter to open .env file for editing (or Ctrl+C to exit)..."
    ${EDITOR:-nano} .env
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p data/chroma uploads static templates
echo "✓ Directories created"

# Start the application
echo ""
echo "=========================================="
echo "Starting the application..."
echo "=========================================="
echo ""
echo "The application will be available at:"
echo "  http://localhost:8000"
echo ""
echo "API documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
