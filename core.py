# core.py - المحرك الرئيسي
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from typing import Optional, Dict, List, Tuple
from database import get_all_stocks, search_stock, get_market_statistics, get_market_info

# تحميل البيانات
ALL_STOCKS_DATA = get_all_stocks()
STOCK_NAMES = list(ALL_STOCKS_DATA.keys())
STOCK_TICKERS = {name: data['ticker'] for name, data in ALL_STOCKS_DATA.items()}
STOCK_METADATA = {name: {
    'market': data['market'],
    'currency': data['currency']
} for name, data in ALL_STOCKS_DATA.items()}

def get_stock_data(ticker: str, period: str = "1y") -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None
        
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['EMA_9'] = ta.ema(df['Close'], length=9)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        return df, stock.info
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def get_stock_ticker(name: str) -> Optional[str]:
    """إرجاع رمز السهم"""
    return STOCK_TICKERS.get(name)

def get_stock_market(name: str) -> Optional[str]:
    """إرجاع سوق السهم"""
    return STOCK_METADATA.get(name, {}).get('market')

def get_stock_metadata(name: str) -> Optional[Dict]:
    """إرجاع معلومات السهم"""
    return STOCK_METADATA.get(name)

def search_stocks_by_keyword(keyword: str) -> Dict:
    """البحث عن أسهم"""
    return search_stock(keyword)

def get_stats() -> Dict:
    """إحصائيات الأسهم"""
    return get_market_statistics()

def get_market_info_by_name(market_name: str) -> Optional[Dict]:
    """جلب معلومات السوق"""
    return get_market_info(market_name)
