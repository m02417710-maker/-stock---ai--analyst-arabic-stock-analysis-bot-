# config.py - إعدادات المشروع المركزية
import os
from pathlib import Path

# المسارات الأساسية
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"

# إنشاء المجلدات إذا لم تكن موجودة
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# إعدادات API (من متغيرات البيئة أو secrets)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# إعدادات التطبيق
APP_NAME = "البورصجي AI"
APP_VERSION = "3.0.0"
APP_AUTHOR = "SahmAI Analyst Team"

# إعدادات التحليل
RSI_OVERBOUGHT = 70  # ذروة شراء
RSI_OVERSOLD = 30     # ذروة بيع
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"

# إعدادات التحديث التلقائي
UPDATE_INTERVAL_HOURS = 1  # تحديث كل ساعة

# الأسواق المدعومة
SUPPORTED_MARKETS = ["EGX", "TADAWUL", "NASDAQ", "NYSE"]
