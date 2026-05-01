# market_scanner.py - الماسح الآلي للأسواق
"""
نظام المسح الآلي للأسواق - يبحث عن فرص الاستثمار
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from config import TECHNICAL_CONFIG

# ====================== المؤشرات الفنية ======================

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    حساب مؤشر القوة النسبية (RSI)
    - أقل من 30: منطقة ذروة بيع (فرصة شراء)
    - أعلى من 70: منطقة ذروة شراء (فرصة بيع)
    """
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
    """
    حساب مؤشر MACD
    - تقاطع MACD فوق الخط الإشارة: إشارة شراء
    - تقاطع MACD تحت الخط الإشارة: إشارة بيع
    """
    try:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]
    except:
        return 0, 0, 0

def scan_stock(ticker: str) -> Optional[Dict]:
    """
    مسح وتحليل سهم واحد
    إرجاع تحليل كامل يشمل السعر، المؤشرات، والتوصية
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 30:
            return None
        
        current_price = df['Close'].iloc[-1]
        rsi = calculate_rsi(df['Close'])
        
        # المتوسطات المتحركة
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
        
        # مستويات الدعم والمقاومة
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        # تحديد قوة الإشارة
        score = 0
        reasons = []
        
        # تحليل RSI
        if rsi < 30:
            score += 3
            reasons.append(f"RSI منخفض جداً ({rsi:.1f}) - منطقة ذروة بيع")
        elif rsi < 40:
            score += 2
            reasons.append(f"RSI منخفض ({rsi:.1f}) - فرصة شراء")
        elif rsi > 70:
            score -= 3
            reasons.append(f"RSI مرتفع جداً ({rsi:.1f}) - منطقة ذروة شراء")
        elif rsi > 60:
            score -= 2
            reasons.append(f"RSI مرتفع ({rsi:.1f}) - خطر تصحيح")
        
        # تحليل السعر مقابل المتوسطات
        if current_price < sma_20:
            score += 1
            reasons.append("السعر أقل من المتوسط 20 - فرصة شراء")
        elif current_price > sma_20 * 1.1:
            score -= 1
            reasons.append("السعر مرتفع عن المتوسط 20 - خطر")
        
        # تحديد التوصية النهائية
        if score >= 3:
            recommendation = "شراء قوي 🟢"
            action = "buy"
            strength = "قوية جداً"
        elif score >= 1:
            recommendation = "شراء 🟡"
            action = "buy_weak"
            strength = "متوسطة"
        elif score <= -3:
            recommendation = "بيع قوي 🔴"
            action = "sell"
            strength = "قوية جداً"
        elif score <= -1:
            recommendation = "مراقبة 🟠"
            action = "sell_weak"
            strength = "متوسطة"
        else:
            recommendation = "انتظار ⚪"
            action = "hold"
            strength = "ضعيفة"
        
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
            "strength": strength,
            "score": score,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return None

def get_market_opportunities() -> List[Dict]:
    """
    مسح السوق بالكامل والحصول على جميع فرص الاستثمار
    """
    # قائمة الأسهم المستهدفة للمسح
    target_tickers = [
        # البورصة المصرية
        "COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "FWRY.CA",
        # بورصة السعودية
        "2222.SR", "1120.SR", "7010.SR",
        # الأسهم الأمريكية
        "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN"
    ]
    
    results = []
    for ticker in target_tickers:
        result = scan_stock(ticker)
        if result:
            results.append(result)
    
    # ترتيب النتائج حسب قوة الإشارة
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def get_buy_opportunities() -> List[Dict]:
    """الحصول على فرص الشراء فقط"""
    opportunities = get_market_opportunities()
    return [opp for opp in opportunities if opp['action'] in ['buy', 'buy_weak']]
