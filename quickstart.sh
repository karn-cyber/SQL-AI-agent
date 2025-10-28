#!/bin/bash

# SQL AI Agent Quick Start Script
echo "🚀 SQL AI Agent - Quick Start"
echo "=============================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Install requirements
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Setup environment
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env with your credentials"
else
    echo "✅ .env file exists"
fi

# Test setup
echo "🧪 Testing setup..."
python3 test_connection.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env file with your credentials"
echo "  2. streamlit run streamlit_app.py  # Web interface"
echo "  3. python3 cli.py                 # Command line"
echo ""
