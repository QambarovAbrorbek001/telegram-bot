"""
Database management module for Telegram Anonymous Bot
Handles SQLite operations for users, messages, and blocked users
"""
import sqlite3
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from config import DATABASE_PATH, BLOCK_LIST_FILE


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
        
        # Users table - stores user information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocking_anonymous BOOLEAN DEFAULT 0,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # Messages table - stores anonymous messages (without sender info)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY (recipient_id) REFERENCES users(user_id)
            )
        ''')
        
        # Rate limiting table - tracks message timestamps for rate limiting
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Message history table - for reply feature (stores parent message reference)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_threads (
                thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER NOT NULL,
                message_id_parent INTEGER,
                reply_message_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES users(user_id),
                FOREIGN KEY (message_id_parent) REFERENCES messages(message_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, user_id: int, username: str = None, 
                     first_name: str = None, last_name: str = None) -> bool:
        """Register a new user or update existing user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name))
            
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
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'created_at': row[4],
                'is_blocking_anonymous': bool(row[5]),
                'message_count': row[6]
            }
        return None
    
    def save_anonymous_message(self, recipient_id: int, message_text: str) -> bool:
        """Save an anonymous message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO messages (recipient_id, message_text, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (recipient_id, message_text))
            
            # Update message count for recipient
            cursor.execute('''
                UPDATE users SET message_count = message_count + 1 
                WHERE user_id = ?
            ''', (recipient_id,))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving message: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_messages(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Retrieve messages for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if unread_only:
            cursor.execute('''
                SELECT message_id, recipient_id, message_text, created_at, is_read
                FROM messages WHERE recipient_id = ? AND is_read = 0
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT message_id, recipient_id, message_text, created_at, is_read
                FROM messages WHERE recipient_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'message_id': row[0],
                'recipient_id': row[1],
                'message_text': row[2],
                'created_at': row[3],
                'is_read': bool(row[4])
            })
        
        return messages
    
    def mark_message_as_read(self, message_id: int) -> bool:
        """Mark a message as read"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE messages SET is_read = 1 WHERE message_id = ?
            ''', (message_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking message as read: {e}")
            return False
        finally:
            conn.close()
    
    def check_rate_limit(self, user_id: int, max_messages: int, 
                        time_window_seconds: int) -> bool:
        """Check if user has exceeded rate limit
        Returns True if user is within limit, False if exceeded"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate time cutoff
        cutoff_time = datetime.now() - timedelta(seconds=time_window_seconds)
        
        cursor.execute('''
            SELECT COUNT(*) FROM rate_limit 
            WHERE user_id = ? AND message_timestamp > ?
        ''', (user_id, cutoff_time.isoformat()))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count < max_messages
    
    def record_message_for_rate_limit(self, user_id: int) -> bool:
        """Record a message for rate limiting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO rate_limit (user_id, message_timestamp)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (user_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording rate limit: {e}")
            return False
        finally:
            conn.close()
    
    def toggle_anonymous_blocking(self, user_id: int, block: bool) -> bool:
        """Toggle whether user accepts anonymous messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET is_blocking_anonymous = ? WHERE user_id = ?
            ''', (int(block), user_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error toggling anonymous blocking: {e}")
            return False
        finally:
            conn.close()
    
    def is_user_blocking_anonymous(self, user_id: int) -> bool:
        """Check if user is blocking anonymous messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT is_blocking_anonymous FROM users WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return bool(row[0]) if row else False
    
    def cleanup_old_rate_limit_entries(self, days: int = 1) -> None:
        """Clean up old rate limit entries to keep database size manageable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(days=days)
        cursor.execute('''
            DELETE FROM rate_limit WHERE message_timestamp < ?
        ''', (cutoff_time.isoformat(),))
        
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
