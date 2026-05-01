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
            is_sent INTEGER DEFAULT 0,
            FOREIGN KEY (trade_id) REFERENCES trades(id)
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
    set_default_settings()

def set_default_settings():
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
    for row in rows:
        trades.append({
            "id": row[0], "symbol": row[1], "entry_price": row[2],
            "target_price": row[3], "stop_loss": row[4], "trailing_stop": row[5] if row[5] else 0,
            "quantity": row[6], "sector": row[7], "date": row[8],
            "status": row[9], "current_price": row[10] if row[10] else row[2],
            "profit_pct": row[11] if row[11] else 0,
            "highest_price": row[12] if row[12] else row[2],
            "notes": row[13] if len(row) > 13 else ""
        })
    return trades

def update_trade(trade_id: int, **kwargs):
    """تحديث بيانات صفقة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for key, value in kwargs.items():
        if key in ["target_price", "stop_loss", "notes", "status"]:
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
    
    # جلب بيانات الصفقة
    cursor.execute('SELECT entry_price, quantity FROM trades WHERE id = ?', (trade_id,))
    row = cursor.fetchone()
    
    if row:
        entry_price, quantity = row
        profit = (exit_price - entry_price) * quantity
        profit_pct = ((exit_price - entry_price) / entry_price) * 100
        
        cursor.execute('''
            UPDATE trades SET status = 'closed', current_price = ?, profit_pct = ? WHERE id = ?
        ''', (exit_price, profit_pct, trade_id))
        
        # تسجيل الإغلاق في سجل التنبيهات
        cursor.execute('''
            INSERT INTO alerts_log (trade_id, alert_type, message, timestamp, is_sent)
            VALUES (?, ?, ?, ?, ?)
        ''', (trade_id, "close", f"تم إغلاق الصفقة بربح {profit_pct:+.1f}%", 
              datetime.now().isoformat(), 1))
    
    conn.commit()
    conn.close()

# ====================== دوال التنبيهات ======================

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

def get_pending_alerts() -> List[Dict]:
    """الحصول على التنبيهات غير المرسلة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, trade_id, alert_type, message, timestamp 
        FROM alerts_log WHERE is_sent = 0 ORDER BY timestamp
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return [{"id": r[0], "trade_id": r[1], "type": r[2], "message": r[3], "timestamp": r[4]} for r in rows]

def mark_alert_sent(alert_id: int):
    """تحديد تنبيه كمرسل"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE alerts_log SET is_sent = 1 WHERE id = ?', (alert_id,))
    conn.commit()
    conn.close()

# ====================== دوال الإحصائيات ======================

def save_daily_stats():
    """حفظ إحصائيات اليوم"""
    trades = load_trades("all")
    if not trades:
        return
    
    total_invested = sum(t["entry_price"] * t["quantity"] for t in trades)
    total_current = sum(t.get("current_price", t["entry_price"]) * t["quantity"] for t in trades)
    total_profit = total_current - total_invested
    profit_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    
    winning_trades = len([t for t in trades if t.get("profit_pct", 0) > 0])
    win_rate = (winning_trades / len(trades)) * 100 if trades else 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO performance_stats (date, total_invested, total_current, 
                    total_profit, profit_pct, win_rate, trades_count, winning_trades)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d"), total_invested, total_current,
          total_profit, profit_pct, win_rate, len(trades), winning_trades))
    conn.commit()
    conn.close()

def get_performance_history(days: int = 30) -> pd.DataFrame:
    """الحصول على تاريخ الأداء"""
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM performance_stats ORDER BY date DESC LIMIT {days}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# تهيئة قاعدة البيانات عند الاستيراد
init_database()
