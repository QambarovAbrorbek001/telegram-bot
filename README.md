# 🤖 Telegram Anonymous Messages Bot

A Python-based Telegram bot that allows users to receive anonymous messages through personal links. Each user gets a unique referral link that they can share, and anyone who clicks it can send them anonymous messages without revealing their identity.

## ✨ Features

- ✅ **Unique Personal Links** - Each user gets a unique link (e.g., `t.me/bot?start=USER_ID`)
- ✅ **Anonymous Messaging** - Send messages without revealing your identity
- ✅ **Rate Limiting** - Built-in anti-spam protection (configurable)
- ✅ **Privacy Controls** - Users can toggle whether they accept anonymous messages
- ✅ **Message History** - View all received messages
- ✅ **User Profiles** - Track message counts and user information
- ✅ **SQLite Database** - Persistent data storage
- ✅ **Multiple Users** - Handle unlimited concurrent users
- ✅ **Modern Async** - Built with aiogram 3.x for high performance
- ✅ **Well Documented** - Clear comments throughout the code

## 📋 Requirements

- Python 3.10+
- A Telegram Bot Token (from @BotFather)

## 🚀 Quick Start

### Step 1: Clone or Download the Project

```bash
cd d:\projrcts\anonimbot
```

### Step 2: Create a Python Virtual Environment (Recommended)

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send the command `/newbot`
3. Follow the prompts to create your bot
4. Copy your bot token (looks like: `123456789:ABCDefGhijKlmnOPqrstUVwxyz1234567890`)

### Step 5: Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` and add your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

### Step 6: Run the Bot

```bash
python main.py
```

You should see:
```
🤖 Anonymous Messages Bot Starting...
==================================================
Make sure your TELEGRAM_BOT_TOKEN is set in .env file
==================================================
```

If successful, the bot is now running!

## 📱 How to Use the Bot

### For Users

1. **Start the Bot**: Search for your bot on Telegram and click `/start`
2. **Get Your Link**: Click "📬 My Link" to view your personal link
3. **Share Your Link**: Send it to friends or post it online
4. **Receive Messages**: When someone clicks your link and sends a message, you'll be notified
5. **Read Messages**: Use "💬 View Messages" to read all anonymous messages
6. **Manage Settings**: Toggle anonymous messaging on/off in Settings

### For Developers

#### Project Structure

```
anonimbot/
├── main.py              # Main bot file with command handlers
├── database.py          # SQLite database management
├── config.py            # Configuration and settings
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .env                 # Your actual bot token (don't commit!)
├── bot_database.db      # SQLite database (auto-created)
└── README.md            # This file
```

#### Key Modules

**database.py**
- `DatabaseManager`: Handles all database operations
- User registration and profile management
- Message storage and retrieval
- Rate limiting tracking
- Anti-spam features

**main.py**
- Command handlers (`/start`, `/help`, `/menu`, etc.)
- Callback query handlers for buttons
- FSM (Finite State Machine) for message flow
- User state management
- Rate limit checking

**config.py**
- Bot token configuration
- Rate limiting settings (messages per minute)
- Database path configuration

#### Key Functions

**Start Command with Parameters**
```python
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
```
- Handles `/start` with optional `?start=USER_ID` parameter
- Checks if recipient exists and accepts anonymous messages
- Sets up FSM state for message sending

**Message Handling**
```python
@dp.message(MessageStates.waiting_for_message)
async def handle_message(message: types.Message, state: FSMContext) -> None:
```
- Checks rate limits
- Validates message length
- Stores message anonymously
- Notifies recipient

**Rate Limiting**
```python
def check_rate_limit(self, user_id: int, max_messages: int, 
                    time_window_seconds: int) -> bool:
```
- Prevents users from spamming messages
- Configurable limits in `config.py`
- Automatic cleanup of old rate limit entries

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Rate limiting (messages per minute)
RATE_LIMIT_MESSAGES = 10      # Max 10 messages
RATE_LIMIT_SECONDS = 60       # Per 60 seconds

# Bot settings
MAX_MESSAGE_LENGTH = 4096     # Telegram limit
BOT_USERNAME = "YourBotUsername"  # Update after creating bot
```

## 🗄️ Database Schema

### Users Table
```sql
- user_id (PRIMARY KEY)
- username
- first_name
- last_name
- created_at (TIMESTAMP)
- is_blocking_anonymous (BOOLEAN)
- message_count (INTEGER)
```

### Messages Table
```sql
- message_id (PRIMARY KEY, AUTO INCREMENT)
- recipient_id (FOREIGN KEY)
- message_text (TEXT)
- created_at (TIMESTAMP)
- is_read (BOOLEAN)
```

### Rate Limit Table
```sql
- id (PRIMARY KEY, AUTO INCREMENT)
- user_id (FOREIGN KEY)
- message_timestamp (TIMESTAMP)
```

### Message Threads Table
```sql
- thread_id (PRIMARY KEY, AUTO INCREMENT)
- recipient_id (FOREIGN KEY)
- message_id_parent (FOREIGN KEY)
- reply_message_text (TEXT)
- created_at (TIMESTAMP)
```

## 🔒 Privacy & Security

- **No Sender Information**: Messages are stored without sender ID
- **User Choice**: Users can disable anonymous messages in settings
- **Rate Limiting**: Prevents spam and abuse
- **Local Storage**: All data stored in SQLite database (in your control)
- **No Cloud**: Bot data never leaves your server

## 🛡️ Anti-Spam Features

1. **Rate Limiting**: Maximum messages per minute per user
2. **Message Length Validation**: Max 4096 characters
3. **User Blocking**: Users can block anonymous messages entirely
4. **Automatic Cleanup**: Old rate limit entries automatically purged

## 📊 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot and get personal link |
| `/help` | Show help information |
| `/menu` | Show main menu |
| `/profile` | View your profile |
| `/settings` | Manage privacy settings |
| `/settings_toggle` | Toggle anonymous messages |
| `/messages` | View all received messages |
| `/cancel` | Cancel current action |

## 🤝 Inline Buttons

- 📬 **My Link** - Get and copy your personal referral link
- 💬 **View Messages** - See all received anonymous messages
- 👤 **Profile** - View your user profile and statistics
- ⚙️ **Settings** - Manage privacy and notification settings
- ❓ **Help** - Show help information
- 🔒 **Toggle Anonymous Messages** - Enable/disable anonymous messaging
- 📖 **Read All Messages** - View detailed message history

## 🔧 Deployment Options

### Local Development
```bash
python main.py
```

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t telegram-anon-bot .
docker run -e TELEGRAM_BOT_TOKEN=your_token_here telegram-anon-bot
```

### Production (with Systemd)

Create `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Anonymous Messages Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/anonimbot
ExecStart=/home/botuser/anonimbot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## 🐛 Troubleshooting

### "Invalid token"
- Check your bot token in `.env`
- Make sure you got it from @BotFather
- Verify no extra spaces or characters

### "No module named 'aiogram'"
- Run: `pip install -r requirements.txt`
- Make sure your virtual environment is activated

### Bot not responding
- Check internet connection
- Verify token is correct
- Look for errors in console output
- Increase logging verbosity

### Database errors
- Delete `bot_database.db` to reset database
- Check file permissions in project folder
- Ensure enough disk space available

## 📝 Logging

The bot logs important events. Check console output:
```
2024-04-25 10:30:45,123 - __main__ - INFO - Starting Anonymous Messages Bot...
2024-04-25 10:30:46,456 - __main__ - INFO - User 123456 started the bot
```

## 🚀 Advanced Features (Bonus)

### Reply Anonymously
The database schema includes `message_threads` table for future reply feature:
```python
# This would enable threaded conversations while maintaining anonymity
def save_reply_message(self, recipient_id: int, parent_message_id: int, reply_text: str):
    # Implementation for replying to specific anonymous messages
    pass
```

### Block Management
Users can block anonymous messages:
```python
@dp.callback_query(F.data == "settings_toggle_anonymous")
async def cb_toggle_anonymous(callback: types.CallbackQuery):
    # Toggle is_blocking_anonymous field
```

## 📚 API Reference

### DatabaseManager Class

```python
# User Management
register_user(user_id, username, first_name, last_name) -> bool
get_user(user_id) -> Optional[Dict]
get_all_users_count() -> int

# Message Management
save_anonymous_message(recipient_id, message_text) -> bool
get_user_messages(user_id, unread_only=False) -> List[Dict]
mark_message_as_read(message_id) -> bool

# Rate Limiting
check_rate_limit(user_id, max_messages, time_window_seconds) -> bool
record_message_for_rate_limit(user_id) -> bool

# Privacy Settings
toggle_anonymous_blocking(user_id, block) -> bool
is_user_blocking_anonymous(user_id) -> bool

# Maintenance
cleanup_old_rate_limit_entries(days=1) -> None
```

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Feel free to fork, modify, and improve this bot. Common enhancements:
- Add database backups
- Implement message deletion
- Add admin commands
- Create web dashboard
- Add message reactions/emojis
- Implement message expiration

## ❓ FAQ

**Q: Is the bot free?**
A: Yes! Telegram's Bot API is free. You only pay for hosting/server.

**Q: Can users identify each other through the bot?**
A: No, messages are stored without sender information. However, Telegram admins could potentially trace messages.

**Q: How many users can the bot handle?**
A: Limited only by your server resources. SQLite works well for 10k+ users.

**Q: Can I run multiple instances?**
A: Yes, but they must use different bot tokens and databases.

**Q: How do I backup the database?**
A: Simply copy `bot_database.db` to a safe location regularly.

## 🎯 Future Improvements

- [ ] Web dashboard for stats
- [ ] Admin commands and moderation
- [ ] Message expiration (auto-delete)
- [ ] Forwarding to channels
- [ ] Reactions and emojis
- [ ] Redis caching for performance
- [ ] PostgreSQL support
- [ ] Message filtering/moderation AI
- [ ] Two-factor authentication
- [ ] Cryptocurrency tips for anonymous donations

---

**Happy messaging! 🎉**

For support, check the code comments or feel free to modify as needed.
