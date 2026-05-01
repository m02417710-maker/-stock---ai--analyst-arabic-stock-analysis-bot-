# app.py - التطبيق الرئيسي الكامل مع نظام التنبيهات للبيع والشراء
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة أولاً
st.set_page_config(
    page_title="Stock AI Analyst Pro - نظام التنبيهات 📢",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== التهيئة الأمنية ======================
from security import initialize_security, validate_ticker, get_safe_ticker
initialize_security()

# ====================== الاستيرادات ======================
from pathlib import Path
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
from datetime import datetime
from typing import Dict, Optional, List
import json

# استيراد core
try:
    import core
    from core import STOCKS
    STOCK_NAMES = list(STOCKS.keys()) if STOCKS else []
except ImportError:
    STOCKS = {
        "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
        "🇸🇦 أرامكو السعودية": "2222.SR",
        "🇺🇸 Apple Inc.": "AAPL"
    }
    STOCK_NAMES = list(STOCKS.keys())

# تعريف الإصدار
try:
    from config import APP_VERSION
except ImportError:
    APP_VERSION = "5.0.0"

# ====================== إعداد Gemini ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي"""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        pass
    return None

# ====================== دوال التحليل الفني ======================

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
    """حساب مؤشر MACD"""
    try:
        ema_fast = prices.ewm(span=12, adjust=False).mean()
        ema_slow = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        return macd_line.iloc[-1], signal_line.iloc[-1]
    except:
        return 0, 0

def calculate_support_resistance(df: pd.DataFrame, lookback: int = 50):
    """حساب مستويات الدعم والمقاومة"""
    try:
        recent_data = df.tail(lookback)
        resistance = recent_data['High'].max()
        support = recent_data['Low'].min()
        return support, resistance
    except:
        return df['Low'].min(), df['High'].max()

# ====================== نظام تنبيهات البيع والشراء ======================

class TradingAlertSystem:
    """
    نظام متكامل لتنبيهات البيع والشراء
    """
    
    def __init__(self):
        # تهيئة سجل التنبيهات في session state
        if 'buy_alerts' not in st.session_state:
            st.session_state.buy_alerts = []
        if 'sell_alerts' not in st.session_state:
            st.session_state.sell_alerts = []
        if 'all_alerts' not in st.session_state:
            st.session_state.all_alerts = []
    
    def analyze_buy_signals(self, ticker: str, current_price: float, rsi: float, 
                            macd: float, macd_signal: float, price_vs_sma: str,
                            volume_ratio: float, trend: str) -> Dict:
        """
        تحليل إشارات الشراء
        """
        buy_signals = []
        buy_score = 0
        reasons = []
        
        # 1. إشارة RSI للشراء
        if rsi < 30:
            buy_score += 3
            reasons.append(f"✅ RSI منخفض جداً ({rsi:.1f}) - منطقة ذروة بيع قوية")
            buy_signals.append("RSI ذروة بيع")
        elif rsi < 35:
            buy_score += 2
            reasons.append(f"📉 RSI منخفض ({rsi:.1f}) - فرصة شراء جيدة")
            buy_signals.append("RSI منخفض")
        elif rsi < 40:
            buy_score += 1
            reasons.append(f"📊 RSI في المنطقة المحايدة السفلية ({rsi:.1f})")
        
        # 2. إشارة MACD للشراء
        if macd > macd_signal:
            buy_score += 2
            reasons.append("🟢 تقاطع MACD إيجابي - إشارة شراء")
            buy_signals.append("MACD إيجابي")
        
        # 3. السعر أقل من المتوسطات
        if price_vs_sma == "below":
            buy_score += 1
            reasons.append("📉 السعر أقل من المتوسط 20 - فرصة شراء")
            buy_signals.append("سعر منخفض")
        
        # 4. حجم تداول إيجابي
        if volume_ratio > 1.2:
            buy_score += 1
            reasons.append("📊 حجم تداول مرتفع - زخم إيجابي")
        
        # 5. الاتجاه الصاعد
        if trend == "صاعد":
            buy_score += 2
            reasons.append("📈 اتجاه عام صاعد للسهم")
        
        # تحديد مستوى الإشارة
        if buy_score >= 5:
            signal_type = "🔴 إشارة شراء قوية جداً"
            action = "شراء فوري 🟢"
            confidence = "عالية جداً"
            suggested_allocation = "15-20%"
        elif buy_score >= 3:
            signal_type = "🟠 إشارة شراء جيدة"
            action = "شراء تدريجي 🟡"
            confidence = "عالية"
            suggested_allocation = "10-15%"
        elif buy_score >= 2:
            signal_type = "🟡 إشارة شراء ضعيفة"
            action = "مراقبة فقط"
            confidence = "متوسطة"
            suggested_allocation = "5-10%"
        else:
            signal_type = "⚪ لا توجد إشارة شراء"
            action = "انتظار"
            confidence = "منخفضة"
            suggested_allocation = "0%"
        
        return {
            "signal": signal_type,
            "action": action,
            "score": buy_score,
            "confidence": confidence,
            "reasons": reasons,
            "signals": buy_signals,
            "suggested_allocation": suggested_allocation,
            "timestamp": datetime.now()
        }
    
    def analyze_sell_signals(self, ticker: str, current_price: float, rsi: float,
                             macd: float, macd_signal: float, price_vs_sma: str,
                             volume_ratio: float, trend: str) -> Dict:
        """
        تحليل إشارات البيع
        """
        sell_signals = []
        sell_score = 0
        reasons = []
        
        # 1. إشارة RSI للبيع
        if rsi > 70:
            sell_score += 3
            reasons.append(f"🔴 RSI مرتفع جداً ({rsi:.1f}) - منطقة ذروة شراء خطيرة")
            sell_signals.append("RSI ذروة شراء")
        elif rsi > 65:
            sell_score += 2
            reasons.append(f"⚠️ RSI مرتفع ({rsi:.1f}) - احتمالية تصحيح")
            sell_signals.append("RSI مرتفع")
        elif rsi > 60:
            sell_score += 1
            reasons.append(f"📊 RSI في المنطقة العلوية ({rsi:.1f})")
        
        # 2. إشارة MACD للبيع
        if macd < macd_signal:
            sell_score += 2
            reasons.append("🔴 تقاطع MACD سلبي - إشارة بيع")
            sell_signals.append("MACD سلبي")
        
        # 3. السعر أعلى من المتوسطات (تمدد)
        if price_vs_sma == "above":
            sell_score += 1
            reasons.append("📈 السعر أعلى من المتوسط 20 - احتمالية تصحيح")
            sell_signals.append("تمدد سعري")
        
        # 4. حجم تداول مع انخفاض
        if volume_ratio > 1.5 and price_vs_sma == "above":
            sell_score += 1
            reasons.append("⚠️ حجم تداول مرتفع مع قرب من المقاومة")
        
        # 5. الاتجاه الهابط
        if trend == "هابط":
            sell_score += 2
            reasons.append("📉 اتجاه عام هابط للسهم")
        
        # تحديد مستوى الإشارة
        if sell_score >= 5:
            signal_type = "🔴 إشارة بيع قوية جداً"
            action = "بيع فوري 🔴"
            confidence = "عالية جداً"
            reason_summary = "خطر كبير - يوصى بالخروج الفوري"
        elif sell_score >= 3:
            signal_type = "🟠 إشارة بيع"
            action = "بيع جزئي 🟠"
            confidence = "عالية"
            reason_summary = "منطقة خطر - يوصى بتقليل المركز"
        elif sell_score >= 2:
            signal_type = "🟡 إشارة مراقبة"
            action = "مراقبة كثيفة"
            confidence = "متوسطة"
            reason_summary = "علامات تحذير - راقب السهم عن كثب"
        else:
            signal_type = "🟢 لا توجد إشارة بيع"
            action = "احتفظ بالسهم"
            confidence = "منخفضة"
            reason_summary = "لا توجد علامات خطر حالياً"
        
        return {
            "signal": signal_type,
            "action": action,
            "score": sell_score,
            "confidence": confidence,
            "reasons": reasons,
            "signals": sell_signals,
            "reason_summary": reason_summary,
            "timestamp": datetime.now()
        }
    
    def get_overall_recommendation(self, buy_signal: Dict, sell_signal: Dict) -> Dict:
        """
        الحصول على التوصية النهائية
        """
        buy_score = buy_signal.get('score', 0)
        sell_score = sell_signal.get('score', 0)
        
        if buy_score >= 3 and sell_score <= 1:
            recommendation = "🟢 **شراء** - مؤشرات إيجابية قوية"
            color = "green"
            action = "شراء"
            urgency = "عالي"
        elif buy_score >= 2 and sell_score <= 2:
            recommendation = "🟡 **شراء تدريجي** - مؤشرات إيجابية معقولة"
            color = "yellow"
            action = "شراء تدريجي"
            urgency = "متوسط"
        elif sell_score >= 3 and buy_score <= 1:
            recommendation = "🔴 **بيع** - مؤشرات سلبية قوية"
            color = "red"
            action = "بيع"
            urgency = "عالي"
        elif sell_score >= 2:
            recommendation = "🟠 **مراقبة** - علامات تحذير"
            color = "orange"
            action = "مراقبة"
            urgency = "متوسط"
        else:
            recommendation = "⚪ **انتظار** - لا توجد إشارات واضحة"
            color = "gray"
            action = "انتظار"
            urgency = "منخفض"
        
        return {
            "recommendation": recommendation,
            "color": color,
            "action": action,
            "urgency": urgency,
            "buy_score": buy_score,
            "sell_score": sell_score
        }
    
    def add_alert_to_history(self, ticker: str, alert_type: str, signal: Dict, price: float):
        """إضافة تنبيه إلى السجل"""
        alert = {
            "ticker": ticker,
            "type": alert_type,
            "signal": signal.get('signal', ''),
            "action": signal.get('action', ''),
            "price": price,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reasons": signal.get('reasons', [])
        }
        
        st.session_state.all_alerts.insert(0, alert)
        
        # الاحتفاظ فقط بآخر 50 تنبيه
        if len(st.session_state.all_alerts) > 50:
            st.session_state.all_alerts = st.session_state.all_alerts[:50]
    
    def display_alerts_panel(self):
        """عرض لوحة التنبيهات"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🔔 آخر التنبيهات")
        
        if st.session_state.all_alerts:
            for alert in st.session_state.all_alerts[:5]:
                if "شراء" in alert['action']:
                    icon = "🟢"
                    color = "#00ff00"
                elif "بيع" in alert['action']:
                    icon = "🔴"
                    color = "#ff4444"
                else:
                    icon = "🟡"
                    color = "#ffaa00"
                
                st.sidebar.markdown(f"""
                <div style="
                    background-color: #1e1e1e;
                    border-left: 3px solid {color};
                    padding: 8px;
                    margin-bottom: 8px;
                    border-radius: 5px;
                ">
                    <small>{icon} <strong>{alert['ticker']}</strong></small><br>
                    <small style="color: {color};">{alert['action']}</small><br>
                    <small style="color: #888;">{alert['timestamp'][:16]}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if st.sidebar.button("🗑️ مسح التنبيهات", use_container_width=True):
                st.session_state.all_alerts = []
                st.rerun()
        else:
            st.sidebar.info("📭 لا توجد تنبيهات بعد")

# ====================== دوال إضافية ======================

@st.cache_data(ttl=300)
def get_stock_data(ticker: str, period: str = "6mo"):
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None
        
        # حساب المؤشرات
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['RSI'] = calculate_rsi(df['Close'], 14)
        
        return df, stock.info
    except Exception:
        return None, None

# ====================== واجهة المستخدم الرئيسية ======================

def main():
    # تهيئة نظام التنبيهات
    alert_system = TradingAlertSystem()
    
    st.title("🔔 بوت تحليل الأسهم - نظام تنبيهات البيع والشراء")
    st.markdown(f"**الإصدار {APP_VERSION}** | تنبيهات فورية | توصيات ذكاء اصطناعي")
    st.markdown("---")
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 📊 لوحة التحكم")
        st.metric("📈 إجمالي الأسهم", len(STOCKS))
        
        # حالة الذكاء الاصطناعي
        model = init_gemini()
        if model:
            st.success("🤖 Gemini: متصل")
        else:
            st.warning("⚠️ أضف مفتاح API")
        
        # إعدادات التنبيهات
        st.markdown("---")
        st.markdown("### ⚙️ إعدادات التنبيهات")
        auto_check = st.checkbox("تفعيل التنبيهات التلقائية", value=True)
        
        st.caption("📊 البيانات من Yahoo Finance")
        st.caption("🎯 نظام تنبيهات متكامل للبيع والشراء")
    
    # عرض لوحة التنبيهات في الشريط الجانبي
    alert_system.display_alerts_panel()
    
    # التبويبات الرئيسية
    tab1, tab2, tab3 = st.tabs(["📈 تحليل وتنبيهات", "📊 سجل التنبيهات", "ℹ️ عن النظام"])
    
    with tab1:
        st.header("🔍 تحليل السهم وتنبيهات البيع والشراء")
        
        # اختيار السهم
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input(
                "🔎 ابحث عن سهم",
                placeholder="مثال: CIB, أرامكو, AAPL",
                help="اكتب اسم الشركة أو رمز السهم"
            )
        
        with col2:
            period = st.selectbox("📅 الفترة", ["1mo", "3mo", "6mo", "1y"], index=2)
        
        if search_term:
            # البحث عن السهم
            found = {}
            for name, ticker in STOCKS.items():
                if search_term.lower() in name.lower() or search_term.lower() in ticker.lower():
                    found[name] = ticker
            
            if found:
                selected_name = st.selectbox("اختر السهم", list(found.keys()), 
                                            format_func=lambda x: f"{x} ({found[x]})")
                selected_ticker = found[selected_name]
                
                with st.spinner("جاري تحليل السهم..."):
                    df, info = get_stock_data(selected_ticker, period)
                
                if df is not None and not df.empty:
                    # حساب المؤشرات الأساسية
                    current_price = df['Close'].iloc[-1]
                    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
                    daily_change = ((current_price - prev_price) / prev_price) * 100
                    rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
                    
                    # حساب MACD
                    macd, macd_signal = calculate_macd(df['Close'])
                    
                    # حساب الدعم والمقاومة
                    support, resistance = calculate_support_resistance(df)
                    
                    # مقارنة السعر مع المتوسط
                    sma_20 = df['SMA_20'].iloc[-1] if not pd.isna(df['SMA_20'].iloc[-1]) else current_price
                    if current_price > sma_20:
                        price_vs_sma = "above"
                    else:
                        price_vs_sma = "below"
                    
                    # حجم التداول
                    avg_volume = df['Volume'].tail(20).mean()
                    volume_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
                    
                    # الاتجاه العام
                    if len(df) >= 20:
                        old_price = df['Close'].iloc[-20]
                        trend_pct = ((current_price - old_price) / old_price) * 100
                        if trend_pct > 5:
                            trend = "صاعد"
                        elif trend_pct < -5:
                            trend = "هابط"
                        else:
                            trend = "جانبي"
                    else:
                        trend = "جانبي"
                    
                    # عرض معلومات الشركة
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("💰 السعر", f"{current_price:.2f}", f"{daily_change:+.2f}%")
                    with col2:
                        rsi_color = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡"
                        st.metric(f"{rsi_color} RSI", f"{rsi:.1f}")
                    with col3:
                        st.metric("📈 اتجاه", trend)
                    with col4:
                        st.metric("📊 حجم التداول", f"{volume_ratio:.1f}x")
                    
                    st.divider()
                    
                    # ====================== تحليل إشارات الشراء ======================
                    buy_analysis = alert_system.analyze_buy_signals(
                        selected_ticker, current_price, rsi, macd, macd_signal,
                        price_vs_sma, volume_ratio, trend
                    )
                    
                    # ====================== تحليل إشارات البيع ======================
                    sell_analysis = alert_system.analyze_sell_signals(
                        selected_ticker, current_price, rsi, macd, macd_signal,
                        price_vs_sma, volume_ratio, trend
                    )
                    
                    # ====================== التوصية النهائية ======================
                    overall = alert_system.get_overall_recommendation(buy_analysis, sell_analysis)
                    
                    # عرض التوصية بشكل بارز
                    st.markdown(f"""
                    <div style="
                        background-color: #1e1e1e;
                        border: 2px solid {overall['color']};
                        border-radius: 15px;
                        padding: 20px;
                        margin: 10px 0;
                        text-align: center;
                    ">
                        <h2 style="color: {overall['color']}; margin: 0;">
                            {overall['recommendation']}
                        </h2>
                        <p style="margin: 5px 0;">درجة الشراء: {overall['buy_score']} | درجة البيع: {overall['sell_score']}</p>
                        <p style="margin: 5px 0;">درجة الإلحاح: {overall['urgency']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # عرض إشارات الشراء والبيع في عمودين
                    col_buy, col_sell = st.columns(2)
                    
                    with col_buy:
                        st.markdown("### 🟢 إشارات الشراء")
                        st.markdown(f"**{buy_analysis['signal']}**")
                        st.markdown(f"**الإجراء:** {buy_analysis['action']}")
                        st.markdown(f"**الثقة:** {buy_analysis['confidence']}")
                        if buy_analysis['suggested_allocation']:
                            st.markdown(f"**نسبة الاستثمار المقترحة:** {buy_analysis['suggested_allocation']}")
                        st.markdown("**الأسباب:**")
                        for reason in buy_analysis['reasons'][:5]:
                            st.markdown(f"- {reason}")
                    
                    with col_sell:
                        st.markdown("### 🔴 إشارات البيع")
                        st.markdown(f"**{sell_analysis['signal']}**")
                        st.markdown(f"**الإجراء:** {sell_analysis['action']}")
                        st.markdown(f"**الثقة:** {sell_analysis['confidence']}")
                        st.markdown("**الأسباب:**")
                        for reason in sell_analysis['reasons'][:5]:
                            st.markdown(f"- {reason}")
                    
                    # أزرار إضافة التنبيهات
                    st.divider()
                    st.markdown("### 🎯 إجراءات سريعة")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("➕ إضافة تنبيه شراء", use_container_width=True):
                            alert_system.add_alert_to_history(
                                selected_ticker, "شراء", buy_analysis, current_price
                            )
                            st.success("✅ تم إضافة تنبيه الشراء إلى السجل!")
                            time.sleep(1)
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("⚠️ إضافة تنبيه بيع", use_container_width=True):
                            alert_system.add_alert_to_history(
                                selected_ticker, "بيع", sell_analysis, current_price
                            )
                            st.success("✅ تم إضافة تنبيه البيع إلى السجل!")
                            time.sleep(1)
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("🤖 تحليل بالذكاء الاصطناعي", use_container_width=True):
                            if model:
                                with st.spinner("جاري التحليل..."):
                                    prompt = f"""
                                    محلل أسهم محترف. حلل السهم {selected_ticker}:
                                    السعر: {current_price:.2f}
                                    RSI: {rsi:.1f}
                                    التوصية الفنية: {overall['recommendation']}
                                    إشارات الشراء: {buy_analysis['reasons'][:3]}
                                    إشارات البيع: {sell_analysis['reasons'][:3]}
                                    
                                    قدم توصية نهائية مختصرة (البيع أو الشراء أو الانتظار) مع الأسباب.
                                    """
                                    response = model.generate_content(prompt)
                                    st.info(f"🧠 **تحليل Gemini:**\n\n{response.text}")
                            else:
                                st.error("الذكاء الاصطناعي غير متوفر")
                    
                    # عرض مستويات الدعم والمقاومة
                    st.divider()
                    col_sup, col_res = st.columns(2)
                    with col_sup:
                        st.metric("🛡️ مستوى الدعم", f"{support:.2f}")
                        if current_price <= support * 1.02:
                            st.warning("⚠️ السهم قريب من مستوى الدعم!")
                    with col_res:
                        st.metric("⚡ مستوى المقاومة", f"{resistance:.2f}")
                        if current_price >= resistance * 0.98:
                            st.warning("⚠️ السهم قريب من مستوى المقاومة!")
                    
                    # رسم بياني
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="السعر", line=dict(color='cyan')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name="SMA 20", line=dict(color='orange', dash='dash')))
                    fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="دعم")
                    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="مقاومة")
                    fig.update_layout(template="plotly_dark", height=400, title=f"تحليل {selected_ticker}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error("لا توجد بيانات للسهم")
            else:
                st.warning("لم يتم العثور على السهم")
    
    with tab2:
        st.header("📋 سجل التنبيهات")
        
        if st.session_state.all_alerts:
            # إحصائيات سريعة
            buy_count = len([a for a in st.session_state.all_alerts if "شراء" in a.get('action', '')])
            sell_count = len([a for a in st.session_state.all_alerts if "بيع" in a.get('action', '')])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 إجمالي التنبيهات", len(st.session_state.all_alerts))
            col2.metric("🟢 تنبيهات شراء", buy_count)
            col3.metric("🔴 تنبيهات بيع", sell_count)
            
            st.divider()
            
            # عرض جميع التنبيهات
            for alert in st.session_state.all_alerts:
                if "شراء" in alert.get('action', ''):
                    emoji = "🟢"
                    color = "#00ff00"
                elif "بيع" in alert.get('action', ''):
                    emoji = "🔴"
                    color = "#ff4444"
                else:
                    emoji = "🟡"
                    color = "#ffaa00"
                
                with st.expander(f"{emoji} {alert['ticker']} - {alert['action']} - {alert['timestamp']}"):
                    st.write(f"**الإشارة:** {alert['signal']}")
                    st.write(f"**السعر:** {alert['price']:.2f}")
                    st.write("**الأسباب:**")
                    for reason in alert.get('reasons', [])[:5]:
                        st.write(f"- {reason}")
            
            if st.button("🗑️ مسح كل التنبيهات"):
                st.session_state.all_alerts = []
                st.rerun()
        else:
            st.info("📭 لا توجد تنبيهات مسجلة. قم بتحليل الأسهم وإضافة التنبيهات")
    
    with tab3:
        st.header("ℹ️ نظام تنبيهات البيع والشراء")
        st.markdown("""
        ### 🎯 كيف يعمل نظام التنبيهات؟
        
        **إشارات الشراء (Buy Signals):**
        - 🔴 **شراء قوي جداً** (5+ نقاط): RSI منخفض جداً + MACD إيجابي + اتجاه صاعد
        - 🟠 **شراء جيد** (3-4 نقاط): RSI منخفض + إشارات إيجابية
        - 🟡 **شراء ضعيف** (2 نقاط): بعض المؤشرات الإيجابية
        
        **إشارات البيع (Sell Signals):**
        - 🔴 **بيع قوي** (5+ نقاط): RSI مرتفع جداً + MACD سلبي + اتجاه هابط
        - 🟠 **بيع** (3-4 نقاط): مؤشرات سلبية واضحة
        - 🟡 **مراقبة** (2 نقاط): علامات تحذير مبكرة
        
        **المؤشرات المستخدمة:**
        - RSI (مؤشر القوة النسبية)
        - MACD (تقاطع المتوسطات)
        - المتوسطات المتحركة
        - حجم التداول
        - الاتجاه العام
        - الدعم والمقاومة
        
        **نصائح مهمة:**
        ⚠️ هذه التنبيهات للأغراض التعليمية فقط
        ⚠️ لا تعتبر نصيحة استثمارية
        ⚠️ يفضل دائمًا إجراء البحث الخاص بك
        """)

if __name__ == "__main__":
    main()
