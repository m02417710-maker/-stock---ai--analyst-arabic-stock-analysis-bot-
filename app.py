# app.py - النسخة النهائية (جميع الأزرار تعمل بشكل سلس)
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
import hashlib

from database import (
    get_all_egyptian_stocks, 
    get_stocks_by_sector, 
    get_all_sectors,
    search_stock,
    get_market_statistics,
    get_market_info,
    EGYPTIAN_STOCKS
)

# استيراد وحدات البحث
from search_utils import (
    search_google, 
    search_stock_news, 
    search_market_news,
    search_commodity_news,
    smart_search,
    analyze_news_with_gemini
)

# إعداد الصفحة
st.set_page_config(
    page_title="تحليل البورصة المصرية - جميع الأسهم",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================== تهيئة حالة الجلسة ======================
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = None
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False
if 'refresh_market_news' not in st.session_state:
    st.session_state.refresh_market_news = True

# ====================== CSS للتنسيق ======================
st.markdown("""
<style>
    /* تنسيق عام */
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 20px;
    }
    /* تنسيق الأزرار */
    .stButton > button {
        background: linear-gradient(45deg, #ff4b4b, #ff9068);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 25px;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: bold;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255,75,75,0.3);
    }
    /* تنسيق البطاقات */
    .stock-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #444;
        transition: all 0.3s ease;
    }
    .stock-card:hover {
        transform: translateY(-5px);
        border-color: #ff4b4b;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    /* تنسيق التحليل */
    .analysis-container {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid #ff4b4b;
    }
    /* تنسيق العناوين */
    h1, h2, h3 {
        direction: rtl;
    }
    /* تنسيق المقاييس */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

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

def select_stock(ticker: str, name: str):
    """دالة لاختيار السهم وعرض التحليل"""
    st.session_state.selected_ticker = ticker
    st.session_state.selected_name = name
    st.session_state.show_analysis = True
    st.rerun()

def clear_selection():
    """مسح الاختيار"""
    st.session_state.selected_ticker = None
    st.session_state.selected_name = None
    st.session_state.show_analysis = False
    st.rerun()

# ====================== عرض التحليل الفني ======================
def display_technical_analysis():
    """عرض التحليل الفني للسهم المختار"""
    
    if not st.session_state.show_analysis or not st.session_state.selected_ticker:
        return False
    
    st.markdown("---")
    st.markdown(f"""
    <div class="analysis-container">
        <h2>📈 التحليل الفني: {st.session_state.selected_name}</h2>
        <p style="color: #aaa;">الرمز: <code>{st.session_state.selected_ticker}</code> | السوق: البورصة المصرية (EGX)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # خيارات التحليل
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        period = st.selectbox(
            "📅 الفترة الزمنية",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            key="analysis_period"
        )
    with col2:
        auto_analyze = st.checkbox("🤖 تحليل ذكي", value=False, key="auto_analyze")
    with col3:
        if st.button("🗑️ مسح", key="clear_analysis_btn", use_container_width=True):
            clear_selection()
    
    with st.spinner("جاري تحميل البيانات..."):
        hist, info = get_stock_data(st.session_state.selected_ticker, period)
    
    if hist is not None and not hist.empty:
        # المقاييس الأساسية
        curr_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
        change_pct = ((curr_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
        volume = hist['Volume'].iloc[-1]
        
        # عرض المقاييس في بطاقات
        st.markdown("### 📊 المؤشرات الرئيسية")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰 السعر الحالي</h3>
                <p style="font-size: 24px; color: #ff4b4b;">{curr_price:.2f} ج.م</p>
                <p style="color: {'green' if change_pct >= 0 else 'red'};">{change_pct:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 مؤشر RSI</h3>
                <p style="font-size: 24px; color: {'#ff4b4b' if rsi > 70 else '#51cf66' if rsi < 30 else '#ffd43b'};">{rsi:.1f}</p>
                <p>{'ذروة شراء' if rsi > 70 else 'ذروة بيع' if rsi < 30 else 'متوازن'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📈 SMA 20</h3>
                <p style="font-size: 24px;">{hist['SMA_20'].iloc[-1]:.2f} ج.م</p>
                <p>المتوسط المتحرك</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📦 حجم التداول</h3>
                <p style="font-size: 20px;">{volume:,.0f}</p>
                <p>سهم</p>
            </div>
            """, unsafe_allow_html=True)
        
        # تنبيه RSI
        show_rsi_alert(rsi)
        
        # معلومات الشركة
        if info:
            with st.expander("ℹ️ معلومات الشركة"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**الاسم:** {info.get('longName', 'غير متوفر')}")
                    st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")
                    st.write(f"**العملة:** {info.get('currency', 'EGP')}")
                with col2:
                    market_cap = info.get('marketCap', 0)
                    if market_cap:
                        st.write(f"**القيمة السوقية:** {market_cap/1e9:.2f} مليار ج.م")
                    st.write(f"**أعلى 52 أسبوع:** {info.get('fiftyTwoWeekHigh', 'غير متوفر')}")
                    st.write(f"**أدنى 52 أسبوع:** {info.get('fiftyTwoWeekLow', 'غير متوفر')}")
        
        # الرسم البياني
        st.markdown("### 📈 الرسم البياني الفني")
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=("حركة السعر", "مؤشر RSI", "حجم التداول")
        )
        
        # السعر والمتوسطات
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر", 
                                 line=dict(color='cyan', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", 
                                 line=dict(dash='dash', color='orange', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA_9'], name="EMA 9", 
                                 line=dict(dash='dot', color='yellow', width=1.5)), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI", 
                                 line=dict(color='magenta', width=2)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="ذروة شراء", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="ذروة بيع", row=2, col=1)
        
        # حجم التداول
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(hist['Close'], hist['Open'])]
        fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Volume",
                            marker_color=colors, opacity=0.5), row=3, col=1)
        
        fig.update_layout(height=700, template="plotly_dark", showlegend=True)
        fig.update_xaxes(rangeslider_visible=False)
        fig.update_yaxes(title_text="السعر (ج.م)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="الحجم", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # التحليل بالذكاء الاصطناعي
        if auto_analyze or st.button("🤖 تحليل ذكي بالذكاء الاصطناعي", type="primary", use_container_width=True):
            model = init_gemini()
            if model:
                with st.spinner("🧠 جاري التحليل الذكي..."):
                    prompt = f"""
                    أنت خبير في تحليل البورصة المصرية. حلل السهم التالي:
                    
                    السهم: {st.session_state.selected_name}
                    الرمز: {st.session_state.selected_ticker}
                    السعر الحالي: {curr_price:.2f} جنيه مصري
                    مؤشر RSI: {rsi:.1f}
                    التغير اليومي: {change_pct:+.2f}%
                    
                    قدم تحليلاً فنياً مختصراً بالعربية يشمل:
                    1. اتجاه السهم (صاعد/هابط/جانبي)
                    2. تحليل RSI وحالة السهم
                    3. نقاط الدعم والمقاومة المتوقعة
                    4. توصية للمستثمر
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("### 📝 نتيجة التحليل الذكي")
                        st.success(response.text)
                    except Exception as e:
                        st.error(f"خطأ في التحليل: {e}")
            else:
                st.warning("⚠️ يرجى إضافة مفتاح Gemini API لتفعيل التحليل الذكي")
        
        return True
    else:
        st.error("❌ تعذر جلب بيانات السهم")
        return False

# ====================== إحصائيات البورصة ======================
def show_stats_bar():
    """عرض إحصائيات البورصة"""
    stats = get_market_statistics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📈 إجمالي الأسهم", stats['total_stocks'])
    col2.metric("🏢 عدد القطاعات", stats['sectors'])
    col3.metric("💰 العملة", stats['currency'])
    col4.metric("⏰ وقت التداول", stats['trading_hours'])
    col5.metric("🤖 AI", "متصل" if init_gemini() else "غير متصل")

# ====================== تبويب الأسهم ======================
def stocks_tab():
    """تبويب الأسهم والبحث"""
    
    st.markdown("## 🔍 ابحث عن سهم")
    
    # شريط البحث
    search_term = st.text_input("", placeholder="🔎 اكتب اسم السهم أو رمزه للبحث...", key="search_input")
    
    if search_term:
        results = search_stock(search_term)
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            cols = st.columns(3)
            for idx, (stock_name, stock_data) in enumerate(results.items()):
                with cols[idx % 3]:
                    if st.button(f"📊 {stock_name}", key=f"search_result_{idx}", use_container_width=True):
                        select_stock(stock_data['ticker'], stock_name)
    
    st.markdown("---")
    st.markdown("## 📋 تصفح جميع الأسهم")
    
    # فلتر القطاعات
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_sector = st.selectbox("🏢 فلتر حسب القطاع", ["جميع القطاعات"] + get_all_sectors(), key="sector_filter")
    with col2:
        st.markdown("")
    
    # عرض الأسهم
    all_stocks = get_all_egyptian_stocks()
    
    if selected_sector != "جميع القطاعات":
        sector_stocks = get_stocks_by_sector(selected_sector)
        stock_items = list(sector_stocks.items())
    else:
        stock_items = list(all_stocks.items())
    
    st.caption(f"📊 عرض {len(stock_items)} سهماً")
    
    # عرض الأسهم في شبكة
    cols = st.columns(4)
    for idx, (name, ticker) in enumerate(stock_items):
        with cols[idx % 4]:
            with st.container():
                st.markdown(f"""
                <div class="stock-card">
                    <h4>{name[:35]}</h4>
                    <code>{ticker}</code>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"تحليل", key=f"stock_{ticker}_{idx}", use_container_width=True):
                    select_stock(ticker, name)

# ====================== تبويب القطاعات ======================
def sectors_tab():
    """تبويب عرض الأسهم حسب القطاعات"""
    
    st.markdown("## 🏢 أسهم البورصة المصرية حسب القطاع")
    
    sectors = get_all_sectors()
    
    for sector_idx, sector in enumerate(sectors):
        sector_stocks = get_stocks_by_sector(sector)
        with st.expander(f"📂 {sector} ({len(sector_stocks)} سهم)", expanded=False):
            cols = st.columns(3)
            for stock_idx, (name, ticker) in enumerate(sector_stocks.items()):
                with cols[stock_idx % 3]:
                    if st.button(f"📈 {name}", key=f"sector_{sector_idx}_{stock_idx}", use_container_width=True):
                        select_stock(ticker, name)
                    st.caption(f"`{ticker}`")

# ====================== تبويب الأخبار ======================
def news_tab():
    """تبويب الأخبار"""
    
    st.markdown("## 📰 أخبار البورصة المصرية")
    
    with st.spinner("جاري جلب الأخبار..."):
        market_news = search_market_news()
        
        if market_news:
            for idx, news in enumerate(market_news[:10]):
                with st.container():
                    st.markdown(f"""
                    <div style="border-bottom: 1px solid #333; padding: 15px 0;">
                        <h4>{idx+1}. {news['title']}</h4>
                        <p style="color: #aaa;">{news['snippet']}</p>
                        <small>📰 {news['display_link']}</small>
                        <br/>
                        <a href="{news['link']}" target="_blank">🔗 اقرأ المزيد</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # زر لتحليل الخبر
                    if st.button(f"🤖 تحليل هذا الخبر", key=f"analyze_news_{idx}"):
                        analysis = analyze_news_with_gemini(news['snippet'])
                        st.info(analysis)
        else:
            st.warning("لا توجد أخبار حالياً")

# ====================== الدالة الرئيسية ======================
def main():
    """التطبيق الرئيسي"""
    
    # رأس الصفحة
    st.markdown("""
    <div class="main-header">
        <h1>🇪🇬 بوت تحليل البورصة المصرية</h1>
        <p>جميع أسهم البورصة المصرية (EGX) | تحليل فني متقدم | ذكاء اصطناعي | أخبار فورية</p>
    </div>
    """, unsafe_allow_html=True)
    
    # شريط الإحصائيات
    show_stats_bar()
    
    # عرض التحليل الفني إذا تم اختيار سهم
    if display_technical_analysis():
        pass
    else:
        # تبويبات التصفح
        tab1, tab2, tab3 = st.tabs(["📈 تصفح الأسهم", "🏢 القطاعات", "📰 الأخبار"])
        
        with tab1:
            stocks_tab()
        
        with tab2:
            sectors_tab()
        
        with tab3:
            news_tab()
    
    # تذييل
    st.markdown("---")
    st.caption("🇪🇬 **البورصة المصرية (EGX)** | البيانات من Yahoo Finance | التحليل بالذكاء الاصطناعي | للأغراض التعليمية")

if __name__ == "__main__":
    main()
