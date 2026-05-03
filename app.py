# أضف هذا الاستيراد في بداية app.py
from search_utils import (
    search_google, 
    search_stock_news, 
    search_market_news,
    search_commodity_news,
    smart_search,
    analyze_news_with_gemini
)

# ====================== تبويب الأخبار والبحث الجديد ======================
def news_and_search_tab():
    """تبويب الأخبار والبحث المتقدم"""
    
    st.markdown("## 📰 أخبار وتحليلات البورصة المصرية")
    
    # أنواع البحث
    search_type = st.radio(
        "اختر نوع البحث:",
        ["📈 أخبار الأسهم", "🌍 أخبار السوق العام", "🏆 السلع والبورصات العالمية", "🔍 بحث مخصص"],
        horizontal=True
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
            if st.button("🔍 بحث عن الأخبار", key="search_stock_news_btn"):
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
                            
                            # زر لتحليل الخبر
                            if st.button(f"🤖 تحليل هذا الخبر", key=f"analyze_news_{idx}"):
                                analysis = analyze_news_with_gemini(news['snippet'], st.session_state.search_stock_news)
                                st.info(analysis)
                else:
                    st.warning("لم يتم العثور على أخبار لهذا السهم")
    
    elif search_type == "🌍 أخبار السوق العام":
        st.subheader("آخر أخبار البورصة المصرية والاقتصاد")
        
        if st.button("🔄 تحديث الأخبار", key="refresh_market_news"):
            st.session_state.refresh_market_news = True
        
        if st.session_state.get('refresh_market_news', True):
            with st.spinner("جاري جلب آخر أخبار السوق..."):
                market_news = search_market_news()
                
                if market_news:
                    # عرض أخبار مهمة أولاً
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
                            
                            if st.button(f"🤖 تحليل", key=f"analyze_market_{idx}"):
                                analysis = analyze_news_with_gemini(news['snippet'])
                                st.info(analysis)
                else:
                    st.warning("لم يتم العثور على أخبار حالياً")
    
    elif search_type == "🏆 السلع والبورصات العالمية":
        st.subheader("أخبار السلع العالمية (ذهب، نفط، عملات)")
        
        commodities_list = ["الذهب", "النفط", "الفضة", "الدولار", "اليورو", "الغاز الطبيعي"]
        selected_commodity = st.selectbox("اختر السلعة أو العملة", commodities_list)
        
        if st.button(f"🔍 بحث عن أخبار {selected_commodity}", key="search_commodity"):
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
            placeholder="مثال: قرارات الفائدة البنك المركزي, أسعار الذهب اليوم, أرباح شركات البورصة..."
        )
        
        if custom_query and st.button("🔍 بحث", type="primary"):
            with st.spinner("جاري البحث..."):
                results = smart_search(custom_query, "اقتصاد")
                
                if results:
                    st.success(f"✅ تم العثور على {len(results)} نتيجة")
                    
                    for idx, result in enumerate(results, 1):
                        with st.expander(f"{idx}. {result['title']}"):
                            st.markdown(f"**الرابط:** [{result['link']}]({result['link']})")
                            st.markdown(f"**الملخص:** {result['snippet']}")
                            
                            if st.button(f"🤖 تحليل المحتوى", key=f"analyze_custom_{idx}"):
                                analysis = analyze_news_with_gemini(result['snippet'])
                                st.info(analysis)
                else:
                    st.warning("لا توجد نتائج. حاول بكلمات مختلفة")

# ====================== تحديث الدالة الرئيسية ======================
def main():
    # ... الكود الحالي ...
    
    # تعديل التبويبات لإضافة تبويب الأخبار
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 بحث عن سهم", 
        "📋 تصفح جميع الأسهم", 
        "🏢 حسب القطاع",
        "📰 أخبار وتحليلات"  # التبويب الجديد
    ])
    
    # ... باقي الكود كما هو ...
    
    with tab4:
        news_and_search_tab()
# app.py - تطبيق تحليل جميع أسهم البورصة المصرية (النسخة المصححة)
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

# ====================== تهيئة حالة الجلسة ======================
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = None

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

# ====================== العنوان الرئيسي ======================
st.title("🇪🇬 بوت تحليل البورصة المصرية - شامل جميع الأسهم")
st.markdown("**جميع أسهم البورصة المصرية (EGX) | تحليل فني + ذكاء اصطناعي**")
st.markdown("---")

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
        st.warning("⚠️ أضف GEMINI_API_KEY في ملف .streamlit/secrets.toml لتفعيل التحليل الذكي")

# ====================== البحث والتصفح ======================
tab1, tab2, tab3 = st.tabs(["🔍 بحث عن سهم", "📋 تصفح جميع الأسهم", "🏢 حسب القطاع"])

# تبويب البحث
with tab1:
    st.markdown("### 🔍 ابحث عن أي سهم في البورصة المصرية")
    
    search_term = st.text_input(
        "اكتب اسم السهم أو الرمز",
        placeholder="مثال: CIB, البنك التجاري الدولي, COMI.CA",
        help="ابحث بالاسم العربي أو الرمز",
        key="search_input"
    )
    
    if search_term:
        results = search_stock(search_term)
        
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            for stock_name, stock_data in results.items():
                with st.expander(f"📈 {stock_name} - {stock_data['ticker']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**الرمز:** `{stock_data['ticker']}`")
                    with col2:
                        if st.button(f"تحليل", key=f"search_btn_{stock_data['ticker']}"):
                            st.session_state.selected_ticker = stock_data['ticker']
                            st.session_state.selected_name = stock_name
                            st.rerun()
        else:
            st.warning("❌ لم يتم العثور على نتائج. جرب كلمة بحث مختلفة")

# تبويب تصفح جميع الأسهم
with tab2:
    st.markdown("### 📋 جميع أسهم البورصة المصرية")
    
    all_stocks = get_all_egyptian_stocks()
    
    # فلتر سريع
    filter_text = st.text_input(
        "🔎 فلتر سريع", 
        placeholder="اكتب جزء من اسم السهم...",
        key="filter_input"
    )
    
    filtered_stocks = all_stocks
    if filter_text:
        filtered_stocks = {
            k: v for k, v in all_stocks.items() 
            if filter_text.lower() in k.lower() or filter_text.upper() in v
        }
    
    st.caption(f"📊 عرض {len(filtered_stocks)} من {len(all_stocks)} سهماً")
    
    # عرض الأسهم في عمودين
    stock_items = list(filtered_stocks.items())
    
    if stock_items:
        col1, col2 = st.columns(2)
        
        for idx, (name, ticker) in enumerate(stock_items):
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"📊 {name}", key=f"browse_btn_{ticker}_{idx}", use_container_width=True):
                    st.session_state.selected_ticker = ticker
                    st.session_state.selected_name = name
                    st.rerun()
                st.caption(f"رمز: `{ticker}`")
                st.markdown("---")
    else:
        st.info("لا توجد أسهم تطابق معايير البحث")

# تبويب حسب القطاع
with tab3:
    st.markdown("### 🏢 تصفح حسب القطاع الاقتصادي")
    
    sectors = get_all_sectors()
    selected_sector = st.selectbox("اختر القطاع", sectors, key="sector_select")
    
    if selected_sector:
        sector_stocks = get_stocks_by_sector(selected_sector)
        st.subheader(f"🏭 أسهم قطاع {selected_sector} ({len(sector_stocks)} سهم)")
        
        if sector_stocks:
            col1, col2 = st.columns(2)
            for idx, (name, ticker) in enumerate(sector_stocks.items()):
                with col1 if idx % 2 == 0 else col2:
                    if st.button(f"📈 {name}", key=f"sector_btn_{ticker}_{idx}", use_container_width=True):
                        st.session_state.selected_ticker = ticker
                        st.session_state.selected_name = name
                        st.rerun()
                    st.caption(f"رمز: `{ticker}`")
                    st.markdown("---")
        else:
            st.info("لا توجد أسهم في هذا القطاع")

# ====================== عرض معلومات السهم المختار ======================
# عرض السهم المختار من أي تبويب
if st.session_state.selected_ticker and st.session_state.selected_name:
    st.markdown("---")
    st.header(f"📈 التحليل الفني: {st.session_state.selected_name}")
    st.caption(f"الرمز: `{st.session_state.selected_ticker}` | السوق: البورصة المصرية (EGX)")
    
    # خيارات التحليل
    col1, col2 = st.columns([2, 1])
    with col1:
        period = st.selectbox(
            "📅 الفترة الزمنية للتحليل",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            key="period_select"
        )
    
    with col2:
        auto_analyze = st.checkbox("🤖 تحليل تلقائي بالذكاء الاصطناعي", value=False, key="auto_analyze")
    
    # جلب البيانات
    with st.spinner("جاري تحميل بيانات السهم..."):
        hist, info = get_stock_data(st.session_state.selected_ticker, period)
    
    if hist is not None and not hist.empty:
        # المقاييس الأساسية
        curr_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
        change_pct = ((curr_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
        volume = hist['Volume'].iloc[-1]
        
        # عرض المقاييس في 4 أعمدة
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 السعر الحالي", f"{curr_price:.2f} ج.م", f"{change_pct:+.2f}%")
        with col2:
            st.metric("📊 مؤشر RSI", f"{rsi:.1f}")
        with col3:
            st.metric("📈 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
        with col4:
            st.metric("📦 حجم التداول", f"{volume:,.0f}")
        
        # تنبيه RSI
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
                    st.write(f"**القيمة السوقية:** {info.get('marketCap', 'غير متوفر'):,}" if info.get('marketCap') else "**القيمة السوقية:** غير متوفر")
                    st.write(f"**أعلى 52 أسبوع:** {info.get('fiftyTwoWeekHigh', 'غير متوفر')}")
                    st.write(f"**أدنى 52 أسبوع:** {info.get('fiftyTwoWeekLow', 'غير متوفر')}")
        
        # الرسم البياني المتقدم
        st.subheader("📊 الرسم البياني الفني")
        
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=("حركة السعر", "مؤشر RSI", "حجم التداول")
        )
        
        # السعر والمتوسطات
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['Close'], 
            name="السعر", 
            line=dict(color='cyan', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['SMA_20'], 
            name="SMA 20", 
            line=dict(dash='dash', color='orange', width=1.5)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['EMA_9'], 
            name="EMA 9", 
            line=dict(dash='dot', color='yellow', width=1.5)
        ), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['RSI'], 
            name="RSI", 
            line=dict(color='magenta', width=2)
        ), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="ذروة شراء", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="ذروة بيع", row=2, col=1)
        
        # حجم التداول
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(hist['Close'], hist['Open'])]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist['Volume'], 
            name="Volume", marker_color=colors, opacity=0.5
        ), row=3, col=1)
        
        # تحديث التنسيق
        fig.update_layout(
            height=700, 
            template="plotly_dark",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        
        fig.update_xaxes(rangeslider_visible=False)
        fig.update_yaxes(title_text="السعر (ج.م)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="الحجم", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # التحليل بالذكاء الاصطناعي
        if auto_analyze or st.button("🤖 تحليل ذكي باستخدام الذكاء الاصطناعي", type="primary", use_container_width=True):
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
                    المتوسط المتحرك 20: {hist['SMA_20'].iloc[-1]:.2f}
                    
                    قدم تحليلاً فنياً مختصراً بالعربية يشمل:
                    1. اتجاه السهم (صاعد/هابط/جانبي)
                    2. تحليل RSI وحالة السهم
                    3. نقاط الدعم والمقاومة المتوقعة
                    4. توصية واضحة للمستثمر
                    
                    الرد بشكل احترافي ومختصر.
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("### 📝 نتيجة التحليل الذكي")
                        st.success(response.text)
                    except Exception as e:
                        st.error(f"خطأ في التحليل: {e}")
            else:
                st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في ملف .streamlit/secrets.toml لتفعيل التحليل الذكي")
        
        # زر لمسح الاختيار
        if st.button("🗑️ مسح الاختيار والعودة للقائمة", use_container_width=True):
            st.session_state.selected_ticker = None
            st.session_state.selected_name = None
            st.rerun()
    
    else:
        st.error("❌ تعذر جلب بيانات السهم. تأكد من الرمز وحاول مرة أخرى")
        if st.button("🔄 محاولة مرة أخرى"):
            st.rerun()

# ====================== تذييل الصفحة ======================
st.markdown("---")
st.caption("🇪🇬 **البورصة المصرية (EGX)** | البيانات من Yahoo Finance | للاستخدام التعليمي فقط")
st.caption("💡 **نصيحة:** استخدم مؤشر RSI مع المتوسطات المتحركة للحصول على إشارات أقوى")
