# market_scanner.py - الماسح الآلي للأسواق
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
from config import TECHNICAL_CONFIG, SUPPORTED_MARKETS

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """حساب مؤشر RSI"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def calculate_macd(prices: pd.Series):
    """حساب MACD"""
    try:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1], signal.iloc[-1], macd.iloc[-1] - signal.iloc[-1]
    except:
        return 0, 0, 0

def scan_stock(ticker: str) -> Dict:
    """مسح سهم واحد"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 30:
            return None
        
        current_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df['Close'])
        macd, macd_signal, macd_hist = calculate_macd(df['Close'])
        
        # المتوسطات المتحركة
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
        
        # الدعم والمقاومة
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        # تحديد الإشارة
        signal = "neutral"
        score = 0
        
        if rsi < 30:
            score += 3
            signal = "buy_strong"
        elif rsi < 40:
            score += 2
            signal = "buy"
        elif rsi > 70:
            score -= 3
            signal = "sell_strong"
        elif rsi > 60:
            score -= 2
            signal = "sell"
        
        if macd > macd_signal:
            score += 1
        
        if current_price < sma_20:
            score += 1
        
        if score >= 3:
            recommendation = "شراء قوي 🟢"
            action = "buy"
        elif score >= 1:
            recommendation = "شراء 🟡"
            action = "buy_weak"
        elif score <= -3:
            recommendation = "بيع قوي 🔴"
            action = "sell"
        elif score <= -1:
            recommendation = "مراقبة 🟠"
            action = "sell_weak"
        else:
            recommendation = "انتظار ⚪"
            action = "hold"
        
        return {
            "ticker": ticker,
            "price": current_price,
            "rsi": rsi,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "support": support,
            "resistance": resistance,
            "signal": signal,
            "recommendation": recommendation,
            "action": action,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return None

def scan_market(tickers: List[str]) -> List[Dict]:
    """مسح مجموعة من الأسهم"""
    results = []
    for ticker in tickers:
        result = scan_stock(ticker)
        if result:
            results.append(result)
    
    # ترتيب حسب قوة الإشارة
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

# قائمة الأسهم الموصى بمسحها
RECOMMENDED_TICKERS = [
    "COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "FWRY.CA",
    "2222.SR", "1120.SR", "7010.SR",
    "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"
]

def get_market_opportunities() -> List[Dict]:
    """الحصول على فرص السوق الحالية"""
    return scan_market(RECOMMENDED_TICKERS)
