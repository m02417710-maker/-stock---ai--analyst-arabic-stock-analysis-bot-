# core.py - المحرك الذكي للتحليل الفني
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import numpy as np
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from database import get_all_stocks, search_stock, get_market_statistics, MARKETS_DATA

# تحميل قاعدة البيانات
ALL_STOCKS_DATA = get_all_stocks()
STOCK_NAMES = list(ALL_STOCKS_DATA.keys())
STOCK_TICKERS = {name: data['ticker'] for name, data in ALL_STOCKS_DATA.items()}
STOCK_METADATA = {name: {
    'market': data['market'],
    'market_name': data['market_name'],
    'currency': data['currency']
} for name, data in ALL_STOCKS_DATA.items()}

def get_stock_data_advanced(ticker: str, period: str = "1y") -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
    """جلب بيانات متقدمة مع 20+ مؤشر فني"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None
        
        # المؤشرات الأساسية
        df['SMA_10'] = ta.sma(df['Close'], length=10)
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['SMA_50'] = ta.sma(df['Close'], length=50)
        df['EMA_9'] = ta.ema(df['Close'], length=9)
        df['EMA_21'] = ta.ema(df['Close'], length=21)
        
        # مؤشرات الزخم
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['RSI_7'] = ta.rsi(df['Close'], length=7)
        
        # مؤشرات التذبذب
        macd = ta.macd(df['Close'])
        if macd is not None:
            df['MACD'] = macd['MACD_12_26_9']
            df['MACD_Signal'] = macd['MACDs_12_26_9']
            df['MACD_Histogram'] = macd['MACDh_12_26_9']
        
        # بولينجر باندز
        bb = ta.bbands(df['Close'], length=20)
        if bb is not None:
            df['BB_Upper'] = bb['BBU_20_2.0']
            df['BB_Middle'] = bb['BBM_20_2.0']
            df['BB_Lower'] = bb['BBL_20_2.0']
        
        # مؤشرات التداول
        df['Volume_SMA'] = ta.sma(df['Volume'], length=20)
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        # مؤشرات إضافية
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['STOCH_K'] = ta.stoch(df['High'], df['Low'], df['Close']).iloc[:, 0] if ta.stoch(df['High'], df['Low'], df['Close']) is not None else 50
        df['STOCH_D'] = ta.stoch(df['High'], df['Low'], df['Close']).iloc[:, 1] if ta.stoch(df['High'], df['Low'], df['Close']) is not None else 50
        
        return df, stock.info
        
    except Exception as e:
        print(f"خطأ في جلب {ticker}: {e}")
        return None, None

def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[List[float], List[float]]:
    """حساب نقاط الدعم والمقاومة تلقائياً"""
    if df.empty or len(df) < window:
        return [], []
    
    recent_df = df.tail(window)
    resistance_levels = []
    support_levels = []
    
    # أعلى 3 قمم
    peaks = recent_df['High'].nlargest(3).tolist()
    resistance_levels = sorted(peaks, reverse=True)
    
    # أدنى 3 قيعان  
    troughs = recent_df['Low'].nsmallest(3).tolist()
    support_levels = sorted(troughs)
    
    return resistance_levels, support_levels

def calculate_fibonacci_levels(df: pd.DataFrame) -> Dict[str, float]:
    """حساب مستويات فيبوناتشي"""
    if df.empty:
        return {}
    
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low
    
    return {
        '0%': high,
        '23.6%': high - diff * 0.236,
        '38.2%': high - diff * 0.382,
        '50%': high - diff * 0.5,
        '61.8%': high - diff * 0.618,
        '78.6%': high - diff * 0.786,
        '100%': low
    }

def get_market_sentiment(ticker: str) -> Dict:
    """تحليل معنويات السوق"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return {}
        
        current = hist['Close'].iloc[-1]
        ma_20 = hist['Close'].tail(20).mean()
        ma_50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else current
        
        sentiment = {
            'trend': 'صاعد 📈' if current > ma_20 else 'هابط 📉',
            'strength': abs((current - ma_20) / ma_20 * 100),
            'volatility': hist['Close'].pct_change().std() * 100,
            'momentum': 'قوي 💪' if hist['Close'].pct_change().tail(5).mean() > 0.02 else 'ضعيف 🌊'
        }
        
        return sentiment
    except:
        return {}

def get_stock_ticker(name: str) -> Optional[str]:
    return STOCK_TICKERS.get(name)

def get_stock_market(name: str) -> Optional[str]:
    return STOCK_METADATA.get(name, {}).get('market')

def get_stock_metadata(name: str) -> Optional[Dict]:
    return STOCK_METADATA.get(name)

def search_stocks_by_keyword(keyword: str) -> Dict:
    return search_stock(keyword)

def get_stats() -> Dict:
    return get_market_statistics()
