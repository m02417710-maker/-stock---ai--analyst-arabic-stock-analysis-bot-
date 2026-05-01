# ============================================================
# ملف: intelligence.py
# طبقة الاستخبارات المالية - ربط البيانات بالعوامل الخارجية
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

class FinancialIntelligenceEngine:
    """
    محرك الاستخبارات المالية
    لربط أسعار الأسهم بالعوامل الاقتصادية الكلية
    """
    
    def __init__(self):
        self.current_rates = self._get_current_rates()
    
    def _get_current_rates(self):
        """جلب الأسعار الحالية للعملات والسلع"""
        try:
            # سعر الدولار مقابل الجنيه
            usd_egp = yf.Ticker("EGPUSD=X").history(period="1d")['Close'].iloc[-1] if "EGPUSD=X" else 48.5
            
            # سعر الذهب
            gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1] if "GC=F" else 2350
            
            # سعر النفط
            oil = yf.Ticker("CL=F").history(period="1d")['Close'].iloc[-1] if "CL=F" else 85
            
            return {
                "usd_egp": usd_egp,
                "gold": gold,
                "oil": oil,
                "timestamp": datetime.now()
            }
        except:
            return {
                "usd_egp": 48.5,
                "gold": 2350,
                "oil": 85,
                "timestamp": datetime.now()
            }
    
    def calculate_relative_strength_ratio(self, stock_price):
        """
        حساب قوة السهم أمام الذهب - كاشف التضخم الحقيقي
        إذا كانت النسبة تهبط، فالسهم يخسر قيمته الحقيقية حتى لو صعد سعره بالجنيه
        """
        gold_price = self.current_rates["gold"]
        ratio = stock_price / gold_price if gold_price > 0 else 0
        
        # تقييم النسبة
        if ratio > 0.01:
            strength = "🟢 قوي جداً"
            ratio_status = "السهم يتفوق على الذهب"
        elif ratio > 0.005:
            strength = "🟡 متوسط"
            ratio_status = "السهم يواكب الذهب"
        else:
            strength = "🔴 ضعيف"
            ratio_status = "السهم يخسر قيمته الحقيقية"
        
        return {
            "ratio": round(ratio, 6),
            "strength": strength,
            "status": ratio_status,
            "gold_price": gold_price
        }
    
    def calculate_usd_impact(self, stock_ticker):
        """
        حساب تأثير سعر الدولار على السهم
        الشركات المصدرة تستفيد من ارتفاع الدولار، والمستوردة تتضرر
        """
        usd_rate = self.current_rates["usd_egp"]
        
        # تحديد طبيعة الشركة (يمكن توسيعها حسب القطاع)
        export_sectors = ["ABUK.CA", "MFOT.CA"]  # قطاع الأسمدة (تصدير)
        import_sectors = ["TMGH.CA", "ORAS.CA"]  # قطاع العقارات (مواد بناء مستوردة)
        
        if stock_ticker in export_sectors:
            impact = "إيجابي" if usd_rate > 48 else "محايد"
            message = f"🇪🇬 ارتفاع الدولار يدعم أرباح التصدير (+{usd_rate:.2f} جنيه)"
            score = 1.5 if usd_rate > 48 else 0.5
        elif stock_ticker in import_sectors:
            impact = "سلبي" if usd_rate > 48 else "محايد"
            message = f"⚠️ ارتفاع الدولار يزيد تكاليف المواد الخام المستوردة"
            score = -1 if usd_rate > 48 else 0
        else:
            impact = "محايد"
            message = f"📊 سعر الدولار: {usd_rate:.2f} جنيه"
            score = 0
        
        return {
            "impact": impact,
            "message": message,
            "score": score,
            "usd_rate": usd_rate
        }
    
    def calculate_oil_impact(self, stock_ticker):
        """حساب تأثير سعر النفط"""
        oil_price = self.current_rates["oil"]
        
        # قطاع الطاقة يتأثر إيجاباً بارتفاع النفط
        energy_sectors = ["EGPC.CA", "MOPC.CA"]
        
        if stock_ticker in energy_sectors:
            impact = "إيجابي" if oil_price > 80 else "سلبي"
            message = f"🛢️ سعر النفط ${oil_price:.2f} - دعم لقطاع الطاقة"
            score = 1 if oil_price > 80 else -0.5
        else:
            impact = "غير مباشر"
            message = f"🛢️ سعر النفط العالمي: ${oil_price:.2f}"
            score = 0
        
        return {
            "impact": impact,
            "message": message,
            "score": score,
            "oil_price": oil_price
        }
    
    def get_comprehensive_analysis(self, stock_ticker, stock_price):
        """
        تحليل استخباراتي شامل
        يجمع جميع العوامل الخارجية المؤثرة على السهم
        """
        # العوامل المختلفة
        gold_analysis = self.calculate_relative_strength_ratio(stock_price)
        usd_analysis = self.calculate_usd_impact(stock_ticker)
        oil_analysis = self.calculate_oil_impact(stock_ticker)
        
        # حساب الدرجة الاستخباراتية الإجمالية
        total_score = gold_analysis.get("ratio", 0) * 100 + usd_analysis["score"] + oil_analysis["score"]
        
        # تحديد التوصية الاستخباراتية
        if total_score > 3:
            macro_recommendation = "🟢 الظروف الاقتصادية داعمة للصعود"
            macro_color = "#10b981"
        elif total_score > 1:
            macro_recommendation = "🟡 ظروف محايدة - انتظار"
            macro_color = "#f59e0b"
        else:
            macro_recommendation = "🔴 ظروف اقتصادية صعبة - توخ الحذر"
            macro_color = "#ef4444"
        
        return {
            "gold": gold_analysis,
            "usd": usd_analysis,
            "oil": oil_analysis,
            "total_score": round(total_score, 2),
            "macro_recommendation": macro_recommendation,
            "macro_color": macro_color,
            "market_rates": self.current_rates
        }

# دالة مبسطة للاستخدام السريع
def get_macro_analysis(ticker, price):
    """واجهة مبسطة للتحليل الاستخباراتي"""
    engine = FinancialIntelligenceEngine()
    return engine.get_comprehensive_analysis(ticker, price)
