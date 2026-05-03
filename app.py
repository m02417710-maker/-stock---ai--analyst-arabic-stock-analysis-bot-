# app.py - تطبيق تحليل جميع أسهم البورصة المصرية
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas_ta as ta
from datetime import datetime

from database import (
    get_all_egyptian_stocks, 
    get_stocks_by_sector, 
    get_all_sectors,
    search_stock,
    get_market_statistics,
    get_market_info,
    EGYPTIAN_STOCKS
)

# إعداد الصفحة
st.set_page_config(
    page_title="تحليل البورصة المصرية - جميع الأسهم",
    page_icon="🇪🇬",
    layout="wide"
)

# العنوان الرئيسي
st.title("🇪🇬 بوت تحليل البورصة المصرية - شامل جميع الأسهم")
st.markdown("**جميع أسهم البورصة المصرية (EGX) | تحليل فني + ذكاء اصطناعي**")

# ====================== إعداد Gemini ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي"""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== دوال التحليل ======================
@st.cache_data(ttl=300)
def get_stock_data(ticker: str, period: str = "1y"):
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
        return None, None

def show_rsi_alert(rsi_value: float):
    """عرض تنبيه RSI"""
    if rsi_value > 70:
        st.error(f"⚠️ **تنبيه: منطقة تشبع شرائي!** RSI = {rsi_value:.1f}")
    elif rsi_value < 30:
        st.success(f"✅ **فرصة: منطقة تشبع بيعي!** RSI = {rsi_value:.1f}")
    else:
        st.info(f"ℹ️ السهم في منطقة حيادية - RSI = {rsi_value:.1f}")

# ====================== الشريط الجانبي ======================
with st.sidebar:
    st.markdown("## 📊 إحصائيات البورصة المصرية")
    
    stats = get_market_statistics()
    st.metric("📈 إجمالي الأسهم المتداولة", stats['total_stocks'])
    st.metric("🏢 عدد القطاعات", stats['sectors'])
    st.metric("💰 العملة", stats['currency'])
    st.metric("⏰ وقت التداول", stats['trading_hours'])
    
    st.divider()
    
    st.markdown("## 📂 القطاعات")
    for sector, count in stats['sectors_stats'].items():
        st.caption(f"• {sector}: {count} سهم")
    
    st.divider()
    
    # حالة الذكاء الاصطناعي
    model = init_gemini()
    if model:
        st.success("🤖 Gemini AI: متصل")
    else:
        st.warning("⚠️ أضف GEMINI_API_KEY لتفعيل التحليل الذكي")

# ====================== البحث والتصفح ======================
tab1, tab2, tab3 = st.tabs(["🔍 بحث عن سهم", "📋 تصفح جميع الأسهم", "🏢 حسب القطاع"])

selected_ticker = None
selected_name = None

with tab1:
    st.markdown("### 🔍 ابحث عن أي سهم في البورصة المصرية")
    
    search_term = st.text_input(
        "اكتب اسم السهم أو الرمز",
        placeholder="مثال: CIB, البنك التجاري الدولي, COMI.CA",
        help="ابحث بالاسم العربي أو الرمز"
    )
    
    if search_term:
        results = search_stock(search_term)
        
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            for stock_name, stock_data in results.items():
                with st.expander(f"📈 {stock_name} - {stock_data['ticker']}"):
                    if st.button(f"تحليل {stock_name}", key=f"search_{stock_data['ticker']}"):
                        selected_ticker = stock_data['ticker']
                        selected_name = stock_name
        else:
            st.warning("❌ لم يتم العثور على نتائج")

with tab2:
    st.markdown("### 📋 جميع أسهم البورصة المصرية")
    
    all_stocks = get_all_egyptian_stocks()
    
    # إضافة خيار البحث السريع
    filter_text = st.text_input("🔎 فلتر سريع", placeholder="اكتب جزء من اسم السهم...")
    
    filtered_stocks = all_stocks
    if filter_text:
        filtered_stocks = {k: v for k, v in all_stocks.items() if filter_text.lower() in k.lower() or filter_text.upper() in v}
    
    st.caption(f"عرض {len(filtered_stocks)} من {len(all_stocks)} سهماً")
    
    # عرض في عمودين
    col1, col2 = st.columns(2)
    for i, (name, ticker) in enumerate(filtered_stocks.items()):
        with col1 if i % 2 == 0 else col2:
            # for i, (name, ticker) in enumerate(market_info['stocks'].items()):
    if st.button(f"📊 {name} ({ticker})", key=f"nav_btn_{ticker}_{i}"):
        st.session_state.selected_ticker = ticker
        st.rerun()
selected_ticker = ticker
                selected_name = name

with tab3:
    st.markdown("### 🏢 تصفح حسب القطاع الاقتصادي")
    
    sectors = get_all_sectors()
    selected_sector = st.selectbox("اختر القطاع", sectors)
    
    if selected_sector:
        sector_stocks = get_stocks_by_sector(selected_sector)
        st.subheader(f"أسهم قطاع {selected_sector} ({len(sector_stocks)} سهم)")
        
        for name, ticker in sector_stocks.items():
            if st.button(f"📈 {name} ({ticker})", key=f"sector_{ticker}"):
                selected_ticker = ticker
                selected_name = name

# ====================== التحليل ======================
if selected_ticker and selected_name:
    st.divider()
    st.header(f"📊 تحليل السهم: {selected_name}")
    st.caption(f"الرمز: `{selected_ticker}`")
    
    # فترة التحليل
    period = st.selectbox(
        "📅 الفترة الزمنية للتحليل",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )
    
    with st.spinner("جاري تحميل بيانات السهم..."):
        hist, info = get_stock_data(selected_ticker, period)
    
    if hist is not None and not hist.empty:
        # المقاييس الأساسية
        curr_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
        change_pct = ((curr_price - prev_price) / prev_price) * 100
        rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 السعر الحالي", f"{curr_price:.2f} ج.م", f"{change_pct:+.2f}%")
        col2.metric("📊 مؤشر RSI", f"{rsi:.1f}")
        col3.metric("📈 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
        col4.metric("🏢 الشركة", info.get('longName', selected_name)[:20] if info else selected_name[:20])
        
        # تنبيه RSI
        show_rsi_alert(rsi)
        
        # الرسم البياني
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
        
        # خط السعر مع المتوسطات المتحركة
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر", 
                                 line=dict(color='cyan', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", 
                                 line=dict(dash='dash', color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA_9'], name="EMA 9", 
                                 line=dict(dash='dot', color='yellow')), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI", 
                                 line=dict(color='magenta')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        fig.update_layout(height=600, template="plotly_dark", title=f"تحليل فني - {selected_name}")
        fig.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # التحليل بالذكاء الاصطناعي
        if st.button("🤖 تحليل ذكي باستخدام الذكاء الاصطناعي", type="primary", use_container_width=True):
            model = init_gemini()
            if model:
                with st.spinner("🧠 جاري التحليل الذكي..."):
                    prompt = f"""
                    أنت خبير في تحليل البورصة المصرية. حلل السهم التالي:
                    
                    السهم: {selected_name}
                    الرمز: {selected_ticker}
                    السعر الحالي: {curr_price:.2f} جنيه مصري
                    مؤشر RSI: {rsi:.1f}
                    التغير اليومي: {change_pct:+.2f}%
                    
                    قدم تحليلاً فنياً مختصراً بالعربية يشمل:
                    1. اتجاه السهم (صاعد/هابط/جانبي)
                    2. تحليل RSI وحالة السهم
                    3. توصية مختصرة
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("### 📝 نتيجة التحليل")
                        st.success(response.text)
                    except Exception as e:
                        st.error(f"خطأ في التحليل: {e}")
            else:
                st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في ملف .streamlit/secrets.toml لتفعيل التحليل الذكي")
    
    else:
        st.error("❌ تعذر جلب بيانات السهم. تأكد من الرمز وحاول مرة أخرى")

# تذييل الصفحة
st.divider()
st.caption("🇪🇬 **البورصة المصرية (EGX)** | البيانات من Yahoo Finance | للاستخدام التعليمي")
