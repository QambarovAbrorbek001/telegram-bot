"""
Telegram Anonim Bot - Konfiguratsiya moduli
"""

import os
import sys
from dotenv import load_dotenv

# .env fayldan o'zgaruvchilarni yuklash
load_dotenv()

# ============================================================
# XAVFSIZLIK: Token faqat .env dan o'qiladi
# ============================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token_here":
    print("❌ XATO: TELEGRAM_BOT_TOKEN .env faylda sozlanmagan!")
    print("   .env faylga quyidagini qo'shing:")
    print("   TELEGRAM_BOT_TOKEN=your_token_here")
    sys.exit(1)

# ============================================================
# ADMIN PANEL — bir nechta admin ID qo'shish mumkin
# ============================================================
# .env da: ADMIN_IDS=123456789,987654321
_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip().isdigit()
]

# ============================================================
# Ma'lumotlar bazasi
# ============================================================
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")

# ============================================================
# Rate limiting (spam himoyasi)
# ============================================================
RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
RATE_LIMIT_SECONDS  = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

# ============================================================
# Xabar sozlamalari
# ============================================================
MAX_MESSAGE_LENGTH = 4096   # Telegram limiti
BLOCK_LIST_FILE = "blocked_users.json"