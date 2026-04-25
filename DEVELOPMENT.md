# 📚 Development Reference Guide

Complete technical documentation for developers working with the Telegram Anonymous Bot.

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Code Overview](#code-overview)
3. [API Reference](#api-reference)
4. [Database](#database)
5. [Message Flow](#message-flow)
6. [State Management](#state-management)
7. [Error Handling](#error-handling)
8. [Extension Guide](#extension-guide)
9. [Performance Tips](#performance-tips)
10. [Deployment](#deployment)

---

## 📐 Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Users                       │
└─────────────────────┬───────────────────────────────────┘
                      │ (Messages via Telegram API)
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Bot Handler (main.py)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Command Handlers: /start, /help, /menu, etc   │  │
│  │  Message Handlers: Text, Callbacks             │  │
│  │  FSM: State Management for Message Flow        │  │
│  └──────────────────────────────────────────────────┘  │
└────┬──────────────────────────────────────────────┬────┘
     │                                              │
     ▼                                              ▼
┌─────────────────────────┐          ┌──────────────────────┐
│   Database Layer        │          │  Admin Panel         │
│   (database.py)         │          │  (admin.py)          │
│                         │          │                      │
│ ┌─────────────────────┐ │          │ • Statistics         │
│ │ SQLite Database     │ │          │ • User Management    │
│ │ - Users Table       │ │          │ • Message Logs       │
│ │ - Messages Table    │ │          │ • Analytics          │
│ │ - Rate Limit Table  │ │          │                      │
│ │ - Threads Table     │ │          └──────────────────────┘
│ └─────────────────────┘ │
└─────────────────────────┘
```

### File Structure

```
main.py (1200 lines)
├── Imports and Setup
├── State Definitions (FSM)
├── Start Command Handler
├── Help Command Handler
├── Menu System (Callbacks)
│   ├── get_link
│   ├── view_messages
│   ├── profile
│   └── settings
├── Message Handling
│   ├── handle_message (for anonymous messages)
│   └── handle_any_message (default fallback)
└── Main Event Loop

database.py (400 lines)
├── DatabaseManager Class
├── User Management Methods
├── Message Storage/Retrieval
├── Rate Limiting Methods
├── Privacy Settings Methods
└── Maintenance Methods

config.py (40 lines)
├── Telegram Bot Token
├── Database Configuration
├── Rate Limiting Settings
└── Bot Configuration

admin.py (250 lines)
├── AdminPanel Class
├── Statistics Methods
├── User Tracking Methods
└── Console Reporting Methods

examples.py (300 lines)
├── Testing Functions
├── Usage Examples
├── Configuration Examples
└── Database Schema
```

---

## 🔍 Code Overview

### main.py - Bot Handler

**Key Components:**

#### 1. FSM States
```python
class MessageStates(StatesGroup):
    waiting_for_recipient_id = State()  # Waiting for recipient selection
    waiting_for_message = State()        # Waiting for message input

class UserStates(StatesGroup):
    main_menu = State()
    viewing_profile = State()
```

#### 2. Command Handlers
```python
@dp.message(CommandStart())
async def cmd_start(message, state)  # /start command with parameter support

@dp.message(Command("help"))
async def cmd_help(message)           # /help command

@dp.message(Command("menu"))
async def cmd_menu(message, state)    # /menu command
```

#### 3. Callback Query Handlers
```python
@dp.callback_query(F.data == "menu_get_link")
async def cb_get_link(callback)       # Handle "My Link" button

@dp.callback_query(F.data == "menu_view_messages")
async def cb_view_messages(callback)  # Handle "View Messages" button
```

#### 4. Message Handler
```python
@dp.message(MessageStates.waiting_for_message)
async def handle_message(message, state)
# Handles anonymous messages with:
# - Rate limiting checks
# - Length validation
# - Recipient existence verification
# - Database storage
# - Recipient notification
```

### database.py - Data Layer

**Key Methods:**

```python
# User Management
register_user(user_id, username, first_name, last_name)
get_user(user_id) -> Dict
get_all_users_count() -> int

# Message Operations
save_anonymous_message(recipient_id, message_text)
get_user_messages(user_id, unread_only=False) -> List[Dict]
mark_message_as_read(message_id)

# Rate Limiting
check_rate_limit(user_id, max_messages, time_window_seconds) -> bool
record_message_for_rate_limit(user_id)

# Privacy
toggle_anonymous_blocking(user_id, block)
is_user_blocking_anonymous(user_id) -> bool

# Maintenance
cleanup_old_rate_limit_entries(days=1)
```

### config.py - Configuration

**Environment Variables:**

```python
# Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN = "123456789:ABCDefGhij..."

# Rate Limiting (messages per minute)
RATE_LIMIT_MESSAGES = 10
RATE_LIMIT_SECONDS = 60

# Limits
MAX_MESSAGE_LENGTH = 4096

# Database
DATABASE_PATH = "bot_database.db"
```

---

## 🔌 API Reference

### DatabaseManager API

#### Initialize
```python
from database import DatabaseManager

db = DatabaseManager()  # Uses DATABASE_PATH from config.py
db = DatabaseManager("custom_path.db")  # Custom path
```

#### User Operations
```python
# Register or update user
db.register_user(
    user_id=123456,
    username="john_doe",
    first_name="John",
    last_name="Doe"
) -> bool

# Retrieve user
user = db.get_user(123456) -> Dict | None
# Returns: {user_id, username, first_name, last_name, created_at, 
#           is_blocking_anonymous, message_count}
```

#### Message Operations
```python
# Save anonymous message
db.save_anonymous_message(
    recipient_id=123456,
    message_text="Hello from anonymous sender!"
) -> bool

# Get messages
messages = db.get_user_messages(
    user_id=123456,
    unread_only=False
) -> List[Dict]
# Returns list of {message_id, recipient_id, message_text, created_at, is_read}

# Mark as read
db.mark_message_as_read(message_id=1) -> bool
```

#### Rate Limiting
```python
# Check if user can send message
can_send = db.check_rate_limit(
    user_id=123456,
    max_messages=10,
    time_window_seconds=60
) -> bool

# Record message for rate limiting
db.record_message_for_rate_limit(user_id=123456) -> bool
```

#### Privacy Settings
```python
# Toggle anonymous blocking
db.toggle_anonymous_blocking(user_id=123456, block=True) -> bool

# Check if blocking
is_blocking = db.is_user_blocking_anonymous(user_id=123456) -> bool
```

---

## 🗄️ Database

### Schema

#### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_blocking_anonymous BOOLEAN DEFAULT 0,
    message_count INTEGER DEFAULT 0
);
```

#### Messages Table
```sql
CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    FOREIGN KEY (recipient_id) REFERENCES users(user_id)
);
```

#### Rate Limit Table
```sql
CREATE TABLE rate_limit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### Message Threads Table (for future replies)
```sql
CREATE TABLE message_threads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER NOT NULL,
    message_id_parent INTEGER,
    reply_message_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES users(user_id),
    FOREIGN KEY (message_id_parent) REFERENCES messages(message_id)
);
```

### Queries

**Get user statistics:**
```sql
SELECT 
    u.user_id,
    u.username,
    COUNT(m.message_id) as message_count,
    MAX(m.created_at) as last_message
FROM users u
LEFT JOIN messages m ON u.user_id = m.recipient_id
GROUP BY u.user_id
ORDER BY message_count DESC;
```

**Get rate limit violations:**
```sql
SELECT user_id, COUNT(*) as message_count
FROM rate_limit
WHERE message_timestamp > datetime('now', '-1 minute')
GROUP BY user_id
HAVING COUNT(*) > 10;
```

**Get inactive users:**
```sql
SELECT user_id, username, created_at
FROM users
WHERE user_id NOT IN (
    SELECT DISTINCT recipient_id FROM messages
    WHERE created_at > datetime('now', '-30 days')
)
ORDER BY created_at DESC;
```

---

## 📊 Message Flow

### Flow 1: User Registration

```
User starts bot
    ↓
/start command triggered
    ↓
Extract user info from message
    ↓
db.register_user() called
    ↓
Generate personal link with user_id
    ↓
Display link and main menu
```

### Flow 2: Sending Anonymous Message

```
Sender clicks personal link (with start=RECIPIENT_ID)
    ↓
Bot checks if recipient exists
    ↓
Bot checks if recipient blocking anonymous
    ↓
FSM state → waiting_for_message
    ↓
Sender types message
    ↓
Bot validates message:
  - Check rate limit
  - Check length < 4096
  - Check recipient still exists
    ↓
db.save_anonymous_message()
    ↓
db.record_message_for_rate_limit()
    ↓
Send notification to recipient
    ↓
Confirm to sender
```

### Flow 3: Viewing Messages

```
Recipient clicks "View Messages"
    ↓
db.get_user_messages(user_id)
    ↓
Display messages with timestamps
    ↓
Mark messages as read
    ↓
Show unread count
```

---

## 🎮 State Management (FSM)

The bot uses Finite State Machine (FSM) for conversation flow.

### State Transitions

```
Start
  ↓
Main Menu (initial state)
  ├─ "My Link" → Show link (no state change)
  ├─ "View Messages" → Show messages (no state change)
  ├─ "Profile" → Show profile (no state change)
  ├─ "Settings" → settings menu (no state change)
  └─ Click personal link → waiting_for_message
          ↓
    waiting_for_message
          ├─ Send message → Validate → Send → Return to main
          ├─ /cancel → Return to main
          └─ /help → Show help → Return to waiting_for_message
```

### FSM Usage in Code

```python
# Set state
await state.set_state(MessageStates.waiting_for_message)

# Get state
current_state = await state.get_state()

# Store data
await state.update_data(recipient_id=123456)

# Retrieve data
data = await state.get_data()
recipient_id = data.get('recipient_id')

# Clear state
await state.clear()
```

---

## 🛡️ Error Handling

### Error Types and Handling

#### 1. Database Errors
```python
try:
    db.save_anonymous_message(recipient_id, message_text)
except sqlite3.Error as e:
    logger.error(f"Database error: {e}")
    await message.answer("❌ Failed to send message. Try again.")
```

#### 2. Validation Errors
```python
# Check message length
if len(message.text) > 4096:
    await message.answer("❌ Message is too long")
    return

# Check rate limit
if not db.check_rate_limit(user_id, RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS):
    await message.answer("⏱️ You're sending too fast")
    return

# Check recipient exists
recipient = db.get_user(recipient_id)
if not recipient:
    await message.answer("❌ Recipient not found")
    return
```

#### 3. Telegram API Errors
```python
try:
    await bot.send_message(recipient_id, message_text)
except Exception as e:
    logger.warning(f"Could not notify recipient: {e}")
```

---

## 🚀 Extension Guide

### Adding New Commands

```python
@dp.message(Command("newcommand"))
async def cmd_newcommand(message: types.Message) -> None:
    """Handle /newcommand"""
    user_id = message.from_user.id
    
    # Your logic here
    await message.answer("Response text")
```

### Adding New Buttons

```python
def get_custom_keyboard() -> InlineKeyboardMarkup:
    """Generate custom keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Button 1", callback_data="btn1")],
        [InlineKeyboardButton(text="📌 Button 2", callback_data="btn2")],
    ])
    return keyboard

@dp.callback_query(F.data == "btn1")
async def cb_button1(callback: types.CallbackQuery) -> None:
    """Handle button 1"""
    await callback.message.edit_text("Button 1 clicked!")
    await callback.answer()
```

### Adding New Database Operations

```python
# In database.py, add to DatabaseManager class:
def get_custom_data(self, user_id: int) -> List[Dict]:
    """Get custom data for user"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM custom_table WHERE user_id = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{'data': row} for row in rows]
```

### Adding New Features

**Example: Message Reactions**

1. Add database table:
```sql
CREATE TABLE message_reactions (
    reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER,
    reaction_emoji TEXT,
    user_id INTEGER,
    FOREIGN KEY (message_id) REFERENCES messages(message_id)
);
```

2. Add database methods:
```python
def add_reaction(self, message_id: int, emoji: str):
    # Add emoji reaction to message
    pass

def get_reactions(self, message_id: int) -> List[str]:
    # Get all reactions for message
    pass
```

3. Add bot command:
```python
@dp.callback_query(F.data.startswith("react_"))
async def cb_reaction(callback: types.CallbackQuery) -> None:
    emoji = callback.data.split("_")[1]
    # Handle reaction
    pass
```

---

## ⚡ Performance Tips

### 1. Database Optimization
```python
# Use connection pooling for frequent operations
# Create indices on frequently queried columns
sqlite3.execute('CREATE INDEX idx_recipient ON messages(recipient_id)')
sqlite3.execute('CREATE INDEX idx_timestamp ON rate_limit(message_timestamp)')
```

### 2. Caching
```python
# Cache frequently accessed data
user_cache = {}

def get_user_cached(user_id: int) -> Dict:
    if user_id in user_cache:
        return user_cache[user_id]
    
    user = db.get_user(user_id)
    user_cache[user_id] = user
    return user
```

### 3. Async Operations
```python
# Use async/await for I/O operations
async def handle_multiple_messages(messages: List):
    tasks = [bot.send_message(msg['recipient'], msg['text']) 
             for msg in messages]
    await asyncio.gather(*tasks)
```

### 4. Rate Limit Cleanup
```python
# Run periodically to clean old entries
async def cleanup_task():
    while True:
        await asyncio.sleep(3600)  # Every hour
        db.cleanup_old_rate_limit_entries(days=1)
```

---

## 🌐 Deployment

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**Build and run:**
```bash
docker build -t telegram-anon-bot .
docker run -e TELEGRAM_BOT_TOKEN=your_token telegram-anon-bot
```

### Systemd Service (Linux)

**File: /etc/systemd/system/telegram-bot.service**
```ini
[Unit]
Description=Telegram Anonymous Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/anonimbot
ExecStart=/home/botuser/anonimbot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Cloud Deployment (Heroku)

**Procfile:**
```
worker: python main.py
```

**Deploy:**
```bash
heroku create your-bot-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
```

---

## 📝 Logging & Debugging

### Enable Debug Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Key Events
```python
logger.info(f"User {user_id} registered")
logger.warning(f"Rate limit exceeded for {user_id}")
logger.error(f"Database error: {e}")
logger.debug(f"FSM state: {current_state}")
```

### Monitor Logs
```bash
# Show recent logs
journalctl -u telegram-bot -n 50

# Follow logs in real-time
journalctl -u telegram-bot -f

# Show errors only
journalctl -u telegram-bot -p err
```

---

## 🔗 Resources

- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python SQLite](https://docs.python.org/3/library/sqlite3.html)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

---

**Last Updated:** April 2024
**Version:** 1.0
**Status:** Production Ready
