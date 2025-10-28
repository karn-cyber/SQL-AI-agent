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
echo ""
echo "📦 Installing dependencies..."
echo "This may take a few minutes on first run..."
echo "----------------------------------------"
pip3 install -r requirements.txt
install_result=$?

echo "----------------------------------------"
if [ $install_result -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Error installing dependencies"
    echo "💡 Try: pip3 install --upgrade pip"
    exit 1
fi

# Setup environment
echo ""
echo "🔧 Setting up environment configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo ""
    echo "📝 IMPORTANT: Edit .env file with your credentials:"
    echo "   - Azure OpenAI API key, endpoint, deployment name"
    echo "   - PostgreSQL database connection details"
    echo ""
    echo "📄 .env file contains:"
    echo "----------------------------------------"
    head -10 .env | grep -E "^[A-Z_]+" || echo "Template variables ready for configuration"
    echo "----------------------------------------"
else
    echo "✅ .env file already exists"
    echo "📄 Current .env configuration:"
    echo "----------------------------------------"
    grep -E "^[A-Z_]+=" .env | sed 's/=.*/=***/' || echo "No variables configured yet"
    echo "----------------------------------------"
fi

# Test setup
echo "🧪 Testing setup..."
echo "Running connection tests..."
echo "----------------------------------------"
python3 test_connection.py
test_result=$?

echo ""
echo "----------------------------------------"

if [ $test_result -eq 0 ]; then
    echo "✅ Test completed successfully!"
else
    echo "⚠️  Test completed with warnings/errors"
    echo "💡 This is normal if you haven't configured .env yet"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env file with your credentials:"
echo "     nano .env"
echo ""
echo "  2. Test your configuration:"
echo "     python3 test_connection.py"
echo ""
echo "  3. Run the application:"
echo "     streamlit run streamlit_app.py  # Web interface"
echo "     python3 cli.py                 # Command line"
echo ""
echo "📚 For detailed setup instructions, see:"
echo "     README.md"
echo "     PRODUCTION_GUIDE.md"
echo ""
