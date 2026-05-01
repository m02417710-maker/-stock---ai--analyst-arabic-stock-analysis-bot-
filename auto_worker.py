# auto_worker.py - الماسح الآلي (يعمل في الخلفية)
import time
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json
from pathlib import Path

# ====================== إعدادات ======================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# الأسهم المستهدفة للمسح
TARGET_STOCKS = [
    "COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "EAST.CA",
    "2222.SR", "1120.SR", "7010.SR",
    "AAPL", "MSFT", "TSLA", "NVDA", "GOOGL"
]

# إعدادات تليجرام (ضع المفاتيح هنا أو في متغيرات البيئة)
TELEGRAM_BOT_TOKEN = ""  # سيتم قراءتها من secrets
TELEGRAM_CHAT_ID = ""

def send_alert(message):
    """إرسال تنبيه لتليجرام"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        try:
            requests.post(url, data=data, timeout=10)
        except:
            pass

def calculate_rsi(prices, period=14):
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def analyze_stock(ticker):
    """تحليل سهم واحد"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="2mo")
        if df.empty or len(df) < 20:
            return None
        
        current_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df['Close'])
        
        # تحديد الإشارة
        if rsi < 30:
            signal = "BUY"
            strength = "قوية"
        elif rsi < 35:
            signal = "BUY_WEAK"
            strength = "متوسطة"
        elif rsi > 70:
            signal = "SELL"
            strength = "قوية"
        else:
            signal = "HOLD"
            strength = "ضعيفة"
        
        return {
            "ticker": ticker,
            "price": current_price,
            "rsi": rsi,
            "signal": signal,
            "strength": strength,
            "timestamp": datetime.now().isoformat()
        }
    except:
        return None

def run_scanner():
    """تشغيل الماسح"""
    print(f"🔄 بدء المسح - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    opportunities = []
    
    for ticker in TARGET_STOCKS:
        analysis = analyze_stock(ticker)
        if analysis and analysis['signal'] in ['BUY', 'BUY_WEAK']:
            opportunities.append(analysis)
            print(f"  ✅ فرصة: {ticker} - RSI: {analysis['rsi']:.1f}")
    
    # إرسال التنبيهات
    if opportunities:
        for opp in opportunities[:5]:
            msg = f"""
🚀 <b>فرصة استثمارية!</b>

<b>السهم:</b> {opp['ticker']}
<b>السعر:</b> {opp['price']:.2f}
<b>RSI:</b> {opp['rsi']:.1f}
<b>القوة:</b> {opp['strength']}
<b>الإشارة:</b> {opp['signal']}
            """
            send_alert(msg)
            print(f"  📨 تم إرسال تنبيه لـ {opp['ticker']}")
    
    # حفظ النتائج
    results = {"timestamp": datetime.now().isoformat(), "opportunities": opportunities}
    with open(DATA_DIR / "scan_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ اكتمل المسح - تم العثور على {len(opportunities)} فرصة")
    return opportunities

if __name__ == "__main__":
    run_scanner()
