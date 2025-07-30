#!/bin/bash

# VersionOne MCP Server Installation Script
# This script helps set up the VersionOne MCP server with all dependencies

set -e

echo "🚀 VersionOne MCP Server Installation"
echo "====================================="

# Check if Python 3.8+ is available
echo "🔍 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "✅ Found Python $PYTHON_VERSION"
    
    # Check if version is 3.8 or higher
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo "✅ Python version is compatible"
    else
        echo "❌ Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if uv is available
echo "🔍 Checking uv availability..."
if command -v uv &> /dev/null; then
    echo "✅ Found uv"
else
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    if command -v uv &> /dev/null; then
        echo "✅ uv installed successfully"
    else
        echo "❌ Failed to install uv. Please install manually from https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
if [ -f "pyproject.toml" ]; then
    uv sync
    echo "✅ Dependencies installed successfully"
else
    echo "❌ pyproject.toml not found. Please run this script from the versionone-mcp-server directory."
    exit 1
fi

# Create environment file if it doesn't exist
echo "🔧 Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f "env-template.txt" ]; then
        cp env-template.txt .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please edit .env file with your VersionOne configuration:"
        echo "   - VERSIONONE_BASE_URL"
        echo "   - VERSIONONE_ACCESS_TOKEN"
    else
        echo "❌ env-template.txt not found"
    fi
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
echo "🔑 Setting script permissions..."
chmod +x test_client.py 2>/dev/null || true

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit the .env file with your VersionOne configuration:"
echo "   nano .env"
echo ""
echo "2. Test your configuration:"
echo "   uv run test_client.py"
echo ""
echo "3. Start the MCP server:"
echo "   uv run server stdio"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "🔗 VersionOne API documentation: https://versionone.github.io/api-docs/" 