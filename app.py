# app.py - النسخة النهائية مع مرآة المحفظة الشخصية
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title="العقل المدبر للأسهم - مرآة المحفظة 🧠",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== الاستيرادات ======================
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import requests

# ====================== التهيئة ======================

# إنشاء المجلدات اللازمة
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ملفات التخزين
SCAN_RESULTS_FILE = DATA_DIR / "scan_results.json"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
REAL_PORTFOLIO_FILE = DATA_DIR / "real_portfolio.json"
PROTECTION_LOG_FILE = DATA_DIR / "protection_log.json"

# ====================== إعداد Gemini ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== إعداد تليجرام ======================
def send_telegram_alert(message: str, priority: str = "info"):
    """إرسال تنبيه عبر تليجرام"""
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            
            # إضافة أيقونة حسب الأولوية
            if priority == "danger":
                full_message = f"🚨⚠️ {message} ⚠️🚨"
            elif priority == "warning":
                full_message = f"⚠️ {message} ⚠️"
            elif priority == "success":
                full_message = f"✅ {message} ✅"
            else:
                full_message = f"📊 {message}"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": full_message, "parse_mode": "HTML"}
            response = requests.post(url, data=data, timeout=10)
            return response.ok
    except Exception as e:
        print(f"Telegram error: {e}")
    return False

# ====================== دوال التحليل الفني ======================

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
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
    try:
        ema_fast = prices.ewm(span=12, adjust=False).mean()
        ema_slow = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        return macd_line.iloc[-1], signal_line.iloc[-1]
    except:
        return 0, 0

def analyze_stock(ticker: str, name: str = "") -> Dict:
    """تحليل شامل لسهم واحد"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 20:
            return None
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        daily_change = ((current_price - prev_price) / prev_price) * 100
        
        rsi = calculate_rsi(df['Close'], 14)
        macd, macd_signal = calculate_macd(df['Close'])
        
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
        
        avg_volume = df['Volume'].tail(20).mean()
        volume_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
        
        support = df['Low'].tail(50).min()
        resistance = df['High'].tail(50).max()
        
        # حساب نقاط الشراء والبيع
        buy_score = 0
        sell_score = 0
        buy_reasons = []
        sell_reasons = []
        
        if rsi < 30:
            buy_score += 3
            buy_reasons.append(f"RSI منخفض ({rsi:.1f}) - ذروة بيع")
        elif rsi < 35:
            buy_score += 2
            buy_reasons.append(f"RSI جيد للشراء ({rsi:.1f})")
        elif rsi > 70:
            sell_score += 3
            sell_reasons.append(f"RSI مرتفع ({rsi:.1f}) - ذروة شراء")
        elif rsi > 65:
            sell_score += 2
            sell_reasons.append(f"RSI في منطقة خطر ({rsi:.1f})")
        
        if macd > macd_signal:
            buy_score += 2
            buy_reasons.append("MACD إيجابي - إشارة شراء")
        else:
            sell_score += 1
            sell_reasons.append("MACD سلبي")
        
        if current_price < sma_20:
            buy_score += 1
            buy_reasons.append("السعر أقل من المتوسط 20")
        elif current_price > sma_20 * 1.1:
            sell_score += 1
            sell_reasons.append("السعر مرتفع عن المتوسط 20")
        
        if volume_ratio > 1.5 and buy_score > 0:
            buy_score += 1
            buy_reasons.append("حجم تداول مرتفع يدعم الشراء")
        
        # جلب الأخبار
        news = []
        try:
            if hasattr(stock, 'news') and stock.news:
                for item in stock.news[:3]:
                    news.append(item.get('title', ''))
        except:
            pass
        
        return {
            "ticker": ticker,
            "name": name,
            "current_price": current_price,
            "daily_change": daily_change,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "support": support,
            "resistance": resistance,
            "volume_ratio": volume_ratio,
            "buy_score": buy_score,
            "sell_score": sell_score,
            "buy_reasons": buy_reasons,
            "sell_reasons": sell_reasons,
            "news": news,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return None

# ====================== نظام مرآة المحفظة الشخصية ======================

class RealPortfolioMirror:
    """نظام مرآة المحفظة الشخصية - يعكس أسهمك الحقيقية"""
    
    @staticmethod
    def load():
        if REAL_PORTFOLIO_FILE.exists():
            with open(REAL_PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"stocks": [], "total_invested": 0, "total_current": 0}
    
    @staticmethod
    def save(data):
        with open(REAL_PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def add_stock(ticker: str, name: str, avg_price: float, quantity: int, notes: str = ""):
        data = RealPortfolioMirror.load()
        
        new_stock = {
            "ticker": ticker,
            "name": name,
            "avg_price": avg_price,
            "quantity": quantity,
            "notes": notes,
            "added_date": datetime.now().isoformat(),
            "sell_alerts_sent": False,
            "buy_alerts_sent": False
        }
        
        data["stocks"].append(new_stock)
        RealPortfolioMirror.save(data)
        return True
    
    @staticmethod
    def remove_stock(ticker: str):
        data = RealPortfolioMirror.load()
        data["stocks"] = [s for s in data["stocks"] if s["ticker"] != ticker]
        RealPortfolioMirror.save(data)
        return True
    
    @staticmethod
    def update_prices():
        """تحديث أسعار جميع الأسهم في المحفظة"""
        data = RealPortfolioMirror.load()
        total_current = 0
        total_invested = 0
        
        for stock in data["stocks"]:
            try:
                ticker = stock["ticker"]
                stock_obj = yf.Ticker(ticker)
                df = stock_obj.history(period="1d")
                
                if not df.empty:
                    current_price = df['Close'].iloc[-1]
                    stock["current_price"] = current_price
                    stock["profit_loss"] = (current_price - stock["avg_price"]) * stock["quantity"]
                    stock["profit_loss_pct"] = ((current_price - stock["avg_price"]) / stock["avg_price"]) * 100
                    stock["last_update"] = datetime.now().isoformat()
                    
                    total_current += current_price * stock["quantity"]
                    total_invested += stock["avg_price"] * stock["quantity"]
            except:
                pass
        
        data["total_current"] = total_current
        data["total_invested"] = total_invested
        data["total_profit"] = total_current - total_invested
        data["total_profit_pct"] = (data["total_profit"] / total_invested * 100) if total_invested > 0 else 0
        
        RealPortfolioMirror.save(data)
        return data
    
    @staticmethod
    def check_protection_alerts():
        """فحص وتفعيل تنبيهات الحماية"""
        data = RealPortfolioMirror.update_prices()
        alerts_sent = []
        
        for stock in data["stocks"]:
            ticker = stock["ticker"]
            current = stock.get("current_price", 0)
            avg_price = stock["avg_price"]
            profit_pct = stock.get("profit_loss_pct", 0)
            
            # جلب التحليل الفني للسهم
            analysis = analyze_stock(ticker, stock["name"])
            
            if analysis:
                rsi = analysis.get('rsi', 50)
                support = analysis.get('support', 0)
                resistance = analysis.get('resistance', 0)
                
                # تنبيه 1: خسارة 5% من سعر الشراء
                if profit_pct <= -5 and not stock.get("loss_alert_sent", False):
                    message = f"""
🔴 <b>تنبيه إدارة مخاطر - خسارة!</b> 🔴

📉 <b>{stock['name']}</b> ({ticker})
💰 سعر الشراء: {avg_price:.2f}
📊 السعر الحالي: {current:.2f}
📉 الخسارة: {profit_pct:.2f}%

⚠️ السهم هبط بنسبة {abs(profit_pct):.1f}% من سعر شرائك!

💡 توصية العقل المدبر:
- مراجعة مركزك في السهم
- تفعيل وقف الخسارة إذا تجاوز 8%
- متابعة الأخبار السلبية عن الشركة
                    """
                    send_telegram_alert(message, "danger")
                    stock["loss_alert_sent"] = True
                    alerts_sent.append(ticker)
                
                # تنبيه 2: ربح 15% (جني أرباح)
                elif profit_pct >= 15 and not stock.get("profit_alert_sent", False):
                    message = f"""
✅ <b>تنبيه أرباح - جني أرباح!</b> ✅

📈 <b>{stock['name']}</b> ({ticker})
💰 سعر الشراء: {avg_price:.2f}
📊 السعر الحالي: {current:.2f}
📈 الأرباح: {profit_pct:.2f}%

🎯 العقل المدبر يوصي:
- جني الأرباح جزئياً (25-50%)
- رفع وقف الخسارة إلى نقطة التعادل
- متابعة المقاومة التالية: {resistance:.2f}
                    """
                    send_telegram_alert(message, "success")
                    stock["profit_alert_sent"] = True
                    alerts_sent.append(ticker)
                
                # تنبيه 3: RSI فوق 75 (ذروة شراء)
                elif rsi > 75 and not stock.get("rsi_alert_sent", False):
                    message = f"""
⚠️ <b>تنبيه فني - ذروة شراء!</b> ⚠️

📊 <b>{stock['name']}</b> ({ticker})
📈 RSI الحالي: {rsi:.1f} (فوق 75)

⚠️ السهم في منطقة ذروة شراء خطيرة!

💡 توصية العقل المدبر:
- احتمالية تصحيح وشيكة
- يفضل جني الأرباح تدريجياً
- مستوى الدعم الأول: {support:.2f}
                    """
                    send_telegram_alert(message, "warning")
                    stock["rsi_alert_sent"] = True
                    alerts_sent.append(ticker)
                
                # تنبيه 4: كسر الدعم
                elif current < support * 0.98 and not stock.get("support_alert_sent", False):
                    message = f"""
🔻 <b>تنبيه - كسر مستوى الدعم!</b> 🔻

📉 <b>{stock['name']}</b> ({ticker})
🛡️ مستوى الدعم: {support:.2f}
📊 السعر الحالي: {current:.2f}

⚠️ السهم كسر الدعم الرئيسي!

💡 العقل المدبر يوصي:
- تفعيل وقف الخسارة فوراً
- مراجعة مركزك في السهم
- انتظار إشارة ارتداد قبل الشراء
                    """
                    send_telegram_alert(message, "danger")
                    stock["support_alert_sent"] = True
                    alerts_sent.append(ticker)
                
                # إعادة تعيين التنبيهات عند تحسن الوضع
                else:
                    if profit_pct > -3:
                        stock["loss_alert_sent"] = False
                    if profit_pct < 12:
                        stock["profit_alert_sent"] = False
                    if rsi < 70:
                        stock["rsi_alert_sent"] = False
                    if current > support:
                        stock["support_alert_sent"] = False
        
        RealPortfolioMirror.save(data)
        return alerts_sent
    
    @staticmethod
    def get_ai_advice_for_stock(ticker: str, model) -> str:
        """الحصول على نصيحة من الذكاء الاصطناعي لسهم معين"""
        data = RealPortfolioMirror.load()
        stock = next((s for s in data["stocks"] if s["ticker"] == ticker), None)
        
        if not stock or not model:
            return "لا يمكن تقديم النصيحة حالياً"
        
        analysis = analyze_stock(ticker, stock["name"])
        
        if not analysis:
            return "لا توجد بيانات كافية للتحليل"
        
        prompt = f"""
أنت "العقل المدبر" - مستشار استثماري ذكي.
لدي سهم في محفظتي الحقيقية:

📊 <b>بيانات السهم:</b>
- السهم: {stock['name']} ({ticker})
- سعر شرائي: {stock['avg_price']:.2f}
- السعر الحالي: {analysis['current_price']:.2f}
- نسبة الربح/الخسارة: {stock.get('profit_loss_pct', 0):.2f}%
- الكمية المملوكة: {stock['quantity']}

📈 <b>التحليل الفني:</b>
- RSI: {analysis['rsi']:.1f}
- الدعم: {analysis['support']:.2f}
- المقاومة: {analysis['resistance']:.2f}
- التوصية الفنية: {'شراء' if analysis['buy_score'] > analysis['sell_score'] else 'بيع' if analysis['sell_score'] > analysis['buy_score'] else 'انتظار'}

المطلوب:
1. هل أبيع أم أحتفظ أم أشتري المزيد؟
2. ما هي نسبة المخاطرة الآن؟
3. أين أضع وقف الخسارة؟
4. ما هو الهدف القادم؟

الرد كمدير مالي محترف، مختصر ومباشر (حد أقصى 150 كلمة).
"""
        try:
            response = model.generate_content(prompt)
            return response.text
        except:
            return "عذراً، حدث خطأ في تحليل الذكاء الاصطناعي"

# ====================== المحفظة الافتراضية ======================

class PaperTrading:
    """نظام التداول الافتراضي"""
    
    @staticmethod
    def load():
        if PORTFOLIO_FILE.exists():
            with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"positions": [], "transactions": [], "balance": 100000, "total_profit": 0}
    
    @staticmethod
    def save(portfolio):
        with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def add_buy(ticker, name, price, shares, reason):
        portfolio = PaperTrading.load()
        
        position = {
            "ticker": ticker,
            "name": name,
            "buy_price": price,
            "shares": shares,
            "buy_date": datetime.now().isoformat(),
            "buy_reason": reason
        }
        
        portfolio["positions"].append(position)
        portfolio["transactions"].append({
            "type": "BUY", "ticker": ticker, "price": price,
            "shares": shares, "amount": price * shares,
            "date": datetime.now().isoformat(), "reason": reason
        })
        
        portfolio["balance"] -= price * shares
        PaperTrading.save(portfolio)
        return True

# ====================== قائمة الأسهم ======================

STOCKS = {
    "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
    "🇪🇬 طلعت مصطفى القابضة": "TMGH.CA",
    "🇪🇬 السويدي إليكتريك": "SWDY.CA",
    "🇪🇬 تليكوم مصر": "ETEL.CA",
    "🇪🇬 الشرقية للدخان": "EAST.CA",
    "🇸🇦 أرامكو السعودية": "2222.SR",
    "🇸🇦 مصرف الراجحي": "1120.SR",
    "🇸🇦 مجموعة STC": "7010.SR",
    "🇺🇸 Apple Inc.": "AAPL",
    "🇺🇸 Microsoft Corp.": "MSFT",
    "🇺🇸 Tesla Inc.": "TSLA",
}

# ====================== واجهة المستخدم الرئيسية ======================

def main():
    st.title("🧠 العقل المدبر للأسهم - مرآة المحفظة الشخصية")
    st.markdown("**راقب أسهمك الحقيقية | تنبيهات حماية فورية | ذكاء اصطناعي استشاري**")
    st.markdown("---")
    
    # تهيئة النماذج
    model = init_gemini()
    
    # تحديث أسعار المحفظة الحقيقية تلقائياً
    if st.button("🔄 تحديث المحفظة وجلب التنبيهات", type="primary"):
        with st.spinner("جاري تحليل محفظتك وتفعيل التنبيهات..."):
            alerts = RealPortfolioMirror.check_protection_alerts()
            if alerts:
                st.success(f"✅ تم إرسال {len(alerts)} تنبيه إلى تليجرام")
            else:
                st.info("✅ لا توجد تنبيهات جديدة - محفظتك في حالة جيدة")
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["👤 محفظتي الحقيقية", "🎯 فرص الاستثمار", "📈 تحليل السهم"])
    
    with tab1:
        st.header("👤 مرآة المحفظة الشخصية")
        st.info("🔒 هذه المحفظة تعكس أسهمك الحقيقية - العقل المدبر يراقبها ويحميها")
        
        # إضافة سهم جديد
        with st.expander("➕ إضافة سهم من محفظتك الحقيقية"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                r_ticker = st.text_input("رمز السهم", placeholder="مثال: COMI.CA")
            with col2:
                stock_name = st.text_input("اسم السهم", placeholder="البنك التجاري الدولي")
            with col3:
                r_price = st.number_input("متوسط سعر الشراء", min_value=0.1, step=0.5)
            with col4:
                r_qty = st.number_input("الكمية المملوكة", min_value=1, step=1)
            
            if st.button("🔗 ربط السهم بالعقل المدبر"):
                if r_ticker and r_price and r_qty:
                    RealPortfolioMirror.add_stock(r_ticker.upper(), stock_name or r_ticker.upper(), r_price, int(r_qty), "")
                    st.success(f"✅ تم ربط {r_ticker} بنجاح! العقل المدبر سيراقب سهمك الآن.")
                    st.rerun()
                else:
                    st.error("يرجى إدخال جميع البيانات")
        
        # عرض المحفظة
        portfolio = RealPortfolioMirror.update_prices()
        
        if portfolio["stocks"]:
            # إحصائيات عامة
            st.markdown("### 📊 إجمالي أداء المحفظة")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 إجمالي المستثمر", f"{portfolio['total_invested']:,.2f}")
            col2.metric("📈 القيمة الحالية", f"{portfolio['total_current']:,.2f}")
            profit_color = "🟢" if portfolio['total_profit'] > 0 else "🔴" if portfolio['total_profit'] < 0 else "⚪"
            col3.metric(f"{profit_color} إجمالي الربح", f"{portfolio['total_profit']:+,.2f}", f"{portfolio['total_profit_pct']:+.2f}%")
            col4.metric("📊 عدد الأسهم", len(portfolio["stocks"]))
            
            st.divider()
            
            # عرض كل سهم
            st.markdown("### 📋 تفاصيل الأسهم")
            for stock in portfolio["stocks"]:
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1])
                    
                    with col1:
                        st.markdown(f"**{stock['name']}**")
                        st.caption(stock['ticker'])
                    
                    with col2:
                        st.metric("سعر الشراء", f"{stock['avg_price']:.2f}")
                    
                    with col3:
                        current = stock.get('current_price', 0)
                        st.metric("السعر الحالي", f"{current:.2f}")
                    
                    with col4:
                        profit = stock.get('profit_loss', 0)
                        profit_pct = stock.get('profit_loss_pct', 0)
                        st.metric("الربح/الخسارة", f"{profit:+,.2f}", f"{profit_pct:+.2f}%")
                    
                    with col5:
                        if st.button(f"🧠 اسأل العقل", key=f"ask_{stock['ticker']}"):
                            with st.spinner("العقل المدبر يفكر..."):
                                advice = RealPortfolioMirror.get_ai_advice_for_stock(stock['ticker'], model)
                                st.session_state[f'advice_{stock["ticker"]}'] = advice
                    
                    with col6:
                        if st.button(f"🗑️ حذف", key=f"del_{stock['ticker']}"):
                            RealPortfolioMirror.remove_stock(stock['ticker'])
                            st.rerun()
                    
                    # عرض النصيحة
                    if f'advice_{stock["ticker"]}' in st.session_state:
                        st.info(f"🧠 **العقل المدبر يقول:**\n\n{st.session_state[f'advice_{stock["ticker"]}']}")
                    
                    # عرض المؤشرات السريعة
                    analysis = analyze_stock(stock['ticker'], stock['name'])
                    if analysis:
                        rsi = analysis.get('rsi', 50)
                        rsi_color = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡"
                        st.caption(f"{rsi_color} RSI: {rsi:.1f} | دعم: {analysis['support']:.2f} | مقاومة: {analysis['resistance']:.2f}")
                    
                    st.divider()
        else:
            st.info("📭 لا توجد أسهم في محفظتك. أضف أسهمك الحقيقية ليراقبها العقل المدبر")
    
    with tab2:
        st.header("🎯 فرص الاستثمار الجديدة")
        st.info("العقل المدبر يبحث عن أفضل الفرص لك")
        
        # تحليل جميع الأسهم
        if st.button("🔍 البحث عن فرص"):
            with st.spinner("جاري البحث عن أفضل الفرص..."):
                results = []
                for name, ticker in STOCKS.items():
                    analysis = analyze_stock(ticker, name)
                    if analysis:
                        results.append(analysis)
                
                results.sort(key=lambda x: x.get('buy_score', 0), reverse=True)
                
                for r in results[:5]:
                    buy_score = r.get('buy_score', 0)
                    if buy_score >= 2:
                        with st.expander(f"{'🟢' if buy_score >= 4 else '🟡'} {r['name']} - درجة الشراء: {buy_score}/7"):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("السعر", f"{r['current_price']:.2f}", f"{r['daily_change']:+.2f}%")
                            col2.metric("RSI", f"{r['rsi']:.1f}")
                            col3.metric("المقاومة", f"{r['resistance']:.2f}")
                            
                            st.markdown("**أسباب الشراء:**")
                            for reason in r.get('buy_reasons', []):
                                st.write(f"• {reason}")
    
    with tab3:
        st.header("📈 تحليل سهم فردي")
        
        selected_name = st.selectbox("اختر السهم", list(STOCKS.keys()))
        selected_ticker = STOCKS[selected_name]
        
        if st.button("تحليل"):
            with st.spinner("جاري التحليل..."):
                analysis = analyze_stock(selected_ticker, selected_name)
                
                if analysis:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 السعر", f"{analysis['current_price']:.2f}", f"{analysis['daily_change']:+.2f}%")
                    col2.metric("📊 RSI", f"{analysis['rsi']:.1f}")
                    col3.metric("🎯 التوصية", "شراء" if analysis['buy_score'] > analysis['sell_score'] else "بيع" if analysis['sell_score'] > analysis['buy_score'] else "انتظار")
                    
                    st.divider()
                    
                    if st.button("🧠 اسأل العقل المدبر"):
                        with st.spinner("العقل يفكر..."):
                            if model:
                                prompt = f"حلل السهم {selected_name} ({selected_ticker}) فنياً. السعر {analysis['current_price']:.2f}، RSI {analysis['rsi']:.1f}. أعط توصية مختصرة."
                                response = model.generate_content(prompt)
                                st.success(response.text)
                            else:
                                st.error("الذكاء الاصطناعي غير متوفر")

if __name__ == "__main__":
    main()
