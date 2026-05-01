# config.py - ملف الإعدادات الأساسية
"""
ملف الإعدادات الرئيسي للتطبيق
يحتوي على جميع الثوابت والإعدادات العامة
"""

import os
from pathlib import Path
from datetime import datetime

# ====================== إصدار التطبيق ======================
APP_VERSION = "5.0.0"
APP_NAME = "Stock AI Analyst Pro"
APP_AUTHOR = "Stock AI Analyst Team"
APP_DESCRIPTION = "تحليل الأسهم المصرية والسعودية والأمريكية بالذكاء الاصطناعي"

# ====================== مسارات المشروع ======================
# الحصول على المسار الأساسي للمشروع
BASE_DIR = Path(__file__).parent

# مجلدات المشروع
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# إنشاء المجلدات إذا لم تكن موجودة
for dir_path in [CACHE_DIR, LOGS_DIR, DATA_DIR]:
    dir_path.mkdir(exist_ok=True)

# ====================== إعدادات التطبيق ======================
APP_CONFIG = {
    "name": APP_NAME,
    "version": APP_VERSION,
    "author": APP_AUTHOR,
    "description": APP_DESCRIPTION,
    "debug_mode": False,
    "default_period": "1y",
    "default_refresh_seconds": 300,
    "max_news_items": 20,
    "supported_markets": ["EGX", "TADAWUL", "ADX", "DFM", "US"]
}

# ====================== إعدادات الأمان ======================
SECURITY_CONFIG = {
    "rate_limit_per_minute": 30,
    "max_requests_per_session": 1000,
    "session_timeout_minutes": 60,
    "enable_ip_checking": True,
    "enable_request_logging": True,
    "max_input_length": 500,
    "allowed_ticker_pattern": r'^[A-Z0-9\.\^\-]{1,20}$'
}

# ====================== إعدادات API ======================
# ملاحظة: المفاتيح الحقيقية توضع في .streamlit/secrets.toml
API_CONFIG = {
    "yfinance": {
        "enabled": True,
        "timeout": 30,
        "retry_count": 3
    },
    "gemini": {
        "enabled": True,
        "model": "gemini-1.5-flash",
        "temperature": 0.7,
        "max_tokens": 1000
    }
}

# ====================== إعدادات الواجهة ======================
UI_CONFIG = {
    "theme": "dark",
    "primary_color": "#ff4b4b",
    "background_color": "#0e1117",
    "secondary_background_color": "#262730",
    "text_color": "#fafafa",
    "font": "sans serif",
    "chart_height": 600,
    "sidebar_width": 300
}

# ====================== إعدادات المؤشرات الفنية ======================
TECHNICAL_CONFIG = {
    "sma_periods": [20, 50, 200],
    "ema_periods": [9, 21],
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "bb_std": 2
}

# ====================== قائمة الأسواق المدعومة ======================
SUPPORTED_MARKETS = {
    "EGX": {
        "name": "البورصة المصرية",
        "suffix": ".CA",
        "currency": "EGP",
        "timezone": "Africa/Cairo",
        "market_hours": "10:00 - 14:30",
        "index": "^EGX30",
        "flag": "🇪🇬"
    },
    "TADAWUL": {
        "name": "تداول السعودية",
        "suffix": ".SR",
        "currency": "SAR",
        "timezone": "Asia/Riyadh",
        "market_hours": "10:00 - 15:00",
        "index": "^TASI",
        "flag": "🇸🇦"
    },
    "US": {
        "name": "الأسهم الأمريكية",
        "suffix": "",
        "currency": "USD",
        "timezone": "America/New_York",
        "market_hours": "09:30 - 16:00",
        "index": "^GSPC",
        "flag": "🇺🇸"
    }
}

# ====================== دوال مساعدة ======================

def get_config(key: str, default=None):
    """
    الحصول على قيمة إعداد معين
    """
    configs = {
        "app": APP_CONFIG,
        "security": SECURITY_CONFIG,
        "api": API_CONFIG,
        "ui": UI_CONFIG,
        "technical": TECHNICAL_CONFIG
    }
    
    for config_name, config_dict in configs.items():
        if key in config_dict:
            return config_dict[key]
    
    return default

def is_debug_mode() -> bool:
    """
    التحقق من وضع التصحيح
    """
    return APP_CONFIG.get("debug_mode", False)

def get_app_info() -> dict:
    """
    الحصول على معلومات التطبيق
    """
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "author": APP_AUTHOR,
        "description": APP_DESCRIPTION,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ====================== اختبار الملف ======================

if __name__ == "__main__":
    print(f"✅ تم تحميل {APP_NAME} الإصدار {APP_VERSION}")
    print(f"📁 المسار: {BASE_DIR}")
    print(f"🌍 الأسواق المدعومة: {len(SUPPORTED_MARKETS)}")
    print(f"🔧 وضع التصحيح: {is_debug_mode()}")
