# telegram_bot.py - بوت التليجرام المتكامل
import requests
import streamlit as st
from typing import Dict, List
from datetime import datetime

TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

def init_telegram():
    """تهيئة بوت التليجرام"""
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
    """إرسال رسالة إلى التليجرام"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    icons = {
        "danger": "🚨",
        "warning": "⚠️",
        "success": "✅",
        "info": "📊",
        "buy": "🟢",
        "sell": "🔴"
    }
    
    full_message = f"{icons.get(alert_type, '📊')} *البورصجي AI*\n\n{message}"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": full_message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.ok
    except:
        return False

def send_trade_alert(trade: Dict, alert_type: str):
    """إرسال تنبيه خاص بالصفقات"""
    if alert_type == "target_approaching":
        message = f"""
🎯 *قرب تحقيق الهدف!*

السهم: {trade['symbol']}
سعر الدخول: {trade['entry_price']:.2f}
السعر الحالي: {trade.get('current_price', trade['entry_price']):.2f}
الهدف: {trade['target_price']:.2f}
الربح المحقق: {trade.get('profit_pct', 0):+.1f}%

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return send_telegram_message(message, "success")
    
    elif alert_type == "stop_loss_approaching":
        message = f"""
⚠️ *قرب من وقف الخسارة!*

السهم: {trade['symbol']}
سعر الدخول: {trade['entry_price']:.2f}
السعر الحالي: {trade.get('current_price', trade['entry_price']):.2f}
وقف الخسارة: {trade['stop_loss']:.2f}
الخسارة: {trade.get('profit_pct', 0):.1f}%

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return send_telegram_message(message, "warning")
    
    elif alert_type == "trailing_stop_raised":
        message = f"""
📈 *تم رفع وقف الخسارة!*

السهم: {trade['symbol']}
وقف الخسارة الجديد: {trade['stop_loss']:.2f}
نسبة التأمين: {trade.get('trailing_stop', 0)}%

🔒 تم تأمين أرباحك تلقائياً!

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return send_telegram_message(message, "info")
    
    return False

def send_daily_report(summary: Dict):
    """إرسال التقرير اليومي"""
    message = f"""
📊 *تقرير البورصجي AI اليومي*

📅 {datetime.now().strftime('%Y-%m-%d')}

💰 *ملخص المحفظة:*
- إجمالي المستثمر: {summary.get('total_invested', 0):,.2f}
- القيمة الحالية: {summary.get('total_current', 0):,.2f}
- إجمالي الربح: {summary.get('total_profit', 0):+,.2f}
- نسبة الربح: {summary.get('profit_pct', 0):+.1f}%

📊 *الإحصائيات:*
- عدد الصفقات: {summary.get('trades_count', 0)}
- الصفقات الرابحة: {summary.get('winning_trades', 0)}
- نسبة النجاح: {summary.get('win_rate', 0):.1f}%

🎯 *توصية العقل المدبر:*
{summary.get('recommendation', 'استمر في تطبيق استراتيجيتك')}

---
🕶️ البورصجي AI - العين التي لا تنام
        """
    return send_telegram_message(message, "info")
