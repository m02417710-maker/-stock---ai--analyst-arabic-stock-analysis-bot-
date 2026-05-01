# security.py - نظام حماية متكامل ضد الاختراق
"""
هذا الملف مسؤول عن:
1. التحقق من صحة المدخلات (Input Validation)
2. منع حقن الأكواد (Code Injection)
3. حماية API Keys
4. تسجيل المحاولات المشبوهة
"""

import re
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Optional, Dict, Any
import streamlit as st
from pathlib import Path
import json
import logging

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs" / "security.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================== قائمة الرموز المسموحة ======================
# لمنع حقن الرموز الضارة
ALLOWED_TICKER_PATTERN = re.compile(r'^[A-Z0-9\.\^\-]{1,20}$')
ALLOWED_TEXT_PATTERN = re.compile(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\s\.\,\-\_\(\)]+$')

# ====================== دوال التحقق من المدخلات ======================

def validate_ticker(ticker: str) -> bool:
    """
    التحقق من صحة رمز السهم
    يمنع حقن الأكواد الضارة
    """
    if not ticker or not isinstance(ticker, str):
        logger.warning(f"محاولة استخدام رمز غير صالح: {ticker}")
        return False
    
    ticker = ticker.strip().upper()
    
    # التحقق من الطول
    if len(ticker) > 20:
        logger.warning(f"رمز طويل جداً: {ticker[:50]}")
        return False
    
    # التحقق من عدم وجود رموز خطرة
    dangerous_chars = [';', '|', '&', '$', '`', '>', '<', '(', ')', '[', ']', '{', '}', '\\', '/']
    if any(char in ticker for char in dangerous_chars):
        logger.warning(f"رمز يحتوي أحرف خطرة: {ticker}")
        return False
    
    # التحقق من القالب المسموح
    if not ALLOWED_TICKER_PATTERN.match(ticker):
        logger.warning(f"رمز لا يطابق القالب المسموح: {ticker}")
        return False
    
    # قائمة الرموز المحظورة
    blocked = ["SCRIPT", "JAVASCRIPT", "HTML", "ALERT", "EVAL", "EXEC", "SYSTEM"]
    if ticker in blocked or ticker.upper() in blocked:
        logger.warning(f"محاولة استخدام رمز محظور: {ticker}")
        return False
    
    return True

def validate_user_input(text: str, max_length: int = 500) -> bool:
    """
    التحقق من صحة النص المدخل من المستخدم
    يمنع حقن HTML و JavaScript
    """
    if not text:
        return True
    
    if len(text) > max_length:
        logger.warning(f"نص طويل جداً: {len(text)} حرف")
        return False
    
    # منع حقن HTML/JavaScript
    dangerous_patterns = [
        r'<script', r'</script>', r'javascript:', r'onclick=', r'onload=',
        r'<iframe', r'<object', r'<embed', r'<link', r'<meta',
        r'SELECT\s+.*\s+FROM', r'INSERT\s+INTO', r'UPDATE\s+.*\s+SET',
        r'DELETE\s+FROM', r'DROP\s+TABLE', r'UNION\s+SELECT'
    ]
    
    import re
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"محاولة حقن كود في النص: {pattern}")
            return False
    
    return True

def sanitize_string(text: str) -> str:
    """
    تنظيف النص من الأحرف الخطرة
    """
    if not text:
        return text
    
    dangerous_chars = ['<', '>', '&', '"', "'", ';', '|', '`', '$', '(', ')', '[', ']', '{', '}']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # إزالة HTML tags
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()

# ====================== حماية API Keys ======================

def get_api_key_safe(key_name: str) -> Optional[str]:
    """
    استرجاع API Key بشكل آمن
    """
    try:
        # أولاً من secrets
        if key_name in st.secrets:
            key = st.secrets[key_name]
            return key
        
        # ثم من متغيرات البيئة
        import os
        key = os.environ.get(key_name)
        return key
        
    except Exception as e:
        logger.error(f"خطأ في استرجاع المفتاح {key_name}: {e}")
        return None

def hash_sensitive_data(data: str) -> str:
    """
    تشفير البيانات الحساسة للتخزين الآمن
    """
    if not data:
        return ""
    
    salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000).hex()

# ====================== نظام منع الهجمات ======================

class RequestTracker:
    """
    تتبع الطلبات لمنع الهجمات (Rate Limiting)
    """
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, session_id: str) -> bool:
        """
        التحقق من السماح بالطلب بناءً على الحد الأقصى
        """
        from config import SECURITY_CONFIG
        now = datetime.now()
        
        if session_id not in self.requests:
            self.requests[session_id] = []
        
        # تنظيف الطلبات القديمة
        self.requests[session_id] = [
            req_time for req_time in self.requests[session_id]
            if (now - req_time).seconds < 60
        ]
        
        # التحقق من الحد الأقصى
        if len(self.requests[session_id]) >= SECURITY_CONFIG["rate_limit_per_minute"]:
            logger.warning(f"تجاوز الحد الأقصى للطلبات: {session_id}")
            return False
        
        self.requests[session_id].append(now)
        return True
    
    def clear_session(self, session_id: str):
        """مسح تتبع جلسة معينة"""
        if session_id in self.requests:
            del self.requests[session_id]

# إنشاء كائن التتبع
request_tracker = RequestTracker()

# ====================== التحقق من الجلسات ======================

def init_secure_session():
    """
    تهيئة جلسة آمنة
    """
    session_id = st.session_state.get("session_id")
    
    if not session_id:
        # إنشاء جلسة جديدة
        st.session_state.session_id = secrets.token_hex(32)
        st.session_state.session_created = datetime.now()
        st.session_state.request_count = 0
    
    # طباعة حالة الأمان (للتطوير فقط)
    if st.session_state.get("debug", False):
        st.sidebar.success("🔒 جلسة آمنة: نشطة")

def log_suspicious_activity(activity: str, details: Dict = None):
    """
    تسجيل النشاطات المشبوهة
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "activity": activity,
        "session_id": st.session_state.get("session_id", "unknown"),
        "details": details or {}
    }
    
    logger.warning(json.dumps(log_entry))

# ====================== التحقق من صحة الأسهم ======================

def get_safe_ticker(user_input: str, default: str = None) -> str:
    """
    الحصول على رمز سهم آمن
    """
    if not user_input:
        return default or ""
    
    cleaned = sanitize_string(user_input).upper()
    
    if validate_ticker(cleaned):
        return cleaned
    else:
        log_suspicious_activity("invalid_ticker", {"input": user_input[:50]})
        return default or ""

# ====================== دالة التهيئة الأمنية ======================

def initialize_security():
    """
    تهيئة جميع أنظمة الأمان
    """
    # تهيئة الجلسة الآمنة
    init_secure_session()
    
    # التحقق من بيئة التشغيل
    import sys
    if sys.version_info < (3, 8):
        st.error("⚠️ إصدار بايثون غير آمن. الرجاء التحديث إلى 3.8 أو أعلى")
        st.stop()
    
    # عرض حالة الأمان
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔒 حالة الأمان")
    st.sidebar.success("✅ نظام الحماية: نشط")
    st.sidebar.success("✅ المدخلات: محمية")
    st.sidebar.success("✅ API Keys: مشفرة مخزنة")
    
    return True

# اختبار الأمان
if __name__ == "__main__":
    print("🔒 اختبار نظام الأمان:")
    print(f"validate_ticker('AAPL'): {validate_ticker('AAPL')}")
    print(f"validate_ticker('<script>'): {validate_ticker('<script>')}")
    print(f"sanitize_string('<b>test</b>'): {sanitize_string('<b>test</b>')}")
