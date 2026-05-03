# app.py - النسخة النهائية (بدون أخطاء تكرار المفاتيح)
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
if 'refresh_market_news' not in st.session_state:
    st.session_state.refresh_market_news = True
if 'search_stock_news' not in st.session_state:
    st.session_state.search_stock_news = None
if 'unique_counter' not in st.session_state:
    st.session_state.unique_counter = 0

def get_unique_key(prefix: str) -> str:
    """توليد مفتاح فريد لكل عنصر"""
    st.session_state.unique_counter += 1
    return f"{prefix}_{st.session_state.unique_counter}_{datetime.now().timestamp()}"

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

# ====================== إحصائيات البورصة في أعلى الصفحة ======================
def show_stats_bar():
    """عرض إحصائيات البورصة في شريط أفقي"""
    stats = get_market_statistics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📈 إجمالي الأسهم", stats['total_stocks'])
    col2.metric("🏢 عدد القطاعات", stats['sectors'])
    col3.metric("💰 العملة", stats['currency'])
    col4.metric("⏰ وقت التداول", stats['trading_hours'])
    col5.metric("🤖 Gemini AI", "متصل" if init_gemini() else "غير متصل")
    
    if not init_gemini():
        st.warning("⚠️ أضف GEMINI_API_KEY في ملف .streamlit/secrets.toml لتفعيل التحليل الذكي")

# ====================== تبويب تحليل السهم ======================
def stock_analysis_tab():
    """تبويب تحليل السهم"""
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input(
            "🔍 ابحث عن سهم",
            placeholder="اكتب اسم السهم أو رمزه...",
            key="main_search_input"
        )
    
    if search_term:
        results = search_stock(search_term)
        if results:
            for idx, (stock_name, stock_data) in enumerate(results.items()):
                unique_key = get_unique_key(f"search_result_{stock_data['ticker']}_{idx}")
                if st.button(f"📊 {stock_name} ({stock_data['ticker']})", key=unique_key):
                    st.session_state.selected_ticker = stock_data['ticker']
                    st.session_state.selected_name = stock_name
                    st.rerun()
    
    st.divider()
    
    # تصفح الأسهم
    col1, col2 = st.columns([1, 2])
    with col1:
        market_filter = st.selectbox(
            "فلتر حسب القطاع",
            ["جميع القطاعات"] + get_all_sectors(),
            key="sector_filter_select"
        )
    
    # عرض الأسهم
    all_stocks = get_all_egyptian_stocks()
    
    if market_filter != "جميع القطاعات":
        sector_stocks = get_stocks_by_sector(market_filter)
        stock_items = list(sector_stocks.items())
    else:
        stock_items = list(all_stocks.items())
    
    st.caption(f"📊 عرض {len(stock_items)} سهماً")
    
    # عرض في 3 أعمدة
    cols = st.columns(3)
    for idx, (name, ticker) in enumerate(stock_items):
        unique_key = get_unique_key(f"stock_btn_{ticker}_{idx}")
        with cols[idx % 3]:
            if st.button(f"📈 {name}", key=unique_key, use_container_width=True):
                st.session_state.selected_ticker = ticker
                st.session_state.selected_name = name
                st.rerun()
            st.caption(f"رمز: `{ticker}`")
    
    # عرض تحليل السهم المختار
    if st.session_state.selected_ticker and st.session_state.selected_name:
        st.divider()
        st.header(f"📈 التحليل الفني: {st.session_state.selected_name}")
        st.caption(f"الرمز: `{st.session_state.selected_ticker}` | السوق: البورصة المصرية (EGX)")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            period = st.selectbox(
                "📅 الفترة الزمنية",
                ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                index=3,
                key="period_select"
            )
        with col2:
            auto_analyze = st.checkbox("🤖 تحليل تلقائي بالذكاء الاصطناعي", value=False, key="auto_analyze_check")
        
        with st.spinner("جاري تحميل البيانات..."):
            hist, info = get_stock_data(st.session_state.selected_ticker, period)
        
        if hist is not None and not hist.empty:
            curr_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
            change_pct = ((curr_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
            rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 السعر", f"{curr_price:.2f} ج.م", f"{change_pct:+.2f}%")
            col2.metric("📊 RSI", f"{rsi:.1f}")
            col3.metric("📈 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
            col4.metric("📦 الحجم", f"{hist['Volume'].iloc[-1]:,.0f}")
            
            show_rsi_alert(rsi)
            
            # رسم بياني
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر", line=dict(color='cyan', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", line=dict(dash='dash', color='orange')), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI", line=dict(color='magenta')), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.update_layout(height=500, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            if auto_analyze or st.button("🤖 تحليل ذكي", type="primary", key="analyze_btn"):
                model = init_gemini()
                if model:
                    with st.spinner("جاري التحليل..."):
                        prompt = f"حلل السهم {st.session_state.selected_name} السعر: {curr_price:.2f} RSI: {rsi:.1f}"
                        response = model.generate_content(prompt)
                        st.success(response.text)
                else:
                    st.warning("⚠️ أضف مفتاح Gemini API")
            
            clear_key = get_unique_key("clear_selection")
            if st.button("🗑️ مسح الاختيار", key=clear_key):
                st.session_state.selected_ticker = None
                st.session_state.selected_name = None
                st.rerun()
        else:
            st.error("❌ تعذر جلب البيانات")

# ====================== تبويب القطاعات ======================
def sectors_tab():
    """تبويب عرض الأسهم حسب القطاعات"""
    
    st.markdown("## 🏢 أسهم البورصة المصرية حسب القطاع")
    
    sectors = get_all_sectors()
    
    for sector_idx, sector in enumerate(sectors):
        sector_stocks = get_stocks_by_sector(sector)
        with st.expander(f"📂 {sector} ({len(sector_stocks)} سهم)", expanded=False):
            cols = st.columns(4)
            for stock_idx, (name, ticker) in enumerate(sector_stocks.items()):
                unique_key = get_unique_key(f"sector_{sector}_{ticker}_{sector_idx}_{stock_idx}")
                with cols[stock_idx % 4]:
                    if st.button(f"{name}", key=unique_key, use_container_width=True):
                        st.session_state.selected_ticker = ticker
                        st.session_state.selected_name = name
                        st.rerun()
                    st.caption(f"`{ticker}`")

# ====================== تبويب الأخبار والبحث ======================
def news_and_search_tab():
    """تبويب الأخبار والبحث المتقدم"""
    
    st.markdown("## 📰 أخبار وتحليلات البورصة المصرية")
    
    # أنواع البحث
    search_type = st.radio(
        "اختر نوع البحث:",
        ["📈 أخبار الأسهم", "🌍 أخبار السوق العام", "🏆 السلع والبورصات العالمية", "🔍 بحث مخصص"],
        horizontal=True,
        key="search_type_radio"
    )
    
    st.divider()
    
    if search_type == "📈 أخبار الأسهم":
        st.subheader("ابحث عن أخبار سهم معين")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            stock_for_news = st.selectbox(
                "اختر السهم",
                list(EGYPTIAN_STOCKS.keys()),
                key="news_stock_select"
            )
        with col2:
            st.write("")
            st.write("")
            search_key = get_unique_key("search_stock_news")
            if st.button("🔍 بحث عن الأخبار", key=search_key):
                st.session_state.search_stock_news = stock_for_news
        
        if st.session_state.get('search_stock_news'):
            stock_ticker = EGYPTIAN_STOCKS.get(st.session_state.search_stock_news)
            
            with st.spinner(f"جاري البحث عن أخبار {st.session_state.search_stock_news}..."):
                news_results = search_stock_news(st.session_state.search_stock_news, stock_ticker)
                
                if news_results:
                    st.success(f"✅ تم العثور على {len(news_results)} خبر")
                    
                    for idx, news in enumerate(news_results, 1):
                        with st.expander(f"📰 {idx}. {news['title'][:100]}", expanded=False):
                            st.markdown(f"**المصدر:** {news['display_link']}")
                            st.markdown(f"**الملخص:** {news['snippet']}")
                            st.markdown(f"**الرابط:** [اقرأ المزيد]({news['link']})")
                            
                            analyze_key = get_unique_key(f"analyze_news_{idx}")
                            if st.button(f"🤖 تحليل هذا الخبر", key=analyze_key):
                                analysis = analyze_news_with_gemini(news['snippet'], st.session_state.search_stock_news)
                                st.info(analysis)
                else:
                    st.warning("لم يتم العثور على أخبار لهذا السهم")
    
    elif search_type == "🌍 أخبار السوق العام":
        st.subheader("آخر أخبار البورصة المصرية والاقتصاد")
        
        refresh_key = get_unique_key("refresh_market_news")
        if st.button("🔄 تحديث الأخبار", key=refresh_key):
            st.session_state.refresh_market_news = True
        
        if st.session_state.get('refresh_market_news', True):
            with st.spinner("جاري جلب آخر أخبار السوق..."):
                market_news = search_market_news()
                
                if market_news:
                    st.markdown("### 🔴 أهم الأخبار العاجلة")
                    
                    cols = st.columns(2)
                    for idx, news in enumerate(market_news[:4]):
                        with cols[idx % 2]:
                            st.markdown(f"""
                            <div style='border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin: 5px;'>
                                <small>{news['display_link']}</small>
                                <h4>{news['title'][:80]}...</h4>
                                <p>{news['snippet'][:150]}...</p>
                                <a href="{news['link']}" target="_blank">📖 اقرأ المزيد</a>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("### 📰 باقي الأخبار")
                    for idx, news in enumerate(market_news[4:], 5):
                        with st.expander(f"{idx}. {news['title']}"):
                            st.markdown(f"**المصدر:** {news['display_link']}")
                            st.markdown(f"**الملخص:** {news['snippet']}")
                            st.markdown(f"**الرابط:** [اقرأ المزيد]({news['link']})")
                            
                            analyze_key = get_unique_key(f"analyze_market_{idx}")
                            if st.button(f"🤖 تحليل", key=analyze_key):
                                analysis = analyze_news_with_gemini(news['snippet'])
                                st.info(analysis)
                else:
                    st.warning("لم يتم العثور على أخبار حالياً")
    
    elif search_type == "🏆 السلع والبورصات العالمية":
        st.subheader("أخبار السلع العالمية (ذهب، نفط، عملات)")
        
        commodities_list = ["الذهب", "النفط", "الفضة", "الدولار", "اليورو", "الغاز الطبيعي"]
        selected_commodity = st.selectbox("اختر السلعة أو العملة", commodities_list, key="commodity_select")
        
        search_key = get_unique_key("search_commodity")
        if st.button(f"🔍 بحث عن أخبار {selected_commodity}", key=search_key):
            with st.spinner(f"جاري البحث عن أخبار {selected_commodity}..."):
                commodity_news = search_commodity_news(selected_commodity)
                
                if commodity_news:
                    st.success(f"✅ تم العثور على {len(commodity_news)} خبر")
                    
                    for idx, news in enumerate(commodity_news, 1):
                        with st.expander(f"🏆 {idx}. {news['title']}"):
                            st.markdown(f"**المصدر:** {news['display_link']}")
                            st.markdown(f"**الملخص:** {news['snippet']}")
                            st.markdown(f"**الرابط:** [اقرأ المزيد]({news['link']})")
                else:
                    st.warning(f"لم يتم العثور على أخبار لـ {selected_commodity}")
    
    else:  # بحث مخصص
        st.subheader("بحث مخصص في أخبار الاقتصاد")
        
        custom_query = st.text_input(
            "أدخل ما تريد البحث عنه",
            placeholder="مثال: قرارات الفائدة البنك المركزي, أسعار الذهب اليوم, أرباح شركات البورصة...",
            key="custom_query_input"
        )
        
        search_key = get_unique_key("custom_search")
        if custom_query and st.button("🔍 بحث", type="primary", key=search_key):
            with st.spinner("جاري البحث..."):
                results = smart_search(custom_query, "اقتصاد")
                
                if results:
                    st.success(f"✅ تم العثور على {len(results)} نتيجة")
                    
                    for idx, result in enumerate(results, 1):
                        with st.expander(f"{idx}. {result['title']}"):
                            st.markdown(f"**الرابط:** [{result['link']}]({result['link']})")
                            st.markdown(f"**الملخص:** {result['snippet']}")
                            
                            analyze_key = get_unique_key(f"analyze_custom_{idx}")
                            if st.button(f"🤖 تحليل المحتوى", key=analyze_key):
                                analysis = analyze_news_with_gemini(result['snippet'])
                                st.info(analysis)
                else:
                    st.warning("لا توجد نتائج. حاول بكلمات مختلفة")

# ====================== الدالة الرئيسية ======================
def main():
    """التطبيق الرئيسي"""
    
    # عنوان رئيسي
    st.title("🇪🇬 بوت تحليل البورصة المصرية - النسخة الشاملة")
    st.markdown("**جميع أسهم البورصة المصرية (EGX) | تحليل فني + ذكاء اصطناعي + أخبار فورية**")
    st.markdown("---")
    
    # شريط الإحصائيات
    show_stats_bar()
    st.markdown("---")
    
    # التبويبات الرئيسية
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 تحليل الأسهم",
        "🏢 القطاعات", 
        "📰 الأخبار والتحليلات",
        "ℹ️ عن التطبيق"
    ])
    
    with tab1:
        stock_analysis_tab()
    
    with tab2:
        sectors_tab()
    
    with tab3:
        news_and_search_tab()
    
    with tab4:
        st.markdown("""
        ### ℹ️ عن التطبيق
        
        **بوت تحليل البورصة المصرية** هو تطبيق شامل لتحليل الأسهم المصرية
        
        #### المميزات:
        - 📊 **تحليل فني متقدم** (RSI, SMA, EMA)
        - 🤖 **ذكاء اصطناعي** من Google Gemini
        - 📰 **أخبار فورية** من محركات البحث
        - 🇪🇬 **جميع أسهم البورصة المصرية**
        - 🏢 **تصنيف حسب القطاعات**
        - 💱 **أسعار العملات والسلع**
        
        #### مصادر البيانات:
        - 📈 الأسعار: Yahoo Finance
        - 🧠 التحليل: Google Gemini AI
        - 📰 الأخبار: Google Search
        
        #### للاستخدام التعليمي فقط ⚠️
        """)
    
    # تذييل
    st.markdown("---")
    st.caption("🇪🇬 **البورصة المصرية (EGX)** | البيانات من Yahoo Finance | للأغراض التعليمية فقط")

if __name__ == "__main__":
    main()
