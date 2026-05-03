# app.py - النسخة مع أزرار متطورة (يتم استبدال فقط في عرض الأزرار)
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

# ====================== CSS للتنسيق ======================
st.markdown("""
<style>
    /* تنسيق البطاقات */
    .stock-card-buy {
        background: linear-gradient(135deg, #1a3d1a, #0d2b0d);
        border: 2px solid #00ff00;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stock-card-buy:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,255,0,0.2);
    }
    .stock-card-sell {
        background: linear-gradient(135deg, #4a1a1a, #2d0b0b);
        border: 2px solid #ff4444;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stock-card-sell:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(255,0,0,0.2);
    }
    .stock-card-neutral {
        background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
        border: 2px solid #ffd700;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stock-card-neutral:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(255,215,0,0.2);
    }
    .stock-price {
        font-size: 24px;
        font-weight: bold;
        margin: 5px 0;
    }
    .stock-change-up {
        color: #00ff00;
        font-size: 16px;
        font-weight: bold;
    }
    .stock-change-down {
        color: #ff4444;
        font-size: 16px;
        font-weight: bold;
    }
    .stock-rsi {
        font-size: 14px;
        margin: 5px 0;
    }
    .signal-buy {
        background-color: #00ff00;
        color: #000;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .signal-sell {
        background-color: #ff4444;
        color: #fff;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .signal-neutral {
        background-color: #ffd700;
        color: #000;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .stock-name {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .recommendation {
        font-size: 13px;
        margin-top: 10px;
        padding: 5px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ====================== تهيئة حالة الجلسة ======================
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = None
if 'refresh_market_news' not in st.session_state:
    st.session_state.refresh_market_news = True
if 'search_stock_news' not in st.session_state:
    st.session_state.search_stock_news = None

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
        
        # تحديد الإشارة
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
        col1.metric("💰 السعر الحالي", f"{curr_price:.2f} ج.م", f"{change_pct:+.2f}%")
        col2.metric("📊 مؤشر RSI", f"{rsi:.1f}")
        col3.metric("📈 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
        col4.metric("📦 حجم التداول", f"{hist['Volume'].iloc[-1]:,.0f}")
        
        show_rsi_alert(rsi)
        
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
        analyze_clicked = st.button("🤖 تحليل ذكي بالذكاء الاصطناعي", type="primary", use_container_width=True)
        
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

# ====================== عرض البطاقة المتطورة للسهم ======================
def display_stock_card(name: str, ticker: str, signal_data: tuple, idx: int):
    """عرض بطاقة سهم متطورة مع إشارة الشراء/البيع"""
    
    signal, rsi, change_pct, price = signal_data
    
    if signal == "buy":
        card_class = "stock-card-buy"
        signal_text = "🟢 فرصة شراء"
        signal_class = "signal-buy"
        recommendation = "✅ يوصى بالشراء - السهم في منطقة ذروة بيع"
        arrow = "📈"
    elif signal == "sell":
        card_class = "stock-card-sell"
        signal_text = "🔴 فرصة بيع"
        signal_class = "signal-sell"
        recommendation = "⚠️ يوصى بالبيع - السهم في منطقة ذروة شراء"
        arrow = "📉"
    else:
        card_class = "stock-card-neutral"
        signal_text = "🟡 مراقبة"
        signal_class = "signal-neutral"
        recommendation = "⏸ يوصى بالانتظار - السهم في منطقة حيادية"
        arrow = "➡️"
    
    change_class = "stock-change-up" if change_pct >= 0 else "stock-change-down"
    change_symbol = "▲" if change_pct >= 0 else "▼"
    
    stock_html = f"""
    <div class="{card_class}" onclick="alert('تم اختيار {name}')">
        <div class="stock-name">{arrow} {name[:40]}</div>
        <div class="stock-price">{price:.2f} ج.م</div>
        <div class="{change_class}">{change_symbol} {abs(change_pct):.2f}%</div>
        <div class="stock-rsi">📊 RSI: {rsi:.1f}</div>
        <div style="margin: 10px 0;">
            <span class="{signal_class}">{signal_text}</span>
        </div>
        <div class="recommendation" style="background: rgba(255,255,255,0.1);">
            {recommendation}
        </div>
    </div>
    """
    
    # استخدام Streamlit button بدلاً من HTML onclick
    container = st.container()
    with container:
        st.markdown(stock_html, unsafe_allow_html=True)
        if st.button(f"🔍 تحليل {name[:20]}", key=f"card_btn_{ticker}_{idx}", use_container_width=True):
            select_stock(ticker, name)

# ====================== تبويب تحليل السهم ======================
def stock_analysis_tab():
    """تبويب تحليل السهم مع أزرار متطورة"""
    
    # شريط البحث
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
            
            # تقسيم النتائج حسب الإشارات
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
            
            # عرض أسهم البيع أولاً (لأنها مثيرة للاهتمام)
            if sell_stocks:
                st.markdown("### 🔴 أسهم يوصى ببيعها (ذروة شراء)")
                for idx, (name, ticker, sig_data) in enumerate(sell_stocks):
                    display_stock_card(name, ticker, sig_data, idx)
            
            # عرض أسهم الشراء
            if buy_stocks:
                st.markdown("### 🟢 أسهم يوصى بشرائها (ذروة بيع)")
                for idx, (name, ticker, sig_data) in enumerate(buy_stocks):
                    display_stock_card(name, ticker, sig_data, idx)
            
            # عرض الأسهم الحيادية
            if neutral_stocks:
                st.markdown("### 🟡 أسهم للمراقبة (منطقة حيادية)")
                for idx, (name, ticker, sig_data) in enumerate(neutral_stocks):
                    display_stock_card(name, ticker, sig_data, idx)
    
    st.divider()
    
    # تصفح الأسهم
    st.markdown("### 📋 جميع أسهم البورصة المصرية")
    
    all_stocks = get_all_egyptian_stocks()
    
    # فلتر سريع
    filter_text = st.text_input("🔎 فلتر سريع", placeholder="اكتب جزء من اسم السهم...", key="filter_input")
    
    filtered_stocks = all_stocks
    if filter_text:
        filtered_stocks = {k: v for k, v in all_stocks.items() if filter_text.lower() in k.lower() or filter_text.upper() in v}
    
    st.caption(f"📊 عرض {len(filtered_stocks)} من {len(all_stocks)} سهماً")
    
    # جلب الإشارات لجميع الأسهم المعروضة
    st.markdown("### 🏆 أسهم البورصة المصرية مرتبة حسب الإشارات")
    
    # تجميع الأسهم حسب الإشارة
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
    
    # عرض أسهم البيع
    if sell_list:
        st.markdown("## 🔴 أسهم يوصى ببيعها")
        st.markdown("> *السهم في منطقة ذروة شراء - احتمال تصحيح*")
        
        cols = st.columns(2)
        for idx, (name, ticker, sig_data) in enumerate(sell_list):
            with cols[idx % 2]:
                display_stock_card(name, ticker, sig_data, idx)
    
    # عرض أسهم الشراء
    if buy_list:
        st.markdown("## 🟢 أسهم يوصى بشرائها")
        st.markdown("> *السهم في منطقة ذروة بيع - فرصة شراء*")
        
        cols = st.columns(2)
        for idx, (name, ticker, sig_data) in enumerate(buy_list):
            with cols[idx % 2]:
                display_stock_card(name, ticker, sig_data, idx)
    
    # عرض الأسهم الحيادية
    if neutral_list:
        st.markdown("## 🟡 أسهم للمراقبة")
        st.markdown("> *السهم في منطقة حيادية - يحتاج لمتابعة*")
        
        cols = st.columns(2)
        for idx, (name, ticker, sig_data) in enumerate(neutral_list):
            with cols[idx % 2]:
                display_stock_card(name, ticker, sig_data, idx)

# ====================== تبويب القطاعات ======================
def sectors_tab():
    """تبويب القطاعات"""
    
    st.markdown("## 🏢 أسهم البورصة المصرية حسب القطاع")
    
    sectors = get_all_sectors()
    
    for sector_idx, sector in enumerate(sectors):
        sector_stocks = get_stocks_by_sector(sector)
        
        with st.expander(f"📂 {sector} ({len(sector_stocks)} سهم)", expanded=False):
            # تحليل أسهم القطاع
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
                cols = st.columns(2)
                for idx, (name, ticker, sig_data) in enumerate(sell_sector):
                    with cols[idx % 2]:
                        display_stock_card(name, ticker, sig_data, idx)
            
            if buy_sector:
                st.markdown("#### 🟢 يوصى بشرائها")
                cols = st.columns(2)
                for idx, (name, ticker, sig_data) in enumerate(buy_sector):
                    with cols[idx % 2]:
                        display_stock_card(name, ticker, sig_data, idx)
            
            if neutral_sector:
                st.markdown("#### 🟡 للمراقبة")
                cols = st.columns(2)
                for idx, (name, ticker, sig_data) in enumerate(neutral_sector):
                    with cols[idx % 2]:
                        display_stock_card(name, ticker, sig_data, idx)

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
                        <p style="color: #aaa;">{news['snippet'][:200]}...</p>
                        <small>📰 {news['display_link']}</small>
                        <br/>
                        <a href="{news['link']}" target="_blank">🔗 اقرأ المزيد</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("لا توجد أخبار حالياً")

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
    
    st.title("🇪🇬 بوت تحليل البورصة المصرية - المتطور")
    st.markdown("**تحليل ذكي | إشارات شراء/بيع | تحديث فوري**")
    st.markdown("---")
    
    show_stats_bar()
    st.markdown("---")
    
    if st.session_state.selected_ticker is not None:
        display_technical_analysis()
    else:
        tab1, tab2, tab3 = st.tabs(["📈 تحليل الأسهم", "🏢 القطاعات", "📰 الأخبار"])
        
        with tab1:
            stock_analysis_tab()
        
        with tab2:
            sectors_tab()
        
        with tab3:
            news_tab()
    
    st.markdown("---")
    st.caption("🇪🇬 **البورصة المصرية (EGX)** | الإشارات مبنية على مؤشر RSI | للأغراض التعليمية")

if __name__ == "__main__":
    main()
