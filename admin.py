"""
Admin utilities and monitoring for Telegram Anonymous Bot
Provides admin commands and bot statistics
"""

import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_PATH


class AdminPanel:
    """Admin utilities for bot management"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize admin panel"""
        self.db_path = db_path
    
    def get_bot_stats(self) -> dict:
        """Get overall bot statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        
        # Messages today
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE DATE(created_at) = ?
        ''', (today,))
        messages_today = cursor.fetchone()[0]
        
        # Average messages per user
        avg_messages = total_messages / total_users if total_users > 0 else 0
        
        # Users blocking anonymous
        cursor.execute('''
            SELECT COUNT(*) FROM users WHERE is_blocking_anonymous = 1
        ''')
        users_blocking = cursor.fetchone()[0]
        
        # Active users (received messages in last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute('''
            SELECT COUNT(DISTINCT recipient_id) FROM messages 
            WHERE created_at > ?
        ''', (yesterday.isoformat(),))
        active_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_messages': total_messages,
            'messages_today': messages_today,
            'average_messages_per_user': round(avg_messages, 2),
            'users_blocking_anonymous': users_blocking,
            'active_users_24h': active_users,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_top_recipients(self, limit: int = 10) -> list:
        """Get top recipients by message count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT recipient_id, COUNT(*) as count
            FROM messages
            GROUP BY recipient_id
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'user_id': row[0],
                'message_count': row[1]
            }
            for row in rows
        ]
    
    def get_recent_messages(self, limit: int = 10) -> list:
        """Get recent messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_id, recipient_id, message_text, created_at
            FROM messages
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'message_id': row[0],
                'recipient_id': row[1],
                'message_text': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                'created_at': row[3]
            }
            for row in rows
        ]
    
    def get_user_details(self, user_id: int) -> dict:
        """Get detailed information about a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User info
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            conn.close()
            return None
        
        # Message count
        cursor.execute('''
            SELECT COUNT(*) FROM messages WHERE recipient_id = ?
        ''', (user_id,))
        message_count = cursor.fetchone()[0]
        
        # Last message received
        cursor.execute('''
            SELECT created_at FROM messages 
            WHERE recipient_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id,))
        last_message = cursor.fetchone()
        
        conn.close()
        
        return {
            'user_id': user_row[0],
            'username': user_row[1],
            'first_name': user_row[2],
            'last_name': user_row[3],
            'created_at': user_row[4],
            'is_blocking_anonymous': bool(user_row[5]),
            'total_messages': message_count,
            'last_message_received': last_message[0] if last_message else None
        }
    
    def print_stats(self) -> None:
        """Print bot statistics to console"""
        stats = self.get_bot_stats()
        
        print("\n" + "=" * 60)
        print("BOT STATISTICS")
        print("=" * 60)
        print(f"Total Users: {stats['total_users']}")
        print(f"Total Messages: {stats['total_messages']}")
        print(f"Messages Today: {stats['messages_today']}")
        print(f"Avg Messages per User: {stats['average_messages_per_user']}")
        print(f"Users Blocking Anonymous: {stats['users_blocking_anonymous']}")
        print(f"Active Users (24h): {stats['active_users_24h']}")
        print(f"Last Updated: {stats['timestamp']}")
        print("=" * 60 + "\n")
    
    def print_top_recipients(self, limit: int = 10) -> None:
        """Print top recipients to console"""
        recipients = self.get_top_recipients(limit)
        
        print("\n" + "=" * 60)
        print(f"TOP {limit} RECIPIENTS")
        print("=" * 60)
        for i, recipient in enumerate(recipients, 1):
            print(f"{i}. User ID: {recipient['user_id']} | Messages: {recipient['message_count']}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Example usage
    admin = AdminPanel()
    admin.print_stats()
    admin.print_top_recipients(5)
