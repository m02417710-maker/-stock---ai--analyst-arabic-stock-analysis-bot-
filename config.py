# config.py - الإعدادات المركزية للمشروع
import os
from pathlib import Path
from datetime import datetime

# ====================== المسارات ======================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
CACHE_DIR = BASE_DIR / "cache"

# إنشاء المجلدات
for dir_path in [DATA_DIR, LOGS_DIR, REPORTS_DIR, CACHE_DIR]:
    dir_path.mkdir(exist_ok=True)

# ====================== إعدادات التطبيق ======================
APP_CONFIG = {
    "name": "البورصجي AI",
    "version": "5.0.0",
    "author": "البورصجي AI Team",
    "description": "منصة التداول الذكية المتكاملة",
    "default_period": "1y",
    "refresh_seconds": 60,
    "max_trades": 100,
    "supported_markets": ["EGX", "TADAWUL", "US"]
}

# ====================== إعدادات إدارة المخاطر ======================
RISK_CONFIG = {
    "default_risk_percent": 2.0,
    "min_risk_reward_ratio": 1.5,
    "ideal_risk_reward_ratio": 2.0,
    "trailing_stop_default": 5.0,
    "max_position_size": 0.25,
    "daily_loss_limit": 5.0
}

# ====================== إعدادات المؤشرات الفنية ======================
TECHNICAL_CONFIG = {
    "rsi_period": 14,
    "sma_periods": [20, 50, 200],
    "ema_periods": [9, 21],
    "bb_period": 20,
    "bb_std": 2,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9
}

# ====================== الأسواق المدعومة ======================
SUPPORTED_MARKETS = {
    "EGX": {
        "name": "البورصة المصرية",
        "suffix": ".CA",
        "currency": "EGP",
        "timezone": "Africa/Cairo",
        "market_hours": "10:00-14:30",
        "flag": "🇪🇬"
    },
    "TADAWUL": {
        "name": "تداول السعودية",
        "suffix": ".SR",
        "currency": "SAR",
        "timezone": "Asia/Riyadh",
        "market_hours": "10:00-15:00",
        "flag": "🇸🇦"
    },
    "US": {
        "name": "الأسهم الأمريكية",
        "suffix": "",
        "currency": "USD",
        "timezone": "America/New_York",
        "market_hours": "09:30-16:00",
        "flag": "🇺🇸"
    }
}

# ====================== دوال مساعدة ======================
def get_market_flag(ticker: str) -> str:
    """تحديد علم السوق تلقائياً"""
    if ".CA" in ticker:
        return "🇪🇬"
    elif ".SR" in ticker:
        return "🇸🇦"
    else:
        return "🇺🇸"

def get_flexible_ticker(symbol: str) -> str:
    """دعم مرن لجميع الأسواق"""
    if "." in symbol:
        return symbol
    return f"{symbol}.CA"

def get_current_time():
    """الحصول على الوقت الحالي"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
