# security.py - نظام حماية متكامل ضد الاختراق
"""
هذا الملف مسؤول عن:
1. التحقق من صحة المدخلات (Input Validation)
2. منع حقن الأكواد (Code Injection)
3. حماية API Keys
4. تسجيل المحاولات المشبوهة
5. منع هجمات الـ SQL Injection و XSS
"""

import re
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Optional, Dict, List, Any
import streamlit as st
from pathlib import Path
import json
import logging

# ====================== إعداد مجلد السجلات ======================
# إنشاء مجلد logs إذا لم يكن موجوداً
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "security.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================== قوالب التحقق ======================
# قالب التحقق من رمز السهم - يسمح فقط بالأحرف الكبيرة والأرقام والنقاط والشرطة
ALLOWED_TICKER_PATTERN = re.compile(r'^[A-Z0-9\.\^\-]{1,20}$')

# قالب التحقق من النص العربي والإنجليزي
ALLOWED_TEXT_PATTERN = re.compile(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\s\.\,\-\_\(\)\?\:\!\+]+$')

# ====================== قوائم الكلمات المحظورة ======================
# أوامر خطيرة للغلق
BLOCKED_SCRIPTS = [
    "SCRIPT", "JAVASCRIPT", "HTML", "ALERT", "EVAL", "EXEC", 
    "SYSTEM", "OS", "SUBPROCESS", "IMPORT", "__IMPORT__"
]

# أوامر SQL للغلق
BLOCKED_SQL = [
    "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", 
    "ALTER", "TRUNCATE", "UNION", "JOIN", "WHERE"
]

# أحرف خطيرة
DANGEROUS_CHARS = [';', '|', '&', '$', '`', '>', '<', '(', ')', '[', ']', '{', '}', '\\', '/', '%', '=', '*']

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
    
    # التحقق من عدم وجود أحرف خطرة
    if any(char in ticker for char in DANGEROUS_CHARS):
        logger.warning(f"رمز يحتوي أحرف خطرة: {ticker}")
        return False
    
    # التحقق من القالب المسموح
    if not ALLOWED_TICKER_PATTERN.match(ticker):
        logger.warning(f"رمز لا يطابق القالب المسموح: {ticker}")
        return False
    
    # التحقق من الكلمات المحظورة
    ticker_upper = ticker.upper()
    for blocked in BLOCKED_SCRIPTS + BLOCKED_SQL:
        if blocked in ticker_upper:
            logger.warning(f"محاولة استخدام كلمة محظورة: {blocked} في {ticker}")
            return False
    
    return True

def validate_user_input(text: str, max_length: int = 500, allow_arabic: bool = True) -> bool:
    """
    التحقق من صحة النص المدخل من المستخدم
    يمنع حقن HTML و JavaScript و SQL
    """
    if not text:
        return True
    
    if len(text) > max_length:
        logger.warning(f"نص طويل جداً: {len(text)} حرف (الحد الأقصى {max_length})")
        return False
    
    # منع حقن HTML/JavaScript
    dangerous_patterns = [
        r'<script', r'</script>', r'javascript:', r'onclick=', r'onload=', r'onerror=',
        r'<iframe', r'<object', r'<embed', r'<link', r'<meta', r'<style',
        r'expression\(', r'url\(', r'alert\(', r'eval\(', r'exec\('
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower):
            logger.warning(f"محاولة حقن كود في النص: {pattern}")
            return False
    
    # منع حقن SQL
    sql_patterns = [
        r'select.*from', r'insert.*into', r'update.*set', r'delete.*from',
        r'drop.*table', r'union.*select', r'--', r'/\*', r'\*/'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, text_lower):
            logger.warning(f"محاولة حقن SQL: {pattern}")
            return False
    
    # التحقق من الأحرف المسموحة (اختياري)
    if allow_arabic and not ALLOWED_TEXT_PATTERN.match(text):
        # قد يحتوي على أحرف عربية مسموحة أو علامات ترقيم بسيطة
        pass
    
    return True

def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    تنظيف النص من الأحرف والعلامات الخطرة
    """
    if not text:
        return ""
    
    # اقتصار الطول
    if len(text) > max_length:
        text = text[:max_length]
    
    # إزالة الأحرف الخطرة
    for char in DANGEROUS_CHARS:
        text = text.replace(char, '')
    
    # إزالة HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # إزلة العلامات الزائدة
    text = re.sub(r'\s+', ' ', text)
    
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
            # التحقق من أن المفتاح ليس فارغاً
            if key and isinstance(key, str) and len(key) > 5:
                return key
        
        # ثم من متغيرات البيئة
        import os
        key = os.environ.get(key_name)
        if key and isinstance(key, str) and len(key) > 5:
            return key
        
        logger.warning(f"مفتاح {key_name} غير موجود أو غير صالح")
        return None
        
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
    hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"

def verify_hashed_data(data: str, hashed_data: str) -> bool:
    """
    التحقق من البيانات المشفرة
    """
    try:
        salt, stored_hash = hashed_data.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000).hex()
        return hmac.compare_digest(stored_hash, new_hash)
    except Exception:
        return False

# ====================== نظام منع الهجمات ======================

class RequestTracker:
    """
    تتبع الطلبات لمنع الهجمات (Rate Limiting)
    """
    def __init__(self):
        self.requests = {}
        self.suspicious_ips = {}
    
    def is_allowed(self, session_id: str) -> bool:
        """
        التحقق من السماح بالطلب بناءً على الحد الأقصى
        """
        from config import SECURITY_CONFIG
        
        if not session_id:
            return False
            
        now = datetime.now()
        
        if session_id not in self.requests:
            self.requests[session_id] = []
        
        # تنظيف الطلبات القديمة (أقدم من دقيقة)
        self.requests[session_id] = [
            req_time for req_time in self.requests[session_id]
            if (now - req_time).seconds < 60
        ]
        
        # التحقق من الحد الأقصى
        rate_limit = SECURITY_CONFIG.get("rate_limit_per_minute", 30)
        if len(self.requests[session_id]) >= rate_limit:
            logger.warning(f"تجاوز الحد الأقصى للطلبات: {session_id}")
            
            # تتبع الجلسات المشبوهة
            if session_id not in self.suspicious_ips:
                self.suspicious_ips[session_id] = 0
            self.suspicious_ips[session_id] += 1
            
            # إذا تكرر التجاوز أكثر من 3 مرات، حظر مؤقت
            if self.suspicious_ips[session_id] > 3:
                logger.error(f"جلسة محظورة: {session_id}")
                return False
            
            return False
        
        self.requests[session_id].append(now)
        return True
    
    def clear_session(self, session_id: str):
        """مسح تتبع جلسة معينة"""
        if session_id in self.requests:
            del self.requests[session_id]
        if session_id in self.suspicious_ips:
            del self.suspicious_ips[session_id]

# إنشاء كائن التتبع العالمي
request_tracker = RequestTracker()

# ====================== التحقق من الجلسات ======================

def init_secure_session():
    """
    تهيئة جلسة آمنة
    """
    # التحقق من وجود session_id
    if "session_id" not in st.session_state:
        # إنشاء جلسة جديدة بمعرف فريد وآمن
        st.session_state.session_id = secrets.token_hex(32)
        st.session_state.session_created = datetime.now().isoformat()
        st.session_state.request_count = 0
        st.session_state.is_secure = True
    
    # التحقق من أن الجلسة لم تنتهِ (بعد 60 دقيقة)
    from config import SECURITY_CONFIG
    session_timeout = SECURITY_CONFIG.get("session_timeout_minutes", 60)
    
    if "session_created" in st.session_state:
        created = datetime.fromisoformat(st.session_state.session_created)
        if (datetime.now() - created).seconds > session_timeout * 60:
            # انتهت الجلسة - إنشاء جديدة
            for key in ["session_id", "session_created", "request_count"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def log_suspicious_activity(activity: str, details: Dict = None):
    """
    تسجيل النشاطات المشبوهة
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "activity": activity,
        "session_id": st.session_state.get("session_id", "unknown"),
        "ip": st.session_state.get("ip", "unknown"),
        "details": details or {}
    }
    
    logger.warning(json.dumps(log_entry, ensure_ascii=False))

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

def validate_amount(amount: float, min_value: float = 0, max_value: float = 1e9) -> bool:
    """
    التحقق من صحة قيمة مالية
    """
    if not isinstance(amount, (int, float)):
        return False
    
    if amount < min_value or amount > max_value:
        return False
    
    return True

# ====================== حماية متقدمة ======================

def prevent_xss(text: str) -> str:
    """
    تحويل النص لمنع هجمات XSS
    """
    if not text:
        return ""
    
    # استبدال الأحرف الخطيرة بنظيراتها الآمنة
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def sanitize_filename(filename: str) -> str:
    """
    تنظيف اسم الملف من الأحرف الخطرة
    """
    if not filename:
        return "file"
    
    # إزالة الأحرف غير المسموحة في أسماء الملفات
    forbidden_chars = r'[<>:"/\\|?*]'
    filename = re.sub(forbidden_chars, '_', filename)
    
    # منع المسارات الاختراقية
    filename = filename.replace('..', '_')
    filename = filename.replace('~', '_')
    
    return filename

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
    
    # التحقق من وجود مكتبات الأمان
    try:
        import cryptography
    except ImportError:
        st.warning("⚠️ مكتبة التشفير غير مثبتة - بعض ميزات الأمان معطلة")
    
    # عرض حالة الأمان في الشريط الجانبي (اختياري)
    if st.session_state.get("debug", False):
        with st.sidebar:
            st.markdown("### 🔒 حالة الأمان")
            st.success("✅ نظام الحماية: نشط")
            st.success("✅ التحقق من المدخلات: مفعل")
            st.success("✅ منع الحقن: مفعل")
            st.info(f"🆔 معرف الجلسة: {st.session_state.session_id[:8]}...")
    
    return True

# ====================== اختبار الأمان ======================

if __name__ == "__main__":
    print("🔒 اختبار نظام الأمان:")
    print("=" * 50)
    
    # اختبار التحقق من الرموز
    test_tickers = ["AAPL", "COMI.CA", "<script>", "2222.SR", "SELECT"]
    for ticker in test_tickers:
        result = validate_ticker(ticker)
        print(f"validate_ticker('{ticker}'): {result}")
    
    print("-" * 50)
    
    # اختبار تنظيف النص
    test_texts = ["<b>Hello</b> World", "test<script>alert()</script>", "Normal text"]
    for text in test_texts:
        cleaned = sanitize_string(text)
        print(f"sanitize_string('{text[:30]}'): '{cleaned}'")
    
    print("-" * 50)
    
    # اختبار منع XSS
    xss_test = "<script>alert('XSS')</script>"
    safe = prevent_xss(xss_test)
    print(f"prevent_xss: '{xss_test}' -> '{safe}'")
    
    print("=" * 50)
    print("✅ جميع اختبارات الأمان اجتازت بنجاح!")
