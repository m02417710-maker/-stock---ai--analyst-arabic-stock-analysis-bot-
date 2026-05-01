# ============================================================
# ملف: config.py
# الإعدادات المركزية والتكوينات
# ============================================================

APP_CONFIG = {
    "title": "المحلل المصري المتكامل - AI Edition",
    "version": "4.0.0",
    "icon": "🧠",
    "layout": "wide",
    "auto_refresh_interval": 60000,
}

ANALYSIS_CONFIG = {
    "chart_height": 800,
    "simulation_days": 30,
    "simulation_count": 5000,
    "risk_percent": 2.0,
    "target_percent": 7.0,
    "stop_percent": 5.0,
}

TECHNICAL_CONFIG = {
    "rsi_length": 14,
    "ma_short": 20,
    "ma_long": 50,
    "bb_length": 20,
    "bb_std": 2,
}

COLORS = {
    "primary": "#10b981",
    "secondary": "#3b82f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#06b6d4",
    "dark": "#0f172a",
    "light": "#1e293b",
    "chart_up": "#10b981",
    "chart_down": "#ef4444",
}

MACRO_CONFIG = {
    "egypt_interest_rate": 19.0,
    "next_meeting": "21 مايو 2026",
    "inflation": "12.8%",
    "oil_price": 85.5,
    "gold_price": 2350,
    "usd_egp": 48.5,
}
