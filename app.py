# app.py - النسخة المتكاملة (الماسح التلقائي + التنبيهات + المحفظة + الذكاء الاصطناعي)
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title="العقل المدبر للأسهم 🧠",
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
def send_telegram_alert(message: str):
    """إرسال تنبيه عبر تليجرام"""
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
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
        
        # المتوسطات المتحركة
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
        
        # حجم التداول
        avg_volume = df['Volume'].tail(20).mean()
        volume_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
        
        # الدعم والمقاومة
        support = df['Low'].tail(50).min()
        resistance = df['High'].tail(50).max()
        
        # حساب نقاط الشراء والبيع
        buy_score = 0
        sell_score = 0
        buy_reasons = []
        sell_reasons = []
        
        # RSI Analysis
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
        
        # MACD Analysis
        if macd > macd_signal:
            buy_score += 2
            buy_reasons.append("MACD إيجابي - إشارة شراء")
        else:
            sell_score += 1
            sell_reasons.append("MACD سلبي")
        
        # Price vs SMA
        if current_price < sma_20:
            buy_score += 1
            buy_reasons.append("السعر أقل من المتوسط 20")
        elif current_price > sma_20 * 1.1:
            sell_score += 1
            sell_reasons.append("السعر مرتفع عن المتوسط 20")
        
        # Volume
        if volume_ratio > 1.5 and buy_score > 0:
            buy_score += 1
            buy_reasons.append("حجم تداول مرتفع يدعم الشراء")
        
        # تحديد التوصية
        if buy_score >= 4:
            recommendation = "BUY"
            action = "🟢 شراء قوي"
            confidence = "عالية"
        elif buy_score >= 2:
            recommendation = "BUY_WEAK"
            action = "🟡 شراء تدريجي"
            confidence = "متوسطة"
        elif sell_score >= 4:
            recommendation = "SELL"
            action = "🔴 بيع"
            confidence = "عالية"
        elif sell_score >= 2:
            recommendation = "SELL_WEAK"
            action = "🟠 مراقبة"
            confidence = "متوسطة"
        else:
            recommendation = "HOLD"
            action = "⚪ انتظار"
            confidence = "منخفضة"
        
        # جلب الأخبار للتحليل الأساسي
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
            "recommendation": recommendation,
            "action": action,
            "confidence": confidence,
            "buy_reasons": buy_reasons,
            "sell_reasons": sell_reasons,
            "news": news,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return None

# ====================== الماسح التلقائي (Scanner) ======================

def run_scanner(stocks_dict: Dict) -> List[Dict]:
    """تشغيل الماسح التلقائي على جميع الأسهم"""
    results = []
    total = len(stocks_dict)
    
    for i, (name, ticker) in enumerate(stocks_dict.items()):
        try:
            analysis = analyze_stock(ticker, name)
            if analysis:
                results.append(analysis)
        except Exception as e:
            print(f"Error scanning {ticker}: {e}")
        
        # تحديث التقدم
        if (i + 1) % 10 == 0:
            print(f"تم فحص {i+1}/{total} سهماً")
    
    # ترتيب النتائج حسب أفضل فرص الشراء
    results.sort(key=lambda x: x.get('buy_score', 0), reverse=True)
    
    # حفظ النتائج
    with open(SCAN_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

def get_top_opportunities(limit: int = 5) -> List[Dict]:
    """الحصول على أفضل فرص الاستثمار"""
    if SCAN_RESULTS_FILE.exists():
        with open(SCAN_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return results[:limit]
    return []

# ====================== المحفظة الافتراضية (Paper Trading) ======================

class PaperTrading:
    """نظام التداول الافتراضي"""
    
    @staticmethod
    def load_portfolio() -> Dict:
        if PORTFOLIO_FILE.exists():
            with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"positions": [], "transactions": [], "balance": 100000, "total_profit": 0}
    
    @staticmethod
    def save_portfolio(portfolio: Dict):
        with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def add_buy(ticker: str, name: str, price: float, shares: int, reason: str):
        portfolio = PaperTrading.load_portfolio()
        
        position = {
            "ticker": ticker,
            "name": name,
            "buy_price": price,
            "shares": shares,
            "buy_date": datetime.now().isoformat(),
            "buy_reason": reason,
            "current_price": price,
            "profit_loss": 0,
            "profit_loss_pct": 0
        }
        
        portfolio["positions"].append(position)
        portfolio["transactions"].append({
            "type": "BUY",
            "ticker": ticker,
            "price": price,
            "shares": shares,
            "amount": price * shares,
            "date": datetime.now().isoformat(),
            "reason": reason
        })
        
        portfolio["balance"] -= price * shares
        PaperTrading.save_portfolio(portfolio)
        return True
    
    @staticmethod
    def add_sell(ticker: str, price: float, reason: str):
        portfolio = PaperTrading.load_portfolio()
        
        for pos in portfolio["positions"]:
            if pos["ticker"] == ticker:
                profit = (price - pos["buy_price"]) * pos["shares"]
                portfolio["transactions"].append({
                    "type": "SELL",
                    "ticker": ticker,
                    "price": price,
                    "shares": pos["shares"],
                    "amount": price * pos["shares"],
                    "profit": profit,
                    "date": datetime.now().isoformat(),
                    "reason": reason
                })
                portfolio["balance"] += price * pos["shares"]
                portfolio["total_profit"] += profit
                portfolio["positions"].remove(pos)
                break
        
        PaperTrading.save_portfolio(portfolio)
        return True
    
    @staticmethod
    def update_prices(stocks_dict: Dict):
        """تحديث أسعار المحفظة"""
        portfolio = PaperTrading.load_portfolio()
        
        for pos in portfolio["positions"]:
            ticker = pos["ticker"]
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="1d")
                if not df.empty:
                    current = df['Close'].iloc[-1]
                    pos["current_price"] = current
                    pos["profit_loss"] = (current - pos["buy_price"]) * pos["shares"]
                    pos["profit_loss_pct"] = ((current - pos["buy_price"]) / pos["buy_price"]) * 100
            except:
                pass
        
        PaperTrading.save_portfolio(portfolio)
    
    @staticmethod
    def get_summary() -> Dict:
        portfolio = PaperTrading.load_portfolio()
        PaperTrading.update_prices({})
        
        total_value = portfolio["balance"]
        total_invested = 0
        
        for pos in portfolio["positions"]:
            total_value += pos["current_price"] * pos["shares"]
            total_invested += pos["buy_price"] * pos["shares"]
        
        return {
            "balance": portfolio["balance"],
            "total_value": total_value,
            "total_invested": total_invested,
            "total_profit": total_value - total_invested - portfolio["balance"],
            "total_profit_pct": ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            "positions_count": len(portfolio["positions"]),
            "transactions_count": len(portfolio["transactions"])
        }

# ====================== نظام التنبيهات التلقائي ======================

def check_and_send_alerts(scan_results: List[Dict]):
    """فحص النتائج وإرسال تنبيهات تلقائية"""
    alerts_sent = []
    
    for stock in scan_results:
        buy_score = stock.get('buy_score', 0)
        
        # تنبيه شراء قوي
        if buy_score >= 4:
            message = f"""
🚨 <b>تنبيه شراء قوي!</b> 🚨

📊 <b>{stock['name']}</b> ({stock['ticker']})
💰 السعر: {stock['current_price']:.2f}
📈 التغير: {stock['daily_change']:+.2f}%
🎯 درجة الشراء: {buy_score}/7

📋 <b>الأسباب:</b>
{chr(10).join([f"• {r}" for r in stock.get('buy_reasons', [])[:4]])}

💡 التوصية: شراء فوري
🎯 الهدف الأول: {stock['resistance']:.2f}
🛡️ وقف الخسارة: {stock['support']:.2f}
            """
            send_telegram_alert(message)
            alerts_sent.append(stock['ticker'])
    
    # حفظ سجل التنبيهات
    if alerts_sent:
        alerts = {"timestamp": datetime.now().isoformat(), "alerts": alerts_sent}
        with open(ALERTS_FILE, 'a', encoding='utf-8') as f:
            json.dump(alerts, f)
            f.write('\n')
    
    return alerts_sent

# ====================== التحليل بالذكاء الاصطناعي ======================

def get_ai_insights(stock_analysis: Dict, model) -> str:
    """الحصول على تحليل متقدم من الذكاء الاصطناعي"""
    if not model:
        return "الذكاء الاصطناعي غير متوفر"
    
    # تجهيز الأخبار للتحليل
    news_text = "\n".join([f"• {n}" for n in stock_analysis.get('news', [])[:3]])
    
    prompt = f"""
أنت محلل أسهم محترف. قم بتحليل شامل للسهم التالي:

📊 <b>البيانات الفنية:</b>
- السهم: {stock_analysis['name']} ({stock_analysis['ticker']})
- السعر: {stock_analysis['current_price']:.2f}
- RSI: {stock_analysis['rsi']:.1f}
- الدعم: {stock_analysis['support']:.2f}
- المقاومة: {stock_analysis['resistance']:.2f}
- درجة الشراء: {stock_analysis['buy_score']}/7
- درجة البيع: {stock_analysis['sell_score']}/7

📰 <b>آخر الأخبار:</b>
{news_text if news_text else "لا توجد أخبار متاحة"}

المطلوب:
1. دمج التحليل الفني مع الأساسي
2. تقييم المخاطر والعوائد
3. توصية نهائية مع توقعات السعر
4. نصيحة للمستثمر

الرد بالعربية بشكل مختصر (حد أقصى 200 كلمة).
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطأ: {e}"

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

# ====================== واجهة المستخدم ======================

def main():
    st.title("🧠 العقل المدبر للأسهم - نظام تحليل وتداول ذكي")
    st.markdown("**الماسح التلقائي | تنبيهات فورية | محفظة افتراضية | ذكاء اصطناعي**")
    st.markdown("---")
    
    # تهيئة النماذج
    model = init_gemini()
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 📊 لوحة التحكم")
        
        # زر تشغيل الماسح
        if st.button("🔄 تشغيل الماسح التلقائي", type="primary", use_container_width=True):
            with st.spinner("جاري فحص جميع الأسهم..."):
                results = run_scanner(STOCKS)
                alerts = check_and_send_alerts(results)
                st.success(f"✅ تم فحص {len(results)} سهماً")
                if alerts:
                    st.success(f"📢 تم إرسال {len(alerts)} تنبيه إلى تليجرام")
        
        st.divider()
        
        # إحصائيات الماسح
        top_opportunities = get_top_opportunities(5)
        if top_opportunities:
            st.markdown("### 🎯 أفضل الفرص")
            for opp in top_opportunities[:3]:
                score = opp.get('buy_score', 0)
                if score >= 3:
                    st.markdown(f"🟢 **{opp['name']}**")
                    st.caption(f"السعر: {opp['current_price']:.2f} | درجة: {score}")
        
        st.divider()
        
        # معلومات التليجرام
        st.markdown("### 🔔 إعدادات التنبيهات")
        if "TELEGRAM_BOT_TOKEN" in st.secrets:
            st.success("✅ بوت تليجرام: متصل")
        else:
            st.warning("⚠️ أضف TELEGRAM_BOT_TOKEN في secrets")
        
        # تحديث يدوي
        if st.button("🔄 تحديث الأسعار", use_container_width=True):
            PaperTrading.update_prices(STOCKS)
            st.success("تم تحديث الأسعار")
    
    # التبويبات الرئيسية
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 فرص الاستثمار", "📈 تحليل متقدم", "💼 المحفظة الافتراضية", "📊 سجل التنبيهات"])
    
    with tab1:
        st.header("🎯 أفضل فرص الشراء")
        
        # عرض نتائج الماسح
        opportunities = get_top_opportunities(10)
        
        if opportunities:
            for opp in opportunities:
                buy_score = opp.get('buy_score', 0)
                if buy_score >= 2:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            if buy_score >= 4:
                                status = "🟢 شراء قوي"
                            elif buy_score >= 2:
                                status = "🟡 شراء تدريجي"
                            else:
                                status = "⚪ مراقبة"
                            st.markdown(f"**{opp['name']}**")
                            st.caption(f"{opp['ticker']} | {status}")
                        
                        with col2:
                            st.metric("السعر", f"{opp['current_price']:.2f}", f"{opp['daily_change']:+.2f}%")
                        
                        with col3:
                            st.metric("RSI", f"{opp['rsi']:.1f}")
                        
                        with col4:
                            st.metric("درجة الشراء", f"{buy_score}/7")
                        
                        with st.expander(f"📋 تفاصيل التحليل"):
                            st.markdown("**✅ أسباب الشراء:**")
                            for reason in opp.get('buy_reasons', []):
                                st.write(f"• {reason}")
                            
                            if opp.get('sell_reasons'):
                                st.markdown("**⚠️ أسباب التحذير:**")
                                for reason in opp.get('sell_reasons', [])[:2]:
                                    st.write(f"• {reason}")
                            
                            st.markdown(f"""
                            **📊 مستويات رئيسية:**
                            - الدعم: {opp['support']:.2f}
                            - المقاومة: {opp['resistance']:.2f}
                            - المتوسط 20: {opp['sma_20']:.2f}
                            """)
                            
                            # أزرار الإجراءات
                            col_a, col_b = st.columns(2)
                            with col_a:
                                shares = st.number_input(f"عدد الأسهم", min_value=1, max_value=1000, value=10, key=f"shares_{opp['ticker']}")
                                if st.button(f"➕ شراء افتراضي", key=f"buy_{opp['ticker']}"):
                                    PaperTrading.add_buy(
                                        opp['ticker'], opp['name'], 
                                        opp['current_price'], shares,
                                        ", ".join(opp.get('buy_reasons', [])[:2])
                                    )
                                    st.success(f"✅ تم شراء {shares} سهم من {opp['name']}")
                                    time.sleep(1)
                                    st.rerun()
                            
                            with col_b:
                                if st.button(f"🤖 تحليل AI", key=f"ai_{opp['ticker']}"):
                                    with st.spinner("جاري التحليل..."):
                                        ai_result = get_ai_insights(opp, model)
                                        st.info(f"🧠 **تحليل الذكاء الاصطناعي:**\n\n{ai_result}")
                        
                        st.divider()
        else:
            st.info("📭 لا توجد نتائج. اضغط على 'تشغيل الماسح التلقائي' في الشريط الجانبي")
    
    with tab2:
        st.header("📈 تحليل سهم فردي")
        
        selected_name = st.selectbox("اختر السهم", list(STOCKS.keys()))
        selected_ticker = STOCKS[selected_name]
        
        if st.button("تحليل", type="primary"):
            with st.spinner("جاري التحليل..."):
                analysis = analyze_stock(selected_ticker, selected_name)
                
                if analysis:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 السعر", f"{analysis['current_price']:.2f}", f"{analysis['daily_change']:+.2f}%")
                    col2.metric("📊 RSI", f"{analysis['rsi']:.1f}")
                    col3.metric("🎯 التوصية", analysis['action'])
                    
                    st.divider()
                    
                    col_buy, col_sell = st.columns(2)
                    with col_buy:
                        st.markdown("### ✅ إشارات الشراء")
                        for reason in analysis.get('buy_reasons', []):
                            st.write(f"• {reason}")
                        st.metric("درجة الشراء", f"{analysis['buy_score']}/7")
                    
                    with col_sell:
                        st.markdown("### ⚠️ إشارات البيع")
                        for reason in analysis.get('sell_reasons', []):
                            st.write(f"• {reason}")
                        st.metric("درجة البيع", f"{analysis['sell_score']}/7")
                    
                    st.divider()
                    
                    if st.button("🧠 تحليل بالذكاء الاصطناعي"):
                        with st.spinner("جاري التحليل..."):
                            ai_result = get_ai_insights(analysis, model)
                            st.success(ai_result)
                else:
                    st.error("فشل في تحليل السهم")
    
    with tab3:
        st.header("💼 المحفظة الافتراضية")
        
        summary = PaperTrading.get_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 الرصيد", f"{summary['balance']:,.2f}")
        col2.metric("📊 قيمة المحفظة", f"{summary['total_value']:,.2f}")
        col3.metric("📈 إجمالي الربح", f"{summary['total_profit']:,.2f}", f"{summary['total_profit_pct']:+.2f}%")
        col4.metric("🎯 عدد الصفقات", summary['transactions_count'])
        
        st.divider()
        
        # عرض المراكز المفتوحة
        portfolio = PaperTrading.load_portfolio()
        
        if portfolio['positions']:
            st.markdown("### 📊 المراكز المفتوحة")
            for pos in portfolio['positions']:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.write(f"**{pos['name']}**")
                    st.caption(pos['ticker'])
                with col2:
                    st.write(f"شراء: {pos['buy_price']:.2f}")
                with col3:
                    st.write(f"حالياً: {pos['current_price']:.2f}")
                with col4:
                    profit_color = "🟢" if pos['profit_loss'] > 0 else "🔴" if pos['profit_loss'] < 0 else "⚪"
                    st.write(f"{profit_color} {pos['profit_loss']:+.2f}")
                with col5:
                    if st.button(f"بيع", key=f"sell_{pos['ticker']}"):
                        PaperTrading.add_sell(pos['ticker'], pos['current_price'], "جني أرباح")
                        st.success(f"✅ تم بيع {pos['name']}")
                        time.sleep(1)
                        st.rerun()
                st.divider()
        else:
            st.info("لا توجد مراكز مفتوحة")
        
        # سجل الصفقات
        with st.expander("📜 سجل الصفقات"):
            for trans in portfolio['transactions'][-10:]:
                if trans['type'] == 'BUY':
                    st.write(f"🟢 شراء {trans['shares']} سهم من {trans['ticker']} بسعر {trans['price']:.2f}")
                else:
                    st.write(f"🔴 بيع {trans['shares']} سهم من {trans['ticker']} بسعر {trans['price']:.2f} | ربح: {trans.get('profit', 0):.2f}")
    
    with tab4:
        st.header("📊 سجل التنبيهات")
        
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                alerts = [json.loads(line) for line in f.readlines()]
            
            for alert in reversed(alerts[-20:]):
                st.info(f"🔔 {alert['timestamp'][:19]} - تم إرسال {len(alert['alerts'])} تنبيه")
        else:
            st.info("لا توجد تنبيهات بعد")

if __name__ == "__main__":
    main()
