"""
Example usage and testing guide for Telegram Anonymous Bot
Shows how to use the bot and test various features
"""

# Example 1: Testing Rate Limiting
def test_rate_limiting():
    """
    Test the rate limiting functionality
    """
    from database import DatabaseManager
    from config import RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS
    
    db = DatabaseManager()
    user_id = 123456
    
    # Simulate sending messages
    print("Testing rate limiting...")
    for i in range(RATE_LIMIT_MESSAGES + 5):
        if db.check_rate_limit(user_id, RATE_LIMIT_MESSAGES, RATE_LIMIT_SECONDS):
            print(f"Message {i+1}: ✅ Within limit")
            db.record_message_for_rate_limit(user_id)
        else:
            print(f"Message {i+1}: ❌ Exceeded limit")


# Example 2: Testing Database Operations
def test_database_operations():
    """
    Test basic database operations
    """
    from database import DatabaseManager
    
    db = DatabaseManager()
    
    # Register a test user
    print("\n1. Registering test user...")
    result = db.register_user(
        user_id=999999,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    print(f"   Registration: {'✅ Success' if result else '❌ Failed'}")
    
    # Get user
    print("\n2. Retrieving user...")
    user = db.get_user(999999)
    if user:
        print(f"   ✅ Found user: {user['first_name']} (@{user['username']})")
    else:
        print("   ❌ User not found")
    
    # Save message
    print("\n3. Saving anonymous message...")
    result = db.save_anonymous_message(
        recipient_id=999999,
        message_text="This is a test anonymous message!"
    )
    print(f"   Save: {'✅ Success' if result else '❌ Failed'}")
    
    # Get messages
    print("\n4. Retrieving messages...")
    messages = db.get_user_messages(999999)
    print(f"   Found {len(messages)} message(s)")
    for msg in messages:
        print(f"   - {msg['message_text']}")
    
    # Toggle blocking
    print("\n5. Toggling anonymous blocking...")
    result = db.toggle_anonymous_blocking(999999, True)
    is_blocking = db.is_user_blocking_anonymous(999999)
    print(f"   Blocking: {'✅ Enabled' if is_blocking else '❌ Disabled'}")
    
    # Check stats
    print("\n6. Checking bot stats...")
    count = db.get_all_users_count()
    print(f"   Total registered users: {count}")


# Example 3: Testing Admin Panel
def test_admin_panel():
    """
    Test admin panel functionality
    """
    from admin import AdminPanel
    
    admin = AdminPanel()
    
    print("\n" + "="*60)
    print("ADMIN PANEL - BOT STATISTICS")
    print("="*60)
    
    # Get and display stats
    stats = admin.get_bot_stats()
    print(f"\nTotal Users: {stats['total_users']}")
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Messages Today: {stats['messages_today']}")
    print(f"Active Users (24h): {stats['active_users_24h']}")
    print(f"Users Blocking Anonymous: {stats['users_blocking_anonymous']}")
    
    # Get top recipients
    print("\nTop 5 Recipients:")
    top = admin.get_top_recipients(5)
    for i, recipient in enumerate(top, 1):
        print(f"  {i}. User {recipient['user_id']}: {recipient['message_count']} messages")
    
    # Get recent messages
    print("\nRecent Messages:")
    recent = admin.get_recent_messages(3)
    for msg in recent:
        print(f"  - {msg['message_text']}")


# Example 4: Bot Command Flow
"""
User Flow Example:

1. User opens Telegram and searches for bot
2. Clicks /start
   → Bot registers user
   → Generates personal link: t.me/bot?start=USER_ID
   → Shows main menu

3. User shares link with friends
4. Friend clicks link
   → Bot checks if recipient exists
   → Sets up message sending state
   → Waits for message input

5. Friend sends anonymous message
   → Bot checks rate limit
   → Validates message length
   → Stores message in database
   → Notifies recipient

6. Recipient gets notification
   → Opens bot
   → Clicks "View Messages"
   → Reads anonymous message

7. Recipient can toggle anonymous messages on/off
   → Stored in database
   → Affects future message delivery
"""


# Example 5: Keyboard and Inline Button Usage
"""
Main Menu Keyboard:
├── 📬 My Link
│   └── Shows personal link with copy button
├── 💬 View Messages
│   └── Lists all received messages
├── 👤 Profile
│   └── Shows user stats and info
├── ⚙️ Settings
│   ├── Toggle Anonymous Messages
│   └── View current settings
└── ❓ Help
    └── Shows usage instructions

Message Sending Flow:
1. User clicks "My Link" → Copy personal link
2. Shares link with friends
3. Friend clicks link → "start" parameter set
4. Friend sees: "Send anonymous message" prompt
5. Friend types message
6. Message stored and sender notified

Settings Management:
├── View current status
├── Toggle anonymous message acceptance
└── Settings persist in database
"""


# Example 6: Error Handling
"""
Common Error Cases Handled:

1. Invalid Recipient ID
   → Check if recipient exists in database
   → Return error message

2. Recipient Blocking Messages
   → Check is_blocking_anonymous flag
   → Return error message

3. Rate Limit Exceeded
   → Check message count in time window
   → Return rate limit message

4. Message Too Long
   → Validate length < 4096 chars
   → Return length error

5. Database Connection Error
   → Catch sqlite3.Error
   → Log error and retry

6. Bot Token Invalid
   → Catch aiogram exception
   → Show configuration error

7. User Cancels Operation
   → /cancel command
   → Clear FSM state
   → Return to main menu
"""


# Example 7: Configuration Options
CONFIG_EXAMPLES = {
    "rate_limiting": {
        "RATE_LIMIT_MESSAGES": 10,  # Max messages
        "RATE_LIMIT_SECONDS": 60,    # Per 60 seconds
        # Meaning: Max 10 messages per 60 seconds
    },
    "message_settings": {
        "MAX_MESSAGE_LENGTH": 4096,  # Telegram's limit
    },
    "database": {
        "DATABASE_PATH": "bot_database.db",
    },
    "bot": {
        "TELEGRAM_BOT_TOKEN": "YOUR_TOKEN_HERE",
    }
}


# Example 8: Database Schema
DATABASE_SCHEMA = """
Users Table:
- user_id (INTEGER, PRIMARY KEY)
- username (TEXT)
- first_name (TEXT)
- last_name (TEXT)
- created_at (TIMESTAMP)
- is_blocking_anonymous (BOOLEAN)
- message_count (INTEGER)

Messages Table:
- message_id (INTEGER, PRIMARY KEY, AUTO INCREMENT)
- recipient_id (INTEGER, FOREIGN KEY)
- message_text (TEXT)
- created_at (TIMESTAMP)
- is_read (BOOLEAN)

Rate Limit Table:
- id (INTEGER, PRIMARY KEY, AUTO INCREMENT)
- user_id (INTEGER, FOREIGN KEY)
- message_timestamp (TIMESTAMP)

Message Threads Table (for replies):
- thread_id (INTEGER, PRIMARY KEY, AUTO INCREMENT)
- recipient_id (INTEGER, FOREIGN KEY)
- message_id_parent (INTEGER, FOREIGN KEY)
- reply_message_text (TEXT)
- created_at (TIMESTAMP)
"""


if __name__ == "__main__":
    print("🤖 Telegram Anonymous Bot - Testing Guide")
    print("=" * 60)
    print("\nAvailable test functions:")
    print("1. test_rate_limiting() - Test rate limiting")
    print("2. test_database_operations() - Test database operations")
    print("3. test_admin_panel() - Test admin panel")
    print("\nExample: python -c \"from examples import test_database_operations; test_database_operations()\"")
    print("=" * 60)
