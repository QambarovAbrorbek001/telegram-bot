#!/bin/bash
# Automated installation script for Telegram Anonymous Bot (Linux/Mac)

set -e  # Exit on error

clear

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Telegram Anonymous Messages Bot - Auto Installer        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.10+ using:"
    echo "  Mac (with Homebrew): brew install python3"
    echo "  Linux (Ubuntu/Debian): sudo apt-get install python3"
    echo "  Linux (Fedora): sudo dnf install python3"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ ERROR: pip is not available"
    echo ""
    echo "Please install pip using:"
    echo "  Mac: brew install python3"
    echo "  Linux (Ubuntu/Debian): sudo apt-get install python3-pip"
    echo "  Linux (Fedora): sudo dnf install python3-pip"
    echo ""
    exit 1
fi
echo "✅ pip is available"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Could not create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Could not activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies (this may take a minute)..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Could not install dependencies"
    echo "Please check requirements.txt and try again manually:"
    echo "  pip install -r requirements.txt"
    exit 1
fi
echo "✅ Dependencies installed successfully"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Telegram Bot Configuration
# Get your token from @BotFather on Telegram

TELEGRAM_BOT_TOKEN=your_bot_token_here
EOF
    echo "✅ .env file created"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Display next steps
clear
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Installation Complete! 🎉                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Python environment ready"
echo "✅ Virtual environment created"
echo "✅ Dependencies installed"
echo "✅ .env file created"
echo ""
echo ""
echo "┌────────────────────────────────────────────────────────────────┐"
echo "│ NEXT STEPS:                                                    │"
echo "├────────────────────────────────────────────────────────────────┤"
echo "│                                                                │"
echo "│ 1. GET YOUR BOT TOKEN:                                         │"
echo "│    - Open Telegram and search: @BotFather                     │"
echo "│    - Send: /newbot                                             │"
echo "│    - Follow the prompts                                        │"
echo "│    - Copy your bot token                                       │"
echo "│                                                                │"
echo "│ 2. CONFIGURE THE BOT:                                          │"
echo "│    - Open .env file:  nano .env                               │"
echo "│    - Replace \"your_bot_token_here\" with your actual token   │"
echo "│    - Save the file (Ctrl+O, Enter, Ctrl+X)                   │"
echo "│                                                                │"
echo "│ 3. RUN THE BOT:                                                │"
echo "│    - Execute: bash run_bot.sh                                 │"
echo "│    - Or manually: python3 main.py                             │"
echo "│                                                                │"
echo "│ 4. TEST IN TELEGRAM:                                           │"
echo "│    - Search for your bot                                       │"
echo "│    - Click /start                                              │"
echo "│    - Share your personal link with friends!                   │"
echo "│                                                                │"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""
echo "For detailed instructions, see: SETUP_GUIDE.md"
echo "Quick start guide: QUICKSTART.md"
echo "Full documentation: README.md"
echo ""
echo ""
echo "Press Enter to finish..."
read
