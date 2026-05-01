import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import google.generativeai as genai
import warnings
import time
import requests

warnings.filterwarnings('ignore')

# ====================== إعدادات الصفحة والتصميم ======================
st.set_page_config(
    page_title="منصة البورصجي الشاملة",
    page_icon="🕶️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; 
    }
    
    .main { 
        background-color: #0e1117; 
    }
    
    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 12px; 
        justify-content: center; 
        background: #1a1c24;
        padding: 8px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        white-space: pre-wrap; 
        background-color: transparent;
        border-radius: 12px; 
        color: white; 
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #00ffcc20;
    }
    
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #00ffcc, #00b4d8) !important; 
        color: #000 !important; 
        font-weight: bold;
    }
    
    /* بطاقات الأخبار */
    .news-card { 
        background: linear-gradient(135deg, #1a1c24, #1e2030);
        padding: 16px; 
        border-radius: 16px; 
        border-right: 4px solid #00ffcc; 
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateX(-5px);
        border-right-color: #ff00ff;
    }
    
    /* بطاقات المؤشرات */
    .index-card {
        background: #1a1c24;
        padding: 16px;
        border-radius: 16px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #2a2a3e;
    }
    
    .index-card:hover {
        transform: translateY(-3px);
        border-color: #00ffcc;
    }
    
    .index-value {
        font-size: 24px;
        font-weight: bold;
        color: #00ffcc;
    }
    
    .index-change-positive {
        color: #00ff88;
        font-size: 14px;
    }
    
    .index-change-negative {
        color: #ff4444;
        font-size: 14px;
    }
    
    /* تذييل */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        margin-top: 30px;
        border-top: 1px solid #2a2a3e;
    }
    
    /* مؤشر التحديث */
    .refresh-indicator {
        text-align: left;
        font-size: 11px;
        color: #666;
        margin-bottom: 10px;
        font-family: monospace;
    }
    
    /* تنسيق الأزرار */
    .stButton > button {
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 25px;
        padding: 8px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0, 255, 204, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ====================== إعداد الذكاء الاصطناعي ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== الدوال المحركة ======================

@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        return stock, df
    except:
        return None, None

@st.cache_data(ttl=300)
def get_index_data(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2] if len(data) > 1 else price
            change = ((price - prev) / prev) * 100
            return price, change
    except:
        pass
    return None, None

def display_news(ticker=None):
    """جلب الأخبار العالمية أو الخاصة بشركة معينة"""
    try:
        if ticker:
            target = yf.Ticker(ticker)
            news = target.news[:5] if hasattr(target, 'news') else []
        else:
            target = yf.Ticker("SPY")
            news = target.news[:5] if hasattr(target, 'news') else []
        
        if not news:
            st.info("📭 لا توجد أخبار حالياً")
            return
        
        for item in news:
            st.markdown(f"""
            <div class="news-card">
                <h4 style='margin:0 0 8px 0; font-size: 14px;'>{item['title'][:100]}</h4>
                <p style='color:#888; font-size:11px; margin:0;'>
                    📰 {item.get('publisher', 'مصدر غير معروف')} | 
                    🕐 {datetime.fromtimestamp(item.get('providerPublishTime', datetime.now().timestamp())).strftime('%Y-%m-%d %H:%M')}
                </p>
                <a href="{item.get('link', '#')}" target="_blank" style="color: #00ffcc; font-size: 12px;">📖 قراءة المزيد →</a>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.write(f"تعذر جلب الأخبار حالياً: {e}")

def calculate_rsi(df, period=14):
    """حساب مؤشر RSI"""
    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def get_rsi_analysis(rsi):
    """تحليل RSI مع توصية"""
    if rsi < 30:
        return "🚀 **منطقة شراء قوية** - السهم في تشبع بيعي", "success", "فرصة شراء ممتازة"
    elif rsi < 40:
        return "📈 **منطقة تراكم** - بداية إشارة شراء", "info", "مراقبة للسهم"
    elif rsi > 70:
        return "⚠️ **منطقة بيع خطرة** - السهم في تشبع شرائي", "error", "ينصح بجني الأرباح"
    elif rsi > 60:
        return "📉 **منطقة تصحيح محتملة**", "warning", "توخي الحذر"
    else:
        return "⚖️ **منطقة محايدة** - السهم في حالة اتزان", "info", "انتظار وضوح الاتجاه"

# ====================== واجهة المستخدم ======================

st.markdown('<div class="refresh-indicator">🕐 تحديث لحظي | ' + datetime.now().strftime("%H:%M:%S") + '</div>', unsafe_allow_html=True)

st.title("🕶️ منصة البورصجي الشاملة")
st.markdown("*العين التي لا تنام في أسواق المال العالمية*")

# التبويبات
tab1, tab2, tab3, tab4 = st.tabs(["🌍 الموجز العالمي", "🇪🇬 البورصة المصرية", "🇺🇸 الأسهم العالمية", "🔍 تحليل الشركات"])

# ====================== التبويب الأول: الموجز العالمي ======================
with tab1:
    st.subheader("📈 أداء المؤشرات الكبرى")
    
    indices = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC", 
        "Dow Jones": "^DJI",
        "EGX 30": "^EGX30",
        "TASI": "^TASI",
        "الذهب": "GC=F",
        "النفط": "CL=F",
        "الدولار/جنيه": "EGP=X"
    }
    
    # تقسيم المؤشرات إلى صفوف
    cols = st.columns(4)
    for i, (name, sym) in enumerate(indices.items()):
        price, change = get_index_data(sym)
        if price:
            with cols[i % 4]:
                st.markdown(f"""
                <div class="index-card">
                    <div style="font-size: 12px; color: #888;">{name}</div>
                    <div class="index-value">{price:,.2f}</div>
                    <div class="index-change-{'positive' if change >= 0 else 'negative'}">
                        {change:+.2f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with cols[i % 4]:
                st.markdown(f"""
                <div class="index-card">
                    <div style="font-size: 12px; color: #888;">{name}</div>
                    <div class="index-value">--</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("📊 رسم بياني للسوق الأمريكي (S&P 500)")
        sp_data, sp_df = get_stock_data("^GSPC", "1mo")
        if sp_df is not None and not sp_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sp_df.index, y=sp_df['Close'],
                mode='lines',
                name='S&P 500',
                line=dict(color='#00ffcc', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 255, 204, 0.1)'
            ))
            fig.update_layout(
                title="أداء S&P 500 - آخر شهر",
                template="plotly_dark",
                height=400,
                xaxis_title="التاريخ",
                yaxis_title="السعر"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📰 أبرز العناوين العالمية")
        display_news()

# ====================== التبويب الثاني: البورصة المصرية ======================
with tab2:
    st.subheader("🇪🇬 شركات السوق المصري (EGX)")
    
    egx_list = {
        "البنك التجاري الدولي": "COMI.CA",
        "طلعت مصطفى": "TMGH.CA",
        "السويدي إليكتريك": "SWDY.CA",
        "تليكوم مصر": "ETEL.CA",
        "فوري": "FWRY.CA",
        "إيخو": "EKHO.CA",
        "أبو قير للأسمدة": "ABUK.CA",
        "موبكو": "MFPC.CA"
    }
    
    selected_egx_name = st.selectbox("اختر شركة مصرية لتحليلها:", list(egx_list.keys()))
    selected_egx = egx_list[selected_egx_name]
    
    s_stock, s_df = get_stock_data(selected_egx, "2mo")
    
    if s_stock and s_df is not None and not s_df.empty:
        current_price = s_df['Close'].iloc[-1]
        prev_price = s_df['Close'].iloc[-2] if len(s_df) > 1 else current_price
        daily_change = ((current_price - prev_price) / prev_price) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 السعر الحالي", f"{current_price:.2f} ج.م", f"{daily_change:+.2f}%")
        col2.metric("📊 أعلى 52 أسبوع", f"{s_df['High'].max():.2f}")
        col3.metric("📉 أدنى 52 أسبوع", f"{s_df['Low'].min():.2f}")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(
                x=s_df.index,
                open=s_df['Open'],
                high=s_df['High'],
                low=s_df['Low'],
                close=s_df['Close'],
                name="الشموع اليابانية"
            )])
            fig.update_layout(
                title=f"تحليل أداء {selected_egx_name} ({selected_egx})",
                template="plotly_dark",
                height=450,
                xaxis_title="التاريخ",
                yaxis_title="السعر"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.write("### 📌 آخر أخبار الشركة")
            display_news(selected_egx)
            
            # تحليل RSI
            rsi = calculate_rsi(s_df)
            rsi_text, rsi_type, recommendation = get_rsi_analysis(rsi)
            
            if rsi_type == "success":
                st.success(f"📊 **مؤشر القوة النسبية (RSI):** {rsi:.1f}\n\n{rsi_text}")
            elif rsi_type == "error":
                st.error(f"📊 **مؤشر القوة النسبية (RSI):** {rsi:.1f}\n\n{rsi_text}")
            else:
                st.info(f"📊 **مؤشر القوة النسبية (RSI):** {rsi:.1f}\n\n{rsi_text}")
            
            st.caption(f"💡 التوصية: {recommendation}")
    else:
        st.error("⚠️ تعذر جلب البيانات. تأكد من اتصالك بالإنترنت")

# ====================== التبويب الثالث: الأسهم العالمية ======================
with tab3:
    st.subheader("🇺🇸 عمالقة التكنولوجيا والسوق العالمي")
    
    global_list = {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "NVIDIA": "NVDA",
        "Meta": "META",
        "Alibaba": "BABA"
    }
    
    selected_global_name = st.selectbox("اختر شركة عالمية:", list(global_list.keys()))
    selected_global = global_list[selected_global_name]
    
    g_stock, g_df = get_stock_data(selected_global, "2mo")
    
    if g_stock and g_df is not None and not g_df.empty:
        current_price = g_df['Close'].iloc[-1]
        prev_price = g_df['Close'].iloc[-2] if len(g_df) > 1 else current_price
        daily_change = ((current_price - prev_price) / prev_price) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 السعر الحالي", f"${current_price:.2f}", f"{daily_change:+.2f}%")
        col2.metric("🏆 أعلى سعر", f"${g_df['High'].max():.2f}")
        col3.metric("📉 أدنى سعر", f"${g_df['Low'].min():.2f}")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=g_df.index, y=g_df['Close'],
                mode='lines',
                name='السعر',
                line=dict(color='#00ffcc', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(0, 255, 204, 0.15)'
            ))
            fig.update_layout(
                title=f"أداء {selected_global_name} ({selected_global})",
                template="plotly_dark",
                height=450,
                xaxis_title="التاريخ",
                yaxis_title="السعر ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.write("### 📌 أخبار حصرية")
            display_news(selected_global)
            
            # تحليل RSI
            rsi = calculate_rsi(g_df)
            rsi_text, rsi_type, recommendation = get_rsi_analysis(rsi)
            
            if rsi_type == "success":
                st.success(f"📊 **RSI:** {rsi:.1f}\n\n{rsi_text}")
            elif rsi_type == "error":
                st.error(f"📊 **RSI:** {rsi:.1f}\n\n{rsi_text}")
            else:
                st.info(f"📊 **RSI:** {rsi:.1f}\n\n{rsi_text}")
            
            st.caption(f"💡 {recommendation}")
    else:
        st.error("⚠️ تعذر جلب البيانات")

# ====================== التبويب الرابع: تحليل الشركات ======================
with tab4:
    st.subheader("🔍 البحث والتحليل العميق")
    
    model = init_gemini()
    
    search_ticker = st.text_input("أدخل رمز أي شركة (مثال: NVDA أو 2222.SR أو COMI.CA):", "").upper()
    
    if search_ticker:
        with st.spinner("🕶️ جاري جمع البيانات وتحليلها..."):
            stock, df = get_stock_data(search_ticker, "3mo")
            
            if stock and df is not None and not df.empty:
                info = stock.info
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1c24, #1e2030); padding: 20px; border-radius: 20px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">{info.get('longName', search_ticker)}</h2>
                    <p style="color: #888;">{info.get('sector', 'قطاع غير محدد')} | {info.get('industry', 'صناعة غير محددة')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
                daily_change = ((current_price - prev_price) / prev_price) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("💰 السعر الحالي", f"{current_price:,.2f}", f"{daily_change:+.2f}%")
                col2.metric("📊 مكرر الربحية (P/E)", info.get('trailingPE', 'N/A'))
                col3.metric("🏦 القيمة السوقية", f"{info.get('marketCap', 0):,}")
                col4.metric("📈 متوسط الحجم", f"{info.get('averageVolume', 0):,}")
                
                st.markdown("---")
                
                # التحليل الفني المتقدم
                st.subheader("📊 التحليل الفني")
                
                # حساب المؤشرات
                rsi = calculate_rsi(df)
                sma_20 = df['Close'].rolling(20).mean().iloc[-1]
                sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
                support = df['Low'].tail(30).min()
                resistance = df['High'].tail(30).max()
                
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("📈 RSI (14)", f"{rsi:.1f}")
                col_b.metric("📊 SMA 20", f"{sma_20:.2f}")
                col_c.metric("📉 SMA 50", f"{sma_50:.2f}")
                col_d.metric("🎯 الدعم/المقاومة", f"{support:.2f} / {resistance:.2f}")
                
                rsi_text, rsi_type, recommendation = get_rsi_analysis(rsi)
                
                if rsi_type == "success":
                    st.success(rsi_text)
                elif rsi_type == "error":
                    st.error(rsi_text)
                else:
                    st.info(rsi_text)
                
                # الرسم البياني المتقدم
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['Close'],
                    mode='lines',
                    name='السعر',
                    line=dict(color='#00ffcc', width=2)
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['Close'].rolling(20).mean(),
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='#ffaa00', width=1, dash='dash')
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=calculate_rsi(df, 14).rename('RSI'),
                    mode='lines',
                    name='RSI',
                    line=dict(color='#ff00ff', width=2)
                ), row=2, col=1)
                
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                
                fig.update_layout(
                    title=f"التحليل الفني المتقدم - {search_ticker}",
                    template="plotly_dark",
                    height=550,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # تحليل الذكاء الاصطناعي
                if model:
                    st.subheader("🧠 تحليل الذكاء الاصطناعي (البورصجي AI)")
                    
                    if st.button("🎯 استشارة البورصجي AI", use_container_width=True):
                        with st.spinner("البورصجي AI يفكر..."):
                            prompt = f"""
                            أنت خبير مالي. حلل السهم التالي:
                            الاسم: {info.get('longName', search_ticker)}
                            الرمز: {search_ticker}
                            السعر: {current_price:.2f}
                            التغير اليومي: {daily_change:+.2f}%
                            RSI: {rsi:.1f}
                            SMA 20: {sma_20:.2f}
                            SMA 50: {sma_50:.2f}
                            الدعم: {support:.2f}
                            المقاومة: {resistance:.2f}
                            
                            قدم تحليلاً مختصراً (3-4 جمل) بالعربية يشمل: الاتجاه، التوصية، ونسبة المخاطرة.
                            """
                            response = model.generate_content(prompt)
                            st.info(f"🕶️ **توصية البورصجي AI:**\n\n{response.text}")
                else:
                    st.warning("⚠️ أضف GEMINI_API_KEY في secrets لتفعيل التحليل بالذكاء الاصطناعي")
                
                # آخر الأخبار
                st.subheader("📰 آخر الأخبار")
                display_news(search_ticker)
                
            else:
                st.error("❌ لم يتم العثور على بيانات لهذا الرمز. تأكد من صحة الرمز (أضف .CA للشركات المصرية)")
    else:
        st.info("💡 أدخل رمز شركة للبدء في التحليل العميق")

# ====================== تذييل الصفحة ======================
st.markdown("""
<div class="footer">
    🕶️ منصة البورصجي AI | العين التي لا تنام في الأسواق<br>
    📊 البيانات من Yahoo Finance | تحديث لحظي | جميع الحقوق محفوظة © 2026
</div>
""", unsafe_allow_html=True)
