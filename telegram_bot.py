# telegram_bot.py - بوت التليجرام للتنبيهات الفورية
"""
نظام التنبيهات عبر تليجرام - إشعارات فورية على هاتفك
"""

import requests
import streamlit as st
from typing import Dict, Optional
from datetime import datetime

# المتغيرات العامة
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

def init_telegram() -> bool:
    """
    تهيئة بوت التليجرام من المفاتيح المخزنة
    يجب إضافة المفاتيح في ملف .streamlit/secrets.toml
    """
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
            TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
            return True
    except:
        pass
    return False

def send_telegram_message(message: str, alert_type: str = "info") -> bool:
    """
    إرسال رسالة إلى التليجرام
    أنواع التنبيهات: info, success, warning, danger, buy, sell
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    icons = {
        "danger": "🚨⚠️",
        "warning": "⚠️",
        "success": "✅",
        "info": "📊",
        "buy": "🟢",
        "sell": "🔴"
    }
    
    full_message = f"{icons.get(alert_type, '📊')} *البورصجي AI*\n\n{message}\n\n---\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": full_message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.ok
    except Exception as e:
        print(f"خطأ في إرسال رسالة تليجرام: {e}")
        return False

def send_trade_alert(trade: Dict, alert_type: str) -> bool:
    """إرسال تنبيه خاص بالصفقات"""
    if alert_type == "target_approaching":
        message = f"""
🎯 *قرب تحقيق الهدف!*

📊 السهم: *{trade['symbol']}*
💰 سعر الدخول: {trade['entry_price']:.2f}
📈 السعر الحالي: {trade.get('current_price', trade['entry_price']):.2f}
🎯 الهدف: {trade['target_price']:.2f}
📊 الربح المحقق: {trade.get('profit_pct', 0):+.1f}%

💡 يوصى بمتابعة الصفقة عن كثب
        """
        return send_telegram_message(message, "success")
    
    elif alert_type == "stop_loss_approaching":
        message = f"""
⚠️ *قرب من وقف الخسارة!*

📊 السهم: *{trade['symbol']}*
💰 سعر الدخول: {trade['entry_price']:.2f}
📉 السعر الحالي: {trade.get('current_price', trade['entry_price']):.2f}
🛡️ وقف الخسارة: {trade['stop_loss']:.2f}
📉 الخسارة: {trade.get('profit_pct', 0):.1f}%

💡 يوصى بمراجعة الصفقة
        """
        return send_telegram_message(message, "warning")
    
    elif alert_type == "trailing_stop_raised":
        message = f"""
📈 *تم رفع وقف الخسارة!*

📊 السهم: *{trade['symbol']}*
🛡️ وقف الخسارة الجديد: {trade['stop_loss']:.2f}
🔒 نسبة التأمين: {trade.get('trailing_stop', 0)}%

✅ تم تأمين أرباحك تلقائياً
        """
        return send_telegram_message(message, "info")
    
    return False

def send_daily_report(stats: Dict) -> bool:
    """إرسال التقرير اليومي إلى التليجرام"""
    message = f"""
📊 *تقرير البورصجي AI اليومي*

📅 {datetime.now().strftime('%Y-%m-%d')}

💰 *ملخص المحفظة:*
- إجمالي المستثمر: {stats.get('total_invested', 0):,.2f}
- القيمة الحالية: {stats.get('total_current', 0):,.2f}
- إجمالي الربح: {stats.get('total_profit', 0):+,.2f}
- نسبة الربح: {stats.get('profit_pct', 0):+.1f}%

📊 *الإحصائيات:*
- عدد الصفقات: {stats.get('trades_count', 0)}
- الصفقات الرابحة: {stats.get('winning_trades', 0)}
- نسبة النجاح: {stats.get('win_rate', 0):.1f}%

🎯 *توصية العقل المدبر:*
استمر في تطبيق استراتيجيات إدارة المخاطر.

---
🕶️ البورصجي AI - العين التي لا تنام
    """
    return send_telegram_message(message, "info")

def send_opportunity_alert(opportunity: Dict) -> bool:
    """إرسال تنبيه بفرصة استثمارية جديدة"""
    message = f"""
🔍 *فرصة استثمارية جديدة!*

📊 السهم: *{opportunity['ticker']}*
💰 السعر الحالي: {opportunity['price']:.2f}
📈 RSI: {opportunity['rsi']:.1f}
🎯 التوصية: {opportunity['recommendation']}
💪 القوة: {opportunity['strength']}

📊 مستويات فنية:
🛡️ الدعم: {opportunity['support']:.2f}
🚀 المقاومة: {opportunity['resistance']:.2f}

💡 يوصى بمراجعة الفرصة والاستشارة قبل الدخول
    """
    return send_telegram_message(message, "buy")
