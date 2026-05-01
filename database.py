# database.py - إدارة قاعدة البيانات المتكاملة
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from config import DATA_DIR

DB_PATH = DATA_DIR / "boursagi.db"

def init_database():
    """تهيئة جميع جداول قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # جدول الصفقات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            entry_price REAL NOT NULL,
            target_price REAL NOT NULL,
            stop_loss REAL NOT NULL,
            trailing_stop REAL DEFAULT 0,
            quantity INTEGER NOT NULL,
            sector TEXT,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            current_price REAL,
            profit_pct REAL DEFAULT 0,
            highest_price REAL,
            notes TEXT
        )
    ''')
    
    # جدول سجل التنبيهات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER,
            alert_type TEXT,
            message TEXT,
            timestamp TEXT,
            is_sent INTEGER DEFAULT 0
        )
    ''')
    
    # جدول إحصائيات الأداء
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            total_invested REAL,
            total_current REAL,
            total_profit REAL,
            profit_pct REAL,
            win_rate REAL,
            trades_count INTEGER,
            winning_trades INTEGER
        )
    ''')
    
    # جدول إعدادات المستخدم
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # إعدادات افتراضية
    _set_default_settings()

def _set_default_settings():
    """تعيين الإعدادات الافتراضية"""
    default_settings = {
        "capital": "100000",
        "risk_percent": "2.0",
        "auto_trailing": "true",
        "daily_alerts": "true",
        "telegram_enabled": "false"
    }
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for key, value in default_settings.items():
        cursor.execute('''
            INSERT OR IGNORE INTO user_settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = None) -> str:
    """الحصول على إعداد معين"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM user_settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def update_setting(key: str, value: str):
    """تحديث إعداد معين"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_settings (key, value, updated_at)
        VALUES (?, ?, ?)
    ''', (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ====================== دوال الصفقات ======================

def save_trade(trade: Dict) -> int:
    """حفظ صفقة جديدة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (symbol, entry_price, target_price, stop_loss, trailing_stop, 
                           quantity, sector, date, status, highest_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trade["symbol"], trade["entry_price"], trade["target_price"],
        trade["stop_loss"], trade.get("trailing_stop", 0),
        trade["quantity"], trade.get("sector", ""), trade["date"],
        "active", trade["entry_price"]
    ))
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trade_id

def load_trades(status: str = "active") -> List[Dict]:
    """تحميل الصفقات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if status == "all":
        cursor.execute('SELECT * FROM trades ORDER BY id DESC')
    else:
        cursor.execute('SELECT * FROM trades WHERE status = ? ORDER BY id DESC', (status,))
    
    rows = cursor.fetchall()
    conn.close()
    
    trades = []
    column_names = ['id', 'symbol', 'entry_price', 'target_price', 'stop_loss', 
                    'trailing_stop', 'quantity', 'sector', 'date', 'status',
                    'current_price', 'profit_pct', 'highest_price', 'notes']
    
    for row in rows:
        trade = {}
        for i, col in enumerate(column_names):
            if i < len(row):
                trade[col] = row[i]
        trades.append(trade)
    
    # تعيين القيم الافتراضية
    for trade in trades:
        if trade.get('current_price') is None:
            trade['current_price'] = trade['entry_price']
        if trade.get('profit_pct') is None:
            trade['profit_pct'] = 0
        if trade.get('highest_price') is None:
            trade['highest_price'] = trade['entry_price']
    
    return trades

def update_trade(trade_id: int, **kwargs):
    """تحديث بيانات صفقة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for key, value in kwargs.items():
        if key in ['target_price', 'stop_loss', 'current_price', 'profit_pct', 
                   'highest_price', 'notes', 'status']:
            cursor.execute(f'UPDATE trades SET {key} = ? WHERE id = ?', (value, trade_id))
    
    conn.commit()
    conn.close()

def delete_trade(trade_id: int):
    """حذف صفقة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()

def close_trade(trade_id: int, exit_price: float):
    """إغلاق صفقة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT entry_price, quantity FROM trades WHERE id = ?', (trade_id,))
    row = cursor.fetchone()
    
    if row:
        entry_price, quantity = row
        profit = (exit_price - entry_price) * quantity
        profit_pct = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        
        cursor.execute('''
            UPDATE trades SET status = 'closed', current_price = ?, profit_pct = ? WHERE id = ?
        ''', (exit_price, profit_pct, trade_id))
        
        cursor.execute('''
            INSERT INTO alerts_log (trade_id, alert_type, message, timestamp, is_sent)
            VALUES (?, ?, ?, ?, ?)
        ''', (trade_id, "close", f"تم إغلاق الصفقة بربح {profit_pct:+.1f}%", 
              datetime.now().isoformat(), 1))
    
    conn.commit()
    conn.close()

def add_alert(trade_id: int, alert_type: str, message: str):
    """إضافة تنبيه جديد"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts_log (trade_id, alert_type, message, timestamp, is_sent)
        VALUES (?, ?, ?, ?, ?)
    ''', (trade_id, alert_type, message, datetime.now().isoformat(), 0))
    conn.commit()
    conn.close()
