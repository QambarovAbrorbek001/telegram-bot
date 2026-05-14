"""
Database management module for Telegram Anonymous Bot
Handles SQLite operations for users, messages, tokens, and required channels.
Minimal: text-only anonymous messaging with replies and channel subscription.
"""
import sqlite3
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from config import DATABASE_PATH
import secrets


class DatabaseManager:
    """Manages all database operations for the bot"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database manager and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Create necessary tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # User tokens table — secure link tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_tokens (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Messages table — anonymous text messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER NOT NULL,
                sender_id INTEGER,
                message_text TEXT,
                reply_to_message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES users(user_id),
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (reply_to_message_id) REFERENCES messages(message_id)
            )
        ''')
        
        # Ensure required columns exist on upgrade
        cursor.execute("PRAGMA table_info(messages)")
        existing = {col[1] for col in cursor.fetchall()}
        needed = {'sender_id', 'reply_to_message_id'}
        for col in needed:
            if col not in existing:
                cursor.execute(f'ALTER TABLE messages ADD COLUMN {col} INTEGER')
        
        # Rate limiting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Required channels table — mandatory subscription channels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS required_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                channel_username TEXT,
                invite_link TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ensure invite_link column exists on upgrade
        cursor.execute("PRAGMA table_info(required_channels)")
        existing_cols = {col[1] for col in cursor.fetchall()}
        if 'invite_link' not in existing_cols:
            cursor.execute("ALTER TABLE required_channels ADD COLUMN invite_link TEXT")
        
        # Pending join requests — users who requested to join private channels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_join_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, channel_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None) -> bool:
        """Register a new user or update existing user, ensuring persistent token exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, current_time))
            
            # Ensure user has a persistent token (create if missing)
            cursor.execute('SELECT 1 FROM user_tokens WHERE user_id = ?', (user_id,))
            if not cursor.fetchone():
                token = secrets.token_urlsafe(16)
                cursor.execute('''
                    INSERT INTO user_tokens (token, user_id) VALUES (?, ?)
                ''', (token, user_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error registering user: {e}")
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Retrieve user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, last_name, created_at, message_count FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'created_at': row[4],
                'message_count': row[5]
            }
        return None
    
    def save_anonymous_message(
        self, 
        recipient_id: int, 
        message_text: str,
        sender_id: int = None,
        reply_to_message_id: int = None
    ) -> Optional[int]:
        """Save an anonymous text message to database and return new message_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO messages 
                (recipient_id, sender_id, message_text, reply_to_message_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (recipient_id, sender_id, message_text, reply_to_message_id, current_time))
            
            message_id = cursor.lastrowid
            
            # Update message count for recipient
            cursor.execute('''
                UPDATE users SET message_count = message_count + 1 
                WHERE user_id = ?
            ''', (recipient_id,))
            
            conn.commit()
            return message_id
        except sqlite3.Error as e:
            print(f"Error saving message: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_messages(self, user_id: int) -> List[Dict]:
        """Retrieve all messages for a user (text only, with sender for reply routing)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_id, recipient_id, sender_id, message_text, 
                   reply_to_message_id, created_at
            FROM messages 
            WHERE recipient_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'message_id': row[0],
                'recipient_id': row[1],
                'sender_id': row[2],
                'message_text': row[3],
                'reply_to_message_id': row[4],
                'created_at': row[5]
            })
        
        return messages
    
    # ============================================================
    # Rate limiting
    # ============================================================
    def check_rate_limit(self, user_id: int, max_messages: int, 
                        time_window_seconds: int) -> bool:
        """Check if user has exceeded rate limit. Returns True if within limit."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now(ZoneInfo("Asia/Tashkent")) - 
                      timedelta(seconds=time_window_seconds)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            SELECT COUNT(*) FROM rate_limit 
            WHERE user_id = ? AND message_timestamp > ?
        ''', (user_id, cutoff_time))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count < max_messages
    
    def record_message_for_rate_limit(self, user_id: int) -> bool:
        """Record a message timestamp for rate limiting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now(ZoneInfo("Asia/Tashkent")).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO rate_limit (user_id, message_timestamp)
                VALUES (?, ?)
            ''', (user_id, current_time))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording rate limit: {e}")
            return False
        finally:
            conn.close()
    
    def cleanup_old_rate_limit_entries(self, days: int = 1) -> None:
        """Clean up old rate limit entries to keep database size manageable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now(ZoneInfo("Asia/Tashkent")) - 
                      timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            DELETE FROM rate_limit WHERE message_timestamp < ?
        ''', (cutoff_time,))
        
        conn.commit()
        conn.close()
    
    def cleanup_old_rate_limit_entries(self, days: int = 1) -> None:
        """Clean up old rate limit entries to keep database size manageable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now(ZoneInfo("Asia/Tashkent")) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            DELETE FROM rate_limit WHERE message_timestamp < ?
        ''', (cutoff_time,))
        
        conn.commit()
        conn.close()
    
    def get_all_users_count(self) -> int:
        """Get total count of registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_all_user_ids(self) -> List[int]:
        """Get list of all user IDs (for broadcasting)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict]:
        """Get a specific message by its ID (for reply routing)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_id, recipient_id, sender_id, message_text, 
                   reply_to_message_id, created_at
            FROM messages WHERE message_id = ?
        ''', (message_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'message_id': row[0],
                'recipient_id': row[1],
                'sender_id': row[2],
                'message_text': row[3],
                'reply_to_message_id': row[4],
                'created_at': row[5]
            }
        return None
    
    # ============================================================
    # Token-based links
    # ============================================================
    def create_or_get_user_token(self, user_id: int) -> str:
        """Create a new token for user or return existing one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if token already exists
            cursor.execute('SELECT token FROM user_tokens WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            
            # Create new secure token
            token = secrets.token_urlsafe(16)
            cursor.execute('''
                INSERT INTO user_tokens (token, user_id) VALUES (?, ?)
            ''', (token, user_id))
            conn.commit()
            return token
        except sqlite3.Error as e:
            print(f"Error creating token: {e}")
            return secrets.token_urlsafe(16)  # fallback
        finally:
            conn.close()
    
    def get_user_id_by_token(self, token: str) -> Optional[int]:
        """Get user_id from token, or None if invalid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM user_tokens WHERE token = ?', (token,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    # ============================================================
    # Required channels management
    # ============================================================
    def add_required_channel(self, channel_id: int, channel_username: str = None, invite_link: str = None) -> bool:
        """Add a required subscription channel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO required_channels (channel_id, channel_username, invite_link) 
                VALUES (?, ?, ?)
            ''', (channel_id, channel_username, invite_link))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding channel: {e}")
            return False
        finally:
            conn.close()
    
    def remove_required_channel(self, row_id: int) -> bool:
        """Remove a required subscription channel by database row id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM required_channels WHERE id = ?', (row_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error removing channel: {e}")
            return False
        finally:
            conn.close()
    
    def get_required_channels(self) -> List[Dict]:
        """Get all required subscription channels"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, channel_id, channel_username, invite_link FROM required_channels ORDER BY added_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'id': r[0],
                'channel_id': r[1],
                'channel_username': r[2],
                'invite_link': r[3]
            }
            for r in rows
        ]
    
    def get_all_required_channel_ids(self) -> List[int]:
        """Get list of all required channel IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id FROM required_channels')
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
    # ============================================================
    # Pending join requests management
    # ============================================================
    def add_join_request(self, user_id: int, channel_id: int) -> bool:
        """Record that user has sent a join request to a channel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO pending_join_requests (user_id, channel_id)
                VALUES (?, ?)
            ''', (user_id, channel_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding join request: {e}")
            return False
        finally:
            conn.close()
    
    def remove_join_request(self, user_id: int, channel_id: int) -> bool:
        """Remove join request record (when approved/denied/cancelled)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM pending_join_requests 
                WHERE user_id = ? AND channel_id = ?
            ''', (user_id, channel_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error removing join request: {e}")
            return False
        finally:
            conn.close()
    
    def has_pending_join_request(self, user_id: int, channel_id: int) -> bool:
        """Check if user has an active join request for a channel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM pending_join_requests 
            WHERE user_id = ? AND channel_id = ?
        ''', (user_id, channel_id))
        row = cursor.fetchone()
        conn.close()
        return bool(row)
