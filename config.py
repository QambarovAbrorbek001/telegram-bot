"""
Configuration module for the Telegram Anonymous Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token - Get from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")

# Database configuration
DATABASE_PATH = "bot_database.db"

# Rate limiting configuration (messages per minute per user)
RATE_LIMIT_MESSAGES = 10  # Maximum 10 messages per minute
RATE_LIMIT_SECONDS = 60   # Per 60 seconds (1 minute)

# Anti-spam configuration
MAX_MESSAGE_LENGTH = 4096  # Telegram limit
BLOCK_LIST_FILE = "blocked_users.json"

# Bot configuration
BOT_USERNAME = "YourBotUsername"  # Update after creating the bot
