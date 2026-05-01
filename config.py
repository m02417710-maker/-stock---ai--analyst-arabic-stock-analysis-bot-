# config.py - ملف الإعدادات المركزي
"""
هذا الملف يحتوي على جميع إعدادات التطبيق والثوابت
يمكن تعديله بسهولة دون التأثير على بقية الأكواد
"""

import os
from pathlib import Path
from datetime import datetime

# ====================== مسارات المشروع ======================
BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# إنشاء المجلدات إذا لم تكن موجودة
for dir_path in [CACHE_DIR, LOGS_DIR, DATA_DIR]:
    dir_path.mkdir(exist_ok=True)

# ====================== إعدادات API ======================
# أخبار ثاندر (Thndr) - ملاحظة: ثاندر منصة تداول مصرية
# للحصول على أخبار ثاندر بشكل رسمي، تحتاج إلى:
# 1. متابعة حسابهم الرسمي على وسائل التواصل
# 2. استخدام RSS feeds إن وجدت
# 3. أو استخدام مصادر مثل Benzinga التي تغطي أخبار الشركات المصرية

THNDR_NEWS_SOURCES = {
    "rss_url": "https://blog.thndr.app/feed/",  # مدونة ثاندر الرسمية
    "social_telegram": "https://t.me/thndr_egypt",
    "social_instagram": "https://instagram.com/thndr_app",
    "facebook_page": "https://facebook.com/thndrapp"
}

THNDR_TICKERS = {
    "CIB": "البنك التجاري الدولي - متاح على ثاندر",
    "TMGH": "طلعت مصطفى - متاح على ثاندر",
    "SWDY": "السويدي - متاح على ثاندر",
    "ETEL": "تليكوم مصر - متاح على ثاندر"
}

# ====================== إعدادات الأخبار ======================
# مصادر الأخبار المتاحة (بدون API Keys للخدمات المجانية)
NEWS_SOURCES = {
    # مصادر مجانية تماماً
    "free": {
        "yahoo_finance": {
            "enabled": True,
            "requires_api_key": False,
            "description": "أخبار Yahoo Finance - مجاني"
        }
    },
    
    # مصادر تحتاج API Key (يمكن الحصول عليها مجاناً بحدود)
    "requires_key": {
        "benzinga": {
            "enabled": True,
            "requires_api_key": True,
            "free_tier_limit": 500,
            "signup_url": "https://www.benzinga.com/apis/",
            "description": "Benzinga News API - 500 طلب/شهر مجاناً"
        },
        "finnhub": {
            "enabled": True,
            "requires_api_key": True,
            "free_tier_limit": 60,
            "signup_url": "https://finnhub.io/register",
            "description": "Finnhub API - 60 طلب/دقيقة مجاناً"
        }
    }
}

# ====================== إعدادات الأمان ======================
SECURITY_CONFIG = {
    "rate_limit_per_minute": 30,
    "max_requests_per_session": 1000,
    "session_timeout_minutes": 60,
    "enable_ip_checking": True,
    "enable_request_logging": True
}

# ====================== إعدادات التطبيق ======================
APP_CONFIG = {
    "app_name": "Stock AI Analyst Pro",
    "version": "5.0.0",
    "debug_mode": False,
    "default_period": "1y",
    "default_refresh_seconds": 300,
    "supported_markets": ["EGX", "TADAWUL", "ADX", "DFM", "US"]
}

# الإصدار
__version__ = "5.0.0"
__author__ = "Stock AI Analyst Team"
__last_update__ = datetime.now().strftime("%Y-%m-%d")
