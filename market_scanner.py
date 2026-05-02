# market_scanner.py - مسح السوق والبحث عن فرص
import yfinance as yf
import pandas as pd
from datetime import datetime
from engines import TechnicalEngine, SignalEngine
import warnings
warnings.filterwarnings('ignore')

class MarketScanner:
    def __init__(self):
        self.technical = TechnicalEngine()
        self.signal_engine = SignalEngine()
    
    def scan_stock(self, ticker, name=""):
        """مسح سهم فردي"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2mo")
            
            if len(hist) < 30:
                return None
            
            # حساب المؤشرات
            rsi = self.technical.calculate_rsi(hist)
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # نقاط الدعم والمقاومة
            sr_levels = self.technical.get_support_resistance(hist)
            
            # الإشارات
            signals = self.signal_engine.generate_signals(hist)
            
            current_price = hist['Close'].iloc[-1]
            
            return {
                'ticker': ticker,
                'name': name,
                'price': round(current_price, 2),
                'rsi': round(current_rsi, 1),
                'signals': signals,
                'support': sr_levels['support'],
                'resistance': sr_levels['resistance'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"خطأ في مسح {ticker}: {e}")
            return None
    
    def scan_multiple_stocks(self, stocks_dict):
        """مسح عدة أسهم"""
        results = []
        for name, ticker in stocks_dict.items():
            result = self.scan_stock(ticker, name)
            if result:
                results.append(result)
        return results
    
    def get_opportunities(self, stocks_dict):
        """الحصول على فرص التداول"""
        results = self.scan_multiple_stocks(stocks_dict)
        
        opportunities = []
        for result in results:
            if result['rsi'] < 35:
                opportunities.append({
                    **result,
                    'type': 'BUY_OPPORTUNITY',
                    'priority': 'HIGH' if result['rsi'] < 30 else 'MEDIUM'
                })
            elif result['rsi'] > 65:
                opportunities.append({
                    **result,
                    'type': 'SELL_ALERT',
                    'priority': 'HIGH' if result['rsi'] > 70 else 'MEDIUM'
                })
        
        return opportunities
