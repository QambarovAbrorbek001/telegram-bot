#!/bin/bash
# Telegram Anonymous Bot Startup Script for Linux/Mac

echo "====================================="
echo "Telegram Anonymous Messages Bot"
echo "====================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Could not create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
python3 -c "import aiogram" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Could not install dependencies"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "==================== SETUP REQUIRED ===================="
    echo "ERROR: .env file not found!"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Copy .env.example to .env:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edit .env and replace 'your_bot_token_here' with your actual bot token"
    echo ""
    echo "3. Get your bot token from @BotFather on Telegram"
    echo ""
    echo "Then run this script again."
    echo "======================================================"
    echo ""
    exit 1
fi

# Check if bot token is configured
if grep -q "your_bot_token_here" .env; then
    echo ""
    echo "ERROR: Bot token is not configured!"
    echo "Please edit .env and replace 'your_bot_token_here' with your actual token"
    echo ""
    exit 1
fi

# Start the bot
echo ""
echo "Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""
python3 main.py
