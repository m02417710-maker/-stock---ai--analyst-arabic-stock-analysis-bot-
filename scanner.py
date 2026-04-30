# ============================================================
# ملف: scanner.py
# الماسح التلقائي - يعمل عبر GitHub Actions أو Cron Job
# ============================================================

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
from datetime import datetime
import time
import os

# إعدادات تيليجرام (ضعها في GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# قائمة الأسهم للمسح
STOCKS_LIST = {
    "البنك التجاري الدولي": "COMI.CA",
    "طلعت مصطفى": "TMGH.CA",
    "فوري": "FWRY.CA",
    "أرامكو": "2222.SR",
    "الراجحي": "1120.SR",
    "آبل": "AAPL",
    "تسلا": "TSLA",
    "مايكروسوفت": "MSFT",
    "إنفيديا": "NVDA"
}

def send_telegram_message(message):
    """إرسال رسالة تيليجرام"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"خطأ في الإرسال: {e}")
            return False
    return False

def analyze_stock(ticker, name):
    """تحليل سهم واحد وإرجاع النتائج"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo", interval="1d")
        
        if df.empty or len(df) < 20:
            return None
        
        # حساب المؤشرات
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        
        current_price = df['Close'].iloc[-1]
        rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
        
        # شروط الإشارات
        signals = []
        
        # شراء: RSI في منطقة ذروة بيع
        if rsi < 30:
            signals.append(f"🟢 **إشارة شراء قوية** - RSI: {rsi:.1f}")
        
        # شراء: اختراق المتوسط 20
        elif df['Close'].iloc[-1] > df['MA20'].iloc[-1] and df['Close'].iloc[-2] <= df['MA20'].iloc[-2]:
            signals.append(f"📈 **اختراق صاعد** - تجاوز المتوسط المتحرك 20")
        
        # بيع: RSI في منطقة ذروة شراء
        elif rsi > 70:
            signals.append(f"🔴 **إشارة بيع** - RSI في منطقة ذروة شراء: {rsi:.1f}")
        
        # بيع: كسر المتوسط 20
        elif df['Close'].iloc[-1] < df['MA20'].iloc[-1] and df['Close'].iloc[-2] >= df['MA20'].iloc[-2]:
            signals.append(f"📉 **كسر هابط** - نزل تحت المتوسط المتحرك 20")
        
        if signals:
            return {
                "name": name,
                "ticker": ticker,
                "price": current_price,
                "rsi": rsi,
                "signals": signals,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        return None
        
    except Exception as e:
        print(f"خطأ في تحليل {ticker}: {e}")
        return None

def run_scanner():
    """تشغيل الماسح الضوئي"""
    print(f"🔄 بدء المسح التلقائي - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    alerts = []
    
    for name, ticker in STOCKS_LIST.items():
        print(f"جاري تحليل {name}...")
        result = analyze_stock(ticker, name)
        if result:
            alerts.append(result)
    
    # إرسال التنبيهات
    if alerts:
        message = f"🔔 <b>تنبيهات الماسح التلقائي</b>\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for alert in alerts:
            message += f"📊 <b>{alert['name']}</b> ({alert['ticker']})\n"
            message += f"💰 السعر: {alert['price']:.2f}\n"
            for sig in alert['signals']:
                message += f"{sig}\n"
            message += f"---\n"
        
        send_telegram_message(message)
        print(f"✅ تم إرسال {len(alerts)} تنبيه")
    else:
        print("ℹ️ لا توجد إشارات جديدة")
    
    print(f"✅ اكتمل المسح - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_scanner()
