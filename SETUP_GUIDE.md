# 🚀 Complete Setup Guide - Telegram Anonymous Bot

This guide walks you through every step needed to get the bot running.

## Prerequisites

- **Windows 10/11, Mac, or Linux**
- **Python 3.10 or higher** - [Download here](https://www.python.org/downloads/)
- **A Telegram account**
- **Internet connection**

---

## Step 1: Verify Python Installation

### Windows
```bash
# Open PowerShell and run:
python --version
```

Should show: `Python 3.10.x` or higher

If not installed or not found:
1. Download Python from https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check "Add Python to PATH"
3. Restart PowerShell/CMD after installation

### Mac/Linux
```bash
python3 --version
```

---

## Step 2: Create Bot on Telegram (@BotFather)

### Quick Steps:

1. **Open Telegram** and search for: **@BotFather**
2. **Start the bot** by clicking "Start"
3. **Send command**: `/newbot`
4. **Follow prompts**:
   - Bot name: `My Anonymous Bot` (or any name)
   - Bot username: `my_anon_bot_<numbers>` (must be unique)

5. **Copy the token** you receive (it looks like):
   ```
   123456789:ABCDefGhijKlmnOPqrstUVwxyz1234567890
   ```
   
   ⚠️ **KEEP THIS SAFE** - Don't share it with anyone!

### Example Response:
```
Done! Congratulations on your new bot. You will find it at t.me/my_anon_bot_12345.
You can now add a description, about section and profile picture for your bot.
See /help for a list of commands.

Use this token to access the HTTP API:
123456789:ABCDefGhijKlmnOPqrstUVwxyz1234567890
```

---

## Step 3: Download/Clone the Project

### Option A: Download as ZIP
1. Go to the project folder on your computer: `d:\projrcts\anonimbot\`
2. Files should already be there

### Option B: Download via Git
```bash
git clone https://github.com/yourusername/telegram-anon-bot.git
cd telegram-anon-bot
```

---

## Step 4: Create Virtual Environment

Virtual environment isolates bot dependencies from your system Python.

### Windows
```bash
cd d:\projrcts\anonimbot

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Mac/Linux
```bash
cd /path/to/anonimbot

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

---

## Step 5: Install Dependencies

With virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- `aiogram` - Telegram bot framework
- `SQLAlchemy` - Database ORM
- `python-dotenv` - Environment variable management

---

## Step 6: Configure Bot Token

### Windows
```bash
# Copy example file
copy .env.example .env

# Open .env in notepad
notepad .env
```

### Mac/Linux
```bash
# Copy example file
cp .env.example .env

# Open .env in your editor
nano .env
```

### Edit .env File

**Before:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**After:** (paste your actual token)
```
TELEGRAM_BOT_TOKEN=123456789:ABCDefGhijKlmnOPqrstUVwxyz1234567890
```

Save and close the file.

---

## Step 7: Test the Setup

Run a quick test to verify everything is configured:

```bash
python -c "from config import TELEGRAM_BOT_TOKEN; print('✅ Token loaded!' if TELEGRAM_BOT_TOKEN != 'your_bot_token_here' else '❌ Token not configured')"
```

Expected output:
```
✅ Token loaded!
```

If you see `❌ Token not configured`, go back to Step 6.

---

## Step 8: Start the Bot

### Option A: Run Python Script Directly
```bash
python main.py
```

### Option B: Use Startup Script (Recommended)

**Windows:**
```bash
run_bot.bat
```

**Mac/Linux:**
```bash
bash run_bot.sh
```

### Expected Output:
```
🤖 Anonymous Messages Bot Starting...
==================================================
Make sure your TELEGRAM_BOT_TOKEN is set in .env file
==================================================
```

If you see this, the bot is running! ✅

---

## Step 9: Test the Bot

### In Telegram:

1. **Open Telegram**
2. **Search for your bot** (e.g., `@my_anon_bot_12345`)
3. **Click "Start"**
4. **Expected response:**
   ```
   👋 Welcome to Anonymous Messages Bot!
   
   Your personal link:
   https://t.me/my_anon_bot_12345?start=YOUR_USER_ID
   
   Share this link with friends so they can send you anonymous messages!
   ```

5. **Test the features:**
   - Click "📬 My Link" - See your personal link
   - Click "👤 Profile" - View your profile
   - Click "⚙️ Settings" - Manage settings
   - Click "❓ Help" - Get help

### Congratulations! 🎉 Bot is running!

---

## Step 10: Keep Bot Running

### Option A: Local Development (Keep Terminal Open)
- Just keep the terminal window open
- Bot runs until you close it

### Option B: Background Process

**Windows (using Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "At startup"
4. Set action: `venv\Scripts\python.exe main.py`
5. Set "Run whether user is logged in or not"

**Mac/Linux (using systemd):**
```bash
# Create service file
sudo nano /etc/systemd/system/telegram-bot.service
```

Paste:
```ini
[Unit]
Description=Telegram Anonymous Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/path/to/anonimbot
ExecStart=/path/to/anonimbot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

---

## Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'aiogram'"

**Solution:**
```bash
# Make sure virtual environment is activated (check for (venv) prefix)
pip install -r requirements.txt
```

### Issue 2: "Invalid token" or bot doesn't respond

**Solution:**
1. Check `.env` file has correct token
2. Verify token from @BotFather (copy again if needed)
3. Make sure there are no extra spaces

### Issue 3: "Python not found" or "python: command not found"

**Solution:**
- Windows: Reinstall Python with "Add Python to PATH" checked
- Mac/Linux: Use `python3` instead of `python`

### Issue 4: Port/Connection errors

**Solution:**
- Check internet connection
- Disable firewall temporarily
- Try using VPN if in restricted country
- Telegram servers might be down (rare)

### Issue 5: Database locked error

**Solution:**
```bash
# Close all instances of the bot
# Delete bot_database.db
del bot_database.db  # Windows
# or
rm bot_database.db   # Mac/Linux
# Run bot again - new database will be created
```

### Issue 6: "No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

---

## File Structure Explained

```
anonimbot/
├── main.py                 # Main bot file (RUN THIS)
├── database.py             # Database management
├── config.py               # Configuration
├── admin.py                # Admin utilities
├── examples.py             # Usage examples
├── requirements.txt        # Dependencies list
├── .env                    # Your bot token (SECRET!)
├── .env.example            # Example config
├── .gitignore              # Git ignore rules
├── bot_database.db         # Database (auto-created)
├── run_bot.bat             # Windows startup script
├── run_bot.sh              # Linux/Mac startup script
├── README.md               # Full documentation
└── SETUP_GUIDE.md          # This file
```

---

## Next Steps

### Share Your Bot
1. Get your personal link from the bot
2. Share it with friends on:
   - WhatsApp, Instagram, Discord
   - Social media profiles
   - Group chats
3. They can click link and send you anonymous messages!

### Customize the Bot
Edit `config.py` to change:
- Rate limiting (messages per minute)
- Maximum message length
- Database path

Edit `main.py` to add:
- New commands
- Custom keyboards
- Additional features

### Add More Features
Suggested additions:
- Message expiration (auto-delete)
- Reactions/emojis to messages
- Admin moderation commands
- Statistics dashboard
- Message categories/tags

---

## Security Tips

⚠️ **IMPORTANT:**

1. **Never share your bot token** in code or online
2. **Keep `.env` file secret** - add to `.gitignore`
3. **Use HTTPS/TLS** if hosting on server
4. **Backup database regularly** (`bot_database.db`)
5. **Monitor bot logs** for suspicious activity
6. **Update dependencies** regularly:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Getting Help

### Check Logs
Bot prints debug information:
```
2024-04-25 10:30:45,123 - INFO - User 123456 started the bot
```

### Enable Debug Logging
Edit `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from INFO to DEBUG
```

### Common Resources
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Python SQLite](https://docs.python.org/3/library/sqlite3.html)

---

## Support

If you encounter issues:
1. Check this SETUP_GUIDE.md - Troubleshooting section
2. Check README.md - FAQ section
3. Review examples.py for usage examples
4. Check bot logs for error messages
5. Verify .env file configuration

---

## Success Checklist ✅

Before considering setup complete, verify:

- [ ] Python 3.10+ installed
- [ ] Bot token from @BotFather
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows aiogram)
- [ ] `.env` file created with bot token
- [ ] Bot runs without errors: `python main.py`
- [ ] Bot responds in Telegram
- [ ] Personal link works: `https://t.me/YOUR_BOT?start=YOUR_ID`
- [ ] Can send anonymous messages

If all checked ✅, you're ready to use the bot!

---

**Happy Botting! 🚀**

For updates and more info, check the README.md file.
