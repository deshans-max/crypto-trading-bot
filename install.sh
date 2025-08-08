#!/bin/bash

# Crypto Swing Trading Bot Installation Script
# This script sets up the environment for the trading bot

echo "🚀 Installing Crypto Swing Trading Bot..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env_example.txt .env
    echo "⚠️  Please edit .env file with your Kraken API credentials"
    echo "   - KRAKEN_API_KEY=your_api_key_here"
    echo "   - KRAKEN_SECRET_KEY=your_secret_key_here"
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x main.py
chmod +x dashboard.py

# Create logs directory
mkdir -p logs

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Kraken API credentials"
echo "2. Test the setup: python main.py --test"
echo "3. Start the bot: python main.py --start"
echo "4. Monitor with dashboard: python dashboard.py"
echo ""
echo "⚠️  IMPORTANT: Only trade with funds you can afford to lose!"
echo "   Cryptocurrency trading involves significant risk."
echo ""
echo "📚 For more information, see README.md"
