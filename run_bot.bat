@echo off
REM Telegram Anonymous Bot Startup Script for Windows

echo =====================================
echo Telegram Anonymous Messages Bot
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Could not create virtual environment
        echo Make sure Python 3.10+ is installed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
pip show aiogram >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Could not install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ==================== SETUP REQUIRED ====================
    echo ERROR: .env file not found!
    echo.
    echo Please follow these steps:
    echo.
    echo 1. Open .env.example and copy its contents
    echo 2. Create a new file named .env and paste the contents
    echo 3. Replace "your_bot_token_here" with your actual bot token
    echo 4. Get your bot token from @BotFather on Telegram
    echo.
    echo Then run this script again.
    echo ======================================================
    echo.
    pause
    exit /b 1
)

REM Check if bot token is set
findstr /m "your_bot_token_here" .env >nul
if not errorlevel 1 (
    echo.
    echo ERROR: Bot token is not configured!
    echo Please edit .env and replace "your_bot_token_here" with your actual token
    echo.
    pause
    exit /b 1
)

REM Start the bot
echo.
echo Starting bot...
echo Press Ctrl+C to stop the bot
echo.
python main.py

pause
