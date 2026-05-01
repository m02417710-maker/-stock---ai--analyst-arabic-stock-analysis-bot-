# market_scanner.py - الماسح الآلي للأسواق
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
from config import TECHNICAL_CONFIG

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

def scan_stock(ticker: str) -> Dict:
    """مسح سهم واحد"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 30:
            return None
        
        current_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df['Close'])
        
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        # تحديد الإشارة
        score = 0
        if rsi < 30:
            score += 3
            recommendation = "شراء قوي 🟢"
            action = "buy"
        elif rsi < 40:
            score += 2
            recommendation = "شراء 🟡"
            action = "buy_weak"
        elif rsi > 70:
            score -= 3
            recommendation = "بيع قوي 🔴"
            action = "sell"
        elif rsi > 60:
            score -= 2
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
            "recommendation": recommendation,
            "action": action,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return None

def get_market_opportunities() -> List[Dict]:
    """الحصول على فرص السوق الحالية"""
    tickers = ["COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "AAPL", "MSFT", "NVDA", "TSLA"]
    results = []
    
    for ticker in tickers:
        result = scan_stock(ticker)
        if result:
            results.append(result)
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
