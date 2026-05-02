# engines.py - محركات التحليل المختلفة
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TechnicalEngine:
    """محرك التحليل الفني"""
    
    @staticmethod
    def calculate_rsi(df, period=14):
        """حساب مؤشر RSI"""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        """حساب مؤشر MACD"""
        exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(df, period=20, std=2):
        """حساب Bollinger Bands"""
        sma = df['Close'].rolling(window=period).mean()
        std_dev = df['Close'].rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return upper, sma, lower
    
    @staticmethod
    def get_support_resistance(df, lookback=50):
        """حساب نقاط الدعم والمقاومة"""
        recent_high = df['High'].tail(lookback).max()
        recent_low = df['Low'].tail(lookback).min()
        current = df['Close'].iloc[-1]
        
        resistance = recent_high
        support = recent_low
        
        # نقاط إضافية
        pivot = (recent_high + recent_low + current) / 3
        r1 = 2 * pivot - recent_low
        s1 = 2 * pivot - recent_high
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'pivot': round(pivot, 2),
            'r1': round(r1, 2),
            's1': round(s1, 2)
        }

class FundamentalEngine:
    """محرك التحليل الأساسي"""
    
    @staticmethod
    def get_company_info(ticker):
        """جلب معلومات الشركة"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
            }
        except:
            return None

class SignalEngine:
    """محرك توليد الإشارات"""
    
    def __init__(self):
        self.technical = TechnicalEngine()
    
    def generate_signals(self, df):
        """توليد إشارات البيع والشراء"""
        if df is None or df.empty:
            return None
        
        rsi = self.technical.calculate_rsi(df)
        macd, signal, _ = self.technical.calculate_macd(df)
        upper, middle, lower = self.technical.calculate_bollinger_bands(df)
        
        signals = []
        
        # إشارات RSI
        current_rsi = rsi.iloc[-1]
        if current_rsi < 30:
            signals.append({'type': 'BUY', 'indicator': 'RSI', 'reason': f'RSI منخفض ({current_rsi:.1f})'})
        elif current_rsi > 70:
            signals.append({'type': 'SELL', 'indicator': 'RSI', 'reason': f'RSI مرتفع ({current_rsi:.1f})'})
        
        # إشارات MACD
        if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
            signals.append({'type': 'BUY', 'indicator': 'MACD', 'reason': 'تقاطع إيجابي'})
        elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
            signals.append({'type': 'SELL', 'indicator': 'MACD', 'reason': 'تقاطع سلبي'})
        
        # إشارات Bollinger Bands
        current_price = df['Close'].iloc[-1]
        if current_price <= lower.iloc[-1]:
            signals.append({'type': 'BUY', 'indicator': 'BB', 'reason': 'السعر عند الحد السفلي'})
        elif current_price >= upper.iloc[-1]:
            signals.append({'type': 'SELL', 'indicator': 'BB', 'reason': 'السعر عند الحد العلوي'})
        
        return signals
