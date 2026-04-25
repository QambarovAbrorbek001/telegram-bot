@echo off
REM Automated installation script for Telegram Anonymous Bot
REM Run this script first to set everything up automatically

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       Telegram Anonymous Messages Bot - Auto Installer        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: pip is not available
    echo Please reinstall Python with pip support
    pause
    exit /b 1
)
echo ✅ pip is available
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Could not create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: Could not activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies (this may take a minute)...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Could not install dependencies
    echo Please check requirements.txt and try again manually:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    (
        echo # Telegram Bot Configuration
        echo # Get your token from @BotFather on Telegram
        echo.
        echo TELEGRAM_BOT_TOKEN=your_bot_token_here
    ) > .env
    echo ✅ .env file created
    echo.
) else (
    echo ✅ .env file already exists
    echo.
)

REM Display next steps
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              Installation Complete! 🎉                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo ✅ Python environment ready
echo ✅ Virtual environment created
echo ✅ Dependencies installed
echo ✅ .env file created
echo.
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ NEXT STEPS:                                                    │
echo ├────────────────────────────────────────────────────────────────┤
echo │                                                                │
echo │ 1. GET YOUR BOT TOKEN:                                         │
echo │    - Open Telegram and search: @BotFather                     │
echo │    - Send: /newbot                                             │
echo │    - Follow the prompts                                        │
echo │    - Copy your bot token                                       │
echo │                                                                │
echo │ 2. CONFIGURE THE BOT:                                          │
echo │    - Open .env file:  notepad .env                            │
echo │    - Replace "your_bot_token_here" with your actual token    │
echo │    - Save the file                                             │
echo │                                                                │
echo │ 3. RUN THE BOT:                                                │
echo │    - Execute: run_bot.bat                                     │
echo │    - Or manually: python main.py                              │
echo │                                                                │
echo │ 4. TEST IN TELEGRAM:                                           │
echo │    - Search for your bot                                       │
echo │    - Click /start                                              │
echo │    - Share your personal link with friends!                   │
echo │                                                                │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo For detailed instructions, see: SETUP_GUIDE.md
echo Quick start guide: QUICKSTART.md
echo Full documentation: README.md
echo.
echo.
pause
