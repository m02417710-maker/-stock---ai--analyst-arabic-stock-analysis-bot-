# telegram_bot.py - بوت التليجرام
import requests
import streamlit as st
from typing import Dict

TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

def init_telegram() -> bool:
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
    
    icons = {"danger": "🚨", "warning": "⚠️", "success": "✅", "info": "📊", "buy": "🟢", "sell": "🔴"}
    full_message = f"{icons.get(alert_type, '📊')} *البورصجي AI*\n\n{message}"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": full_message, "parse_mode": "Markdown"}
        response = requests.post(url, data=data, timeout=10)
        return response.ok
    except:
        return False
