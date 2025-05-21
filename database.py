import sqlite3
from datetime import datetime, timedelta

def create_tables():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    
    # جدول اشتراک گروه‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS groups
                 (chat_id INTEGER PRIMARY KEY, 
                 expiry_date DATETIME)''')
    
    # جدول اخطارهای کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS warnings
                 (user_id INTEGER, 
                 chat_id INTEGER,
                 count INTEGER DEFAULT 0,
                 PRIMARY KEY (user_id, chat_id))''')
    
    conn.commit()
    conn.close()

# توابع مدیریت دیتابیس
def get_subscription(chat_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT expiry_date FROM groups WHERE chat_id=?", (chat_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_subscription(chat_id, days):
    expiry_date = datetime.now() + timedelta(days=days)
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("REPLACE INTO groups (chat_id, expiry_date) VALUES (?, ?)", 
              (chat_id, expiry_date))
    conn.commit()
    conn.close()

def add_warning(user_id, chat_id):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO warnings (user_id, chat_id, count) VALUES (?, ?, 0)", 
              (user_id, chat_id))
    c.execute("UPDATE warnings SET count = count + 1 WHERE user_id=? AND chat_id=?", 
              (user_id, chat_id))
    conn.commit()
    conn.close()