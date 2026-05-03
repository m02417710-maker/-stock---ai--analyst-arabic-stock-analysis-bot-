# app.py - النسخة النهائية الكاملة (جميع الأزرار تعمل بدون أخطاء)
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
import random

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
    page_title="تحليل البورصة المصرية - المنصة المتكاملة",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================== تهيئة حالة الجلسة ======================
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = None
if 'refresh_market_news' not in st.session_state:
    st.session_state.refresh_market_news = True
if 'search_stock_news' not in st.session_state:
    st.session_state.search_stock_news = None
if 'button_counter' not in st.session_state:
    st.session_state.button_counter = 0

def get_unique_button_id():
    """توليد معرف فريد لكل زر"""
    st.session_state.button_counter += 1
    return f"btn_{st.session_state.button_counter}_{random.randint(10000, 99999)}"

# ====================== CSS للتنسيق الاحترافي ======================
st.markdown("""
<style>
    /* تنسيق عام */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    /* تنسيق الأزرار */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 14px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px 0;
        text-align: left;
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #444;
        color: white;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2a2a3e, #3a3a4e);
        transform: translateY(-2px);
        border-color: #ff4b4b;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    /* تنسيق البطاقات */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background: rgba(255,255,255,0.05);
    }
    /* تنسيق العناوين */
    h1, h2, h3 {
        direction: rtl;
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

@st.cache_data(ttl=300)
def get_stock_signal(ticker: str):
    """الحصول على إشارة السهم (شراء/بيع/حيادي)"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        if df.empty or len(df) < 14:
            return "neutral", 50, 0, df['Close'].iloc[-1] if not df.empty else 0
        
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        
        if rsi < 30:
            return "buy", rsi, change_pct, current_price
        elif rsi > 70:
            return "sell", rsi, change_pct, current_price
        else:
            return "neutral", rsi, change_pct, current_price
    except:
        return "neutral", 50, 0, 0

def show_rsi_alert(rsi_value: float):
    """عرض تنبيه RSI"""
    if rsi_value > 70:
        st.error(f"⚠️ **تنبيه: منطقة تشبع شرائي!** RSI = {rsi_value:.1f}")
    elif rsi_value < 30:
        st.success(f"✅ **فرصة: منطقة تشبع بيعي!** RSI = {rsi_value:.1f}")
    else:
        st.info(f"ℹ️ السهم في منطقة حيادية - RSI = {rsi_value:.1f}")

def select_stock(ticker: str, name: str):
    """دالة لاختيار السهم"""
    st.session_state.selected_ticker = ticker
    st.session_state.selected_name = name
    st.rerun()

def clear_selection():
    """مسح الاختيار"""
    st.session_state.selected_ticker = None
    st.session_state.selected_name = None
    st.rerun()

# ====================== عرض التحليل الفني ======================
def display_technical_analysis():
    """عرض التحليل الفني للسهم المختار"""
    
    if st.session_state.selected_ticker is None:
        return False
    
    st.markdown("---")
    st.header(f"📈 التحليل الفني: {st.session_state.selected_name}")
    st.caption(f"الرمز: `{st.session_state.selected_ticker}` | السوق: البورصة المصرية (EGX)")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        period = st.selectbox(
            "📅 الفترة الزمنية",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            key="analysis_period"
        )
    with col2:
        auto_analyze = st.checkbox("🤖 تحليل تلقائي", value=False, key="auto_analyze")
    with col3:
        if st.button("🗑️ مسح والعودة للقائمة", key="clear_btn", use_container_width=True):
            clear_selection()
    
    with st.spinner("جاري تحميل البيانات..."):
        hist, info = get_stock_data(st.session_state.selected_ticker, period)
    
    if hist is not None and not hist.empty:
        curr_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
        change_pct = ((curr_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
        
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
            rsi_color = '#ff4b4b' if rsi > 70 else '#51cf66' if rsi < 30 else '#ffd43b'
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 مؤشر RSI</h3>
                <p style="font-size: 24px; color: {rsi_color};">{rsi:.1f}</p>
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
                <p style="font-size: 20px;">{hist['Volume'].iloc[-1]:,.0f}</p>
                <p>سهم</p>
            </div>
            """, unsafe_allow_html=True)
        
        show_rsi_alert(rsi)
        
        # معلومات إضافية عن الشركة
        if info:
            with st.expander("ℹ️ معلومات إضافية عن الشركة"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**الاسم:** {info.get('longName', 'غير متوفر')}")
                    st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")
                    st.write(f"**العملة:** {info.get('currency', 'EGP')}")
                with col2:
                    if info.get('marketCap'):
                        st.write(f"**القيمة السوقية:** {info.get('marketCap', 0)/1e9:.2f} مليار ج.م")
                    st.write(f"**أعلى 52 أسبوع:** {info.get('fiftyTwoWeekHigh', 'غير متوفر')}")
                    st.write(f"**أدنى 52 أسبوع:** {info.get('fiftyTwoWeekLow', 'غير متوفر')}")
        
        # الرسم البياني
        st.subheader("📊 الرسم البياني الفني")
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر", line=dict(color='cyan', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", line=dict(dash='dash', color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA_9'], name="EMA 9", line=dict(dash='dot', color='yellow')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI", line=dict(color='magenta')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.update_layout(height=500, template="plotly_dark")
        fig.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # التحليل بالذكاء الاصطناعي
        analyze_clicked = st.button("🤖 تحليل ذكي بالذكاء الاصطناعي", type="primary", use_container_width=True, key="ai_analyze_btn")
        
        if auto_analyze or analyze_clicked:
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
                    
                    قدم تحليلاً فنياً مختصراً بالعربية.
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("### 📝 نتيجة التحليل الذكي")
                        st.success(response.text)
                    except Exception as e:
                        st.error(f"خطأ في التحليل: {e}")
            else:
                st.warning("⚠️ يرجى إضافة مفتاح Gemini API")
        
        return True
    else:
        st.error("❌ تعذر جلب بيانات السهم")
        return True

# ====================== عرض زر السهم (النسخة النهائية) ======================
def display_stock_card(name: str, ticker: str, signal_data: tuple, unique_id: int = 0):
    """عرض زر سهم يعمل 100% مع مفتاح فريد"""
    
    signal, rsi, change_pct, price = signal_data
    
    if signal == "buy":
        emoji = "🟢"
        signal_text = "شراء"
    elif signal == "sell":
        emoji = "🔴"
        signal_text = "بيع"
    else:
        emoji = "🟡"
        signal_text = "مراقبة"
    
    change_symbol = "▲" if change_pct >= 0 else "▼"
    change_color = "#00ff00" if change_pct >= 0 else "#ff4444"
    
    # نص الزر مع كل المعلومات
    button_text = f"{emoji} {name[:40]} | 💰{price:.2f} | {change_symbol}{abs(change_pct):.1f}% | 📊RSI:{rsi:.0f} | {signal_text}"
    
    # مفتاح فريد 100% باستخدام ticker والرقم الفريد
    unique_key = f"stock_btn_{ticker}_{unique_id}"
    
    # زر واحد فقط
    if st.button(button_text, key=unique_key, use_container_width=True):
        select_stock(ticker, name)

# ====================== تبويب تحليل السهم ======================
def stock_analysis_tab():
    """تبويب تحليل السهم"""
    
    st.markdown("### 🔍 ابحث عن سهم")
    
    search_term = st.text_input(
        "اكتب اسم السهم أو رمزه",
        placeholder="مثال: CIB, البنك التجاري الدولي, COMI.CA",
        key="main_search_input"
    )
    
    if search_term:
        results = search_stock(search_term)
        
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            buy_stocks = []
            sell_stocks = []
            neutral_stocks = []
            
            for stock_name, stock_data in results.items():
                signal_data = get_stock_signal(stock_data['ticker'])
                signal = signal_data[0]
                
                if signal == "buy":
                    buy_stocks.append((stock_name, stock_data['ticker'], signal_data))
                elif signal == "sell":
                    sell_stocks.append((stock_name, stock_data['ticker'], signal_data))
                else:
                    neutral_stocks.append((stock_name, stock_data['ticker'], signal_data))
            
            if sell_stocks:
                st.markdown("### 🔴 أسهم يوصى ببيعها (ذروة شراء)")
                for idx, (name, ticker, sig_data) in enumerate(sell_stocks):
                    display_stock_card(name, ticker, sig_data, idx)
            
            if buy_stocks:
                st.markdown("### 🟢 أسهم يوصى بشرائها (ذروة بيع)")
                for idx, (name, ticker, sig_data) in enumerate(buy_stocks):
                    display_stock_card(name, ticker, sig_data, idx + 100)
            
            if neutral_stocks:
                st.markdown("### 🟡 أسهم للمراقبة (منطقة حيادية)")
                for idx, (name, ticker, sig_data) in enumerate(neutral_stocks):
                    display_stock_card(name, ticker, sig_data, idx + 200)
    
    st.divider()
    
    st.markdown("### 📋 جميع أسهم البورصة المصرية")
    
    all_stocks = get_all_egyptian_stocks()
    
    filter_text = st.text_input("🔎 فلتر سريع", placeholder="اكتب جزء من اسم السهم...", key="filter_input")
    
    filtered_stocks = all_stocks
    if filter_text:
        filtered_stocks = {k: v for k, v in all_stocks.items() if filter_text.lower() in k.lower() or filter_text.upper() in v}
    
    st.caption(f"📊 عرض {len(filtered_stocks)} من {len(all_stocks)} سهماً")
    
    st.markdown("### 🏆 أسهم البورصة المصرية مرتبة حسب الإشارات")
    
    buy_list = []
    sell_list = []
    neutral_list = []
    
    with st.spinner("جاري تحليل الأسهم..."):
        for name, ticker in list(filtered_stocks.items()):
            signal_data = get_stock_signal(ticker)
            signal = signal_data[0]
            
            if signal == "buy":
                buy_list.append((name, ticker, signal_data))
            elif signal == "sell":
                sell_list.append((name, ticker, signal_data))
            else:
                neutral_list.append((name, ticker, signal_data))
    
    if sell_list:
        st.markdown("## 🔴 أسهم يوصى ببيعها")
        st.markdown("> *السهم في منطقة ذروة شراء - احتمال تصحيح*")
        for idx, (name, ticker, sig_data) in enumerate(sell_list):
            display_stock_card(name, ticker, sig_data, idx + 500)
    
    if buy_list:
        st.markdown("## 🟢 أسهم يوصى بشرائها")
        st.markdown("> *السهم في منطقة ذروة بيع - فرصة شراء*")
        for idx, (name, ticker, sig_data) in enumerate(buy_list):
            display_stock_card(name, ticker, sig_data, idx + 600)
    
    if neutral_list:
        st.markdown("## 🟡 أسهم للمراقبة")
        st.markdown("> *السهم في منطقة حيادية - يحتاج لمتابعة*")
        for idx, (name, ticker, sig_data) in enumerate(neutral_list):
            display_stock_card(name, ticker, sig_data, idx + 700)

# ====================== تبويب القطاعات ======================
def sectors_tab():
    """تبويب القطاعات"""
    
    st.markdown("## 🏢 أسهم البورصة المصرية حسب القطاع")
    
    sectors = get_all_sectors()
    
    for sector_idx, sector in enumerate(sectors):
        sector_stocks = get_stocks_by_sector(sector)
        
        with st.expander(f"📂 {sector} ({len(sector_stocks)} سهم)", expanded=False):
            buy_sector = []
            sell_sector = []
            neutral_sector = []
            
            for name, ticker in sector_stocks.items():
                signal_data = get_stock_signal(ticker)
                signal = signal_data[0]
                
                if signal == "buy":
                    buy_sector.append((name, ticker, signal_data))
                elif signal == "sell":
                    sell_sector.append((name, ticker, signal_data))
                else:
                    neutral_sector.append((name, ticker, signal_data))
            
            if sell_sector:
                st.markdown("#### 🔴 يوصى ببيعها")
                for idx, (name, ticker, sig_data) in enumerate(sell_sector):
                    display_stock_card(name, ticker, sig_data, sector_idx * 1000 + idx)
            
            if buy_sector:
                st.markdown("#### 🟢 يوصى بشرائها")
                for idx, (name, ticker, sig_data) in enumerate(buy_sector):
                    display_stock_card(name, ticker, sig_data, sector_idx * 1000 + idx + 100)
            
            if neutral_sector:
                st.markdown("#### 🟡 للمراقبة")
                for idx, (name, ticker, sig_data) in enumerate(neutral_sector):
                    display_stock_card(name, ticker, sig_data, sector_idx * 1000 + idx + 200)

# ====================== تبويب الأخبار ======================
def news_tab():
    """تبويب الأخبار"""
    
    st.markdown("## 📰 أخبار البورصة المصرية")
    
    # أنواع البحث
    search_type = st.radio(
        "اختر نوع البحث:",
        ["📈 أخبار الأسهم", "🌍 أخبار السوق العام", "🏆 السلع والبورصات العالمية", "🔍 بحث مخصص"],
        horizontal=True
    )
    
    st.divider()
    
    if search_type == "📈 أخبار الأسهم":
        stock_for_news = st.selectbox("اختر السهم", list(EGYPTIAN_STOCKS.keys()), key="news_stock")
        if st.button("🔍 بحث", key="search_news_btn"):
            ticker = EGYPTIAN_STOCKS.get(stock_for_news)
            with st.spinner("جاري البحث..."):
                news = search_stock_news(stock_for_news, ticker)
                if news:
                    for idx, item in enumerate(news):
                        with st.expander(f"📰 {item['title']}"):
                            st.write(item['snippet'])
                            st.markdown(f"[اقرأ المزيد]({item['link']})")
                else:
                    st.warning("لا توجد أخبار")
    
    elif search_type == "🌍 أخبار السوق العام":
        if st.button("🔄 تحديث الأخبار", key="refresh_news"):
            with st.spinner("جاري جلب الأخبار..."):
                news = search_market_news()
                if news:
                    for idx, item in enumerate(news):
                        with st.expander(f"📰 {item['title']}"):
                            st.write(item['snippet'])
                            st.markdown(f"[اقرأ المزيد]({item['link']})")
                else:
                    st.warning("لا توجد أخبار")
    
    elif search_type == "🏆 السلع والبورصات العالمية":
        commodity = st.selectbox("اختر السلعة", ["الذهب", "النفط", "الفضة", "الدولار", "اليورو"])
        if st.button("🔍 بحث", key="search_commodity_btn"):
            with st.spinner("جاري البحث..."):
                news = search_commodity_news(commodity)
                if news:
                    for idx, item in enumerate(news):
                        with st.expander(f"🏆 {item['title']}"):
                            st.write(item['snippet'])
                            st.markdown(f"[اقرأ المزيد]({item['link']})")
                else:
                    st.warning("لا توجد أخبار")
    
    else:
        custom_query = st.text_input("اكتب ما تريد البحث عنه", key="custom_query")
        if custom_query and st.button("🔍 بحث", key="custom_search_btn"):
            with st.spinner("جاري البحث..."):
                results = smart_search(custom_query)
                if results:
                    for idx, item in enumerate(results):
                        with st.expander(f"📰 {item['title']}"):
                            st.write(item['snippet'])
                            st.markdown(f"[اقرأ المزيد]({item['link']})")
                else:
                    st.warning("لا توجد نتائج")

# ====================== عرض الشريط العلوي ======================
def show_stats_bar():
    """عرض إحصائيات البورصة"""
    stats = get_market_statistics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📈 إجمالي الأسهم", stats['total_stocks'])
    col2.metric("🏢 عدد القطاعات", stats['sectors'])
    col3.metric("💰 العملة", stats['currency'])
    col4.metric("⏰ وقت التداول", stats['trading_hours'])
    col5.metric("🤖 AI", "متصل" if init_gemini() else "غير متصل")

# ====================== الدالة الرئيسية ======================
def main():
    """التطبيق الرئيسي"""
    
    # رأس الصفحة
    st.markdown("""
    <div class="main-header">
        <h1>🇪🇬 منصة تحليل البورصة المصرية - النسخة المتكاملة</h1>
        <p>تحليل فني متقدم | إشارات ذكية | أخبار فورية | ذكاء اصطناعي</p>
    </div>
    """, unsafe_allow_html=True)
    
    # شريط الإحصائيات
    show_stats_bar()
    st.markdown("---")
    
    # عرض التحليل الفني إذا تم اختيار سهم
    if st.session_state.selected_ticker is not None:
        display_technical_analysis()
    else:
        # تبويبات التصفح
        tab1, tab2, tab3 = st.tabs(["📈 تحليل الأسهم", "🏢 القطاعات", "📰 الأخبار"])
        
        with tab1:
            stock_analysis_tab()
        
        with tab2:
            sectors_tab()
        
        with tab3:
            news_tab()
    
    # تذييل الصفحة
    st.markdown("---")
    st.caption("""
    <div style="text-align: center;">
        🇪🇬 **البورصة المصرية (EGX)** | البيانات من Yahoo Finance | الإشارات مبنية على مؤشر RSI | للأغراض التعليمية
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
