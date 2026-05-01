# borasjy_pro_terminal.py - بورصجي Pro Terminal (الإصدار النهائي)
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import google.generativeai as genai
import warnings
import time
import requests
import numpy as np
from threading import Thread

# إعدادات أساسية
warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="بورصجي Pro | Terminal",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed"
)

# ====================== CSS الاحترافي (نظام النيون المتطور) ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #050505 0%, #0a0a0f 100%);
        color: #e0e0e0;
    }
    
    /* الهيدر الاحترافي */
    .terminal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 25px;
        background: rgba(10, 10, 15, 0.95);
        border-bottom: 1px solid #00ffcc30;
        margin-bottom: 20px;
    }
    
    .logo-area {
        display: flex;
        align-items: baseline;
        gap: 15px;
    }
    
    .logo-glow {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    
    .logo-sub {
        font-size: 12px;
        color: #00ffcc80;
    }
    
    /* شريط الأسعار المتحرك */
    .ticker-wrapper {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.95);
        border-top: 2px solid #00ffcc;
        padding: 10px 0;
        z-index: 999;
        overflow: hidden;
        white-space: nowrap;
        backdrop-filter: blur(10px);
    }
    
    .ticker-content {
        display: inline-block;
        animation: ticker 35s linear infinite;
        font-weight: bold;
        font-size: 14px;
    }
    
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    .ticker-item {
        display: inline-block;
        margin: 0 25px;
        padding: 5px 10px;
        background: rgba(0, 255, 204, 0.1);
        border-radius: 20px;
    }
    
    .price-up { color: #00ff88; }
    .price-down { color: #ff4444; }
    
    /* بطاقات المؤشرات */
    .stat-card {
        background: linear-gradient(135deg, #111115, #0a0a0f);
        border: 1px solid #222;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00ffcc, #ff00ff);
    }
    
    .stat-card:hover {
        border-color: #00ffcc;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 255, 204, 0.1);
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .stat-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(17, 17, 21, 0.9);
        padding: 8px;
        border-radius: 20px;
        margin-bottom: 25px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 16px;
        padding: 10px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 255, 204, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        color: #000 !important;
        font-weight: bold;
    }
    
    /* شريط التحميل */
    .stSpinner > div {
        border-color: #00ffcc !important;
    }
    
    /* تذييل */
    .terminal-footer {
        text-align: center;
        padding: 20px;
        color: #555;
        font-size: 11px;
        margin-top: 40px;
        border-top: 1px solid #1a1a1a;
    }
    
    /* مؤشر التحديث */
    .live-badge {
        display: inline-block;
        background: #ff0000;
        color: white;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 20px;
        margin-left: 10px;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ====================== محرك البيانات الذكي ======================

@st.cache_data(ttl=30)
def fetch_live_data(symbols):
    """جلب البيانات الحية للأسهم"""
    data_list = []
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((price - prev_price) / prev_price) * 100
                data_list.append({
                    "symbol": sym.replace(".CA", "").replace("-USD", ""),
                    "price": price,
                    "change": change,
                    "volume": hist['Volume'].iloc[-1] if 'Volume' in hist else 0
                })
        except:
            continue
    return data_list

@st.cache_data(ttl=60)
def get_market_indices():
    """جلب بيانات المؤشرات الرئيسية"""
    indices = {
        "EGX 30": "^EGX30",
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI",
        "TASI": "^TASI",
        "ذهب": "GC=F",
        "نفط": "CL=F",
        "بيتكوين": "BTC-USD"
    }
    
    results = {}
    for name, symbol in indices.items():
        try:
            data = yf.Ticker(symbol).history(period="2d")
            if not data.empty and len(data) >= 2:
                price = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                change = ((price - prev) / prev) * 100
                results[name] = {"price": price, "change": change}
            else:
                results[name] = {"price": 0, "change": 0}
        except:
            results[name] = {"price": 0, "change": 0}
    return results

def get_technical_indicators(df, period=14):
    """حساب المؤشرات الفنية المتقدمة"""
    if df.empty or len(df) < period:
        return df
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['StdDev'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['StdDev'] * 2)
    df['Lower'] = df['MA20'] - (df['StdDev'] * 2)
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    
    # المتوسطات المتحركة
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    
    return df

def get_stock_fundamentals(ticker):
    """جلب البيانات الأساسية للسهم"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get('longName', ticker),
            "sector": info.get('sector', 'غير محدد'),
            "industry": info.get('industry', 'غير محدد'),
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "eps": info.get('trailingEps', 'N/A'),
            "dividend_yield": info.get('dividendYield', 0),
            "target_price": info.get('targetMeanPrice', 'N/A'),
            "recommendation": info.get('recommendationKey', 'N/A')
        }
    except:
        return None

# ====================== إعداد الذكاء الاصطناعي ======================

def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel('gemini-1.5-pro')
    except:
        pass
    return None

def get_ai_analysis(ticker, df, fundamentals, user_query=""):
    """تحليل متقدم باستخدام الذكاء الاصطناعي"""
    if df.empty or len(df) < 20:
        return "بيانات غير كافية للتحليل"
    
    current_price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1] if 'RSI' in df else 50
    sma_20 = df['SMA_20'].iloc[-1] if 'SMA_20' in df else current_price
    sma_50 = df['SMA_50'].iloc[-1] if 'SMA_50' in df else current_price
    support = df['Low'].tail(30).min()
    resistance = df['High'].tail(30).max()
    
    prompt = f"""
    أنت خبير مالي محلل في الأسواق المصرية والعالمية. قم بتحليل عميق للسهم التالي:
    
    📊 البيانات الفنية:
    - الرمز: {ticker}
    - السعر الحالي: {current_price:.2f}
    - RSI (14): {rsi:.1f}
    - المتوسط المتحرك 20: {sma_20:.2f}
    - المتوسط المتحرك 50: {sma_50:.2f}
    - الدعم: {support:.2f}
    - المقاومة: {resistance:.2f}
    
    📋 البيانات الأساسية:
    - الاسم: {fundamentals.get('name', ticker) if fundamentals else ticker}
    - القطاع: {fundamentals.get('sector', 'غير محدد') if fundamentals else 'غير محدد'}
    - القيمة السوقية: {fundamentals.get('market_cap', 0):,} if fundamentals else 'غير محدد'
    - مكرر الربحية: {fundamentals.get('pe_ratio', 'N/A') if fundamentals else 'N/A'}
    
    بناءً على هذه البيانات، قم بتقديم:
    1. تحليل اتجاه السهم (صاعد/هابط/جانبي)
    2. تقييم المخاطر بناءً على RSI والمتوسطات
    3. توصية واضحة (شراء/بيع/انتظار) مع نسبة الثقة
    4. مستويات الدخول والخروج المقترحة
    
    الرد باللغة العربية بشكل احترافي ومختصر (حد أقصى 200 كلمة).
    """
    
    if user_query:
        prompt = f"{prompt}\n\nسؤال إضافي من المستخدم: {user_query}\nأجب عليه في نهاية التحليل."
    
    model = init_gemini()
    if model:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ خطأ في التحليل: {e}"
    return "⚠️ يرجى إضافة GEMINI_API_KEY في ملف secrets لتفعيل التحليل بالذكاء الاصطناعي"

# ====================== قائمة الأسهم للشريط المتحرك ======================
TICKER_POOL = [
    "COMI.CA", "TMGH.CA", "FWRY.CA", "SWDY.CA", "ETEL.CA", "EAST.CA",
    "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN",
    "BTC-USD", "ETH-USD", "GC=F", "CL=F"
]

# ====================== واجهة المستخدم الرئيسية ======================

# الهيدر الاحترافي
st.markdown("""
<div class="terminal-header">
    <div class="logo-area">
        <div>
            <span class="logo-glow">BORSAJY PRO</span>
            <span class="logo-sub">TERMINAL</span>
        </div>
        <div class="live-badge">LIVE</div>
    </div>
    <div style="display: flex; gap: 15px;">
        <div style="font-size: 12px;">📅 """ + datetime.now().strftime("%Y-%m-%d") + """</div>
        <div style="font-size: 12px;">🕐 """ + datetime.now().strftime("%H:%M:%S") + """</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ====================== التبويبات الرئيسية ======================
tabs = st.tabs(["🏛️ قاعة التداول", "📊 التحليل العميق", "🤖 بوت الذكاء الخارق", "🗞️ غرفة الأخبار"])

# ====================== Tab 1: قاعة التداول ======================
with tabs[0]:
    st.markdown("### 📈 مؤشرات السوق اللحظية")
    
    indices_data = get_market_indices()
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for i, (name, data) in enumerate(indices_data.items()):
        if i < 4:
            with cols[i]:
                change_color = "🟢" if data['change'] >= 0 else "🔴"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">{name}</div>
                    <div class="stat-value">{data['price']:,.2f}</div>
                    <div style="color: {'#00ff88' if data['change'] >= 0 else '#ff4444'}; font-size: 14px;">
                        {change_color} {data['change']:+.2f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    cols2 = [col5, col6, col7, col8]
    
    for i, (name, data) in enumerate(indices_data.items()):
        if i >= 4:
            with cols2[i-4]:
                change_color = "🟢" if data['change'] >= 0 else "🔴"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">{name}</div>
                    <div class="stat-value">{data['price']:,.2f}</div>
                    <div style="color: {'#00ff88' if data['change'] >= 0 else '#ff4444'}; font-size: 14px;">
                        {change_color} {data['change']:+.2f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔝 الشركات الأكثر نشاطاً")
    
    top_stocks = ["COMI.CA", "TMGH.CA", "SWDY.CA", "NVDA", "AAPL", "TSLA"]
    
    for stock in top_stocks:
        try:
            data = yf.Ticker(stock).history(period="1mo")
            if not data.empty:
                current = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2] if len(data) > 1 else current
                change = ((current - prev) / prev) * 100
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    status = "🟢" if change >= 0 else "🔴"
                    st.markdown(f"**{stock}** {status}")
                    st.caption(f"{current:.2f} ({change:+.2f}%)")
                with col2:
                    # Sparkline chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data['Close'],
                        mode='lines',
                        line=dict(color='#00ffcc', width=1.5),
                        fill='tozeroy',
                        fillcolor='rgba(0, 255, 204, 0.1)
                    ))
                    fig.update_layout(
                        height=50,
                        margin=dict(l=0, r=0, t=0, b=0),
                        xaxis_visible=False,
                        yaxis_visible=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
        except:
            pass

# ====================== Tab 2: التحليل العميق ======================
with tabs[1]:
    st.markdown("### 📊 منصة التحليل الفني المتقدم")
    
    col_input, col_period = st.columns([3, 1])
    with col_input:
        symbol = st.text_input("أدخل رمز السهم (مثال: COMI.CA أو MSFT):", "COMI.CA").upper()
    with col_period:
        period = st.selectbox("الفترة الزمنية", ["1mo", "3mo", "6mo", "1y"], index=2)
    
    if symbol:
        with st.spinner("جاري تحميل البيانات وتحليلها..."):
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            fundamentals = get_stock_fundamentals(symbol)
            
            if not df.empty and len(df) > 20:
                df = get_technical_indicators(df)
                
                current_price = df['Close'].iloc[-1]
                rsi = df['RSI'].iloc[-1] if 'RSI' in df else 50
                
                # معلومات سريعة
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("💰 السعر الحالي", f"{current_price:.2f}")
                col2.metric("📊 RSI (14)", f"{rsi:.1f}")
                col3.metric("🎯 SMA 20", f"{df['SMA_20'].iloc[-1]:.2f}" if 'SMA_20' in df else "--")
                col4.metric("📈 SMA 50", f"{df['SMA_50'].iloc[-1]:.2f}" if 'SMA_50' in df else "--")
                
                # الرسم البياني المتقدم
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.5, 0.25, 0.25],
                    subplot_titles=("السعر مع Bollinger Bands", "RSI (14)", "MACD")
                )
                
                # Candlestick chart
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'], name="السعر"
                ), row=1, col=1)
                
                # Bollinger Bands
                if 'Upper' in df:
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['Upper'], name="Upper",
                        line=dict(color='rgba(173, 216, 230, 0.3)')
                    ), row=1, col=1)
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['Lower'], name="Lower",
                        line=dict(color='rgba(173, 216, 230, 0.3)'), fill='tonexty'
                    ), row=1, col=1)
                
                # RSI
                if 'RSI' in df:
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['RSI'], name="RSI",
                        line=dict(color='#ff00ff', width=2)
                    ), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, row=2, col=1)
                    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, row=2, col=1)
                
                # MACD
                if 'MACD' in df:
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['MACD'], name="MACD",
                        line=dict(color='#00ffcc', width=1.5)
                    ), row=3, col=1)
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['Signal'], name="Signal",
                        line=dict(color='#ffaa00', width=1.5, dash='dash')
                    ), row=3, col=1)
                    
                    # Histogram
                    colors = ['red' if val < 0 else 'green' for val in df['MACD_Hist']]
                    fig.add_trace(go.Bar(
                        x=df.index, y=df['MACD_Hist'], name="Histogram",
                        marker_color=colors, opacity=0.5
                    ), row=3, col=1)
                
                fig.update_layout(
                    template="plotly_dark",
                    height=700,
                    xaxis_rangeslider_visible=False,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # مستويات الدعم والمقاومة
                support = df['Low'].tail(50).min()
                resistance = df['High'].tail(50).max()
                
                col_sup, col_res = st.columns(2)
                with col_sup:
                    st.info(f"🛡️ **مستوى الدعم:** {support:.2f}")
                with col_res:
                    st.warning(f"⚡ **مستوى المقاومة:** {resistance:.2f}")
                
                # تحليل RSI
                if rsi < 30:
                    st.success(f"✅ **إشارة شراء قوية!** RSI عند {rsi:.1f} - منطقة ذروة بيع")
                elif rsi > 70:
                    st.error(f"⚠️ **إشارة بيع!** RSI عند {rsi:.1f} - منطقة ذروة شراء")
                else:
                    st.info(f"⚖️ **منطقة محايدة** - RSI عند {rsi:.1f}")
                
            else:
                st.error("❌ لا توجد بيانات كافية للتحليل. تأكد من صحة الرمز.")
    else:
        st.info("💡 أدخل رمز سهم للبدء في التحليل العميق")

# ====================== Tab 3: بوت الذكاء الخارق ======================
with tabs[2]:
    st.markdown("### 🤖 BORSAJY AI ENGINE - العقل المدبر")
    st.markdown("*اسأل البورصجي AI عن أي سهم أو استراتيجية واحصل على تحليل احترافي فوري*")
    
    col_ai1, col_ai2 = st.columns([2, 1])
    with col_ai1:
        ai_ticker = st.text_input("أدخل رمز السهم للتحليل:", "COMI.CA").upper()
    with col_ai2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 تحليل متقدم", use_container_width=True):
            st.session_state['ai_analyze'] = ai_ticker
    
    if 'ai_analyze' in st.session_state:
        ticker = st.session_state['ai_analyze']
        with st.spinner(f"البورصجي AI يحلل {ticker}..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period="3mo")
            if not df.empty:
                df = get_technical_indicators(df)
                fundamentals = get_stock_fundamentals(ticker)
                analysis = get_ai_analysis(ticker, df, fundamentals, "")
                
                st.markdown("---")
                st.markdown("### 🧠 تحليل البورصجي AI")
                st.markdown(analysis)
            else:
                st.error("لم يتم العثور على بيانات لهذا السهم")
    
    st.markdown("---")
    st.markdown("### 💬 اسأل البورصجي AI")
    
    user_query = st.chat_input("اكتب سؤالك هنا (مثال: هل سهم TMGH مناسب للشراء الآن؟)")
    
    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("البورصجي AI يفكر..."):
                # استخراج رمز السهم من السؤال إذا وجد
                words = user_query.split()
                possible_ticker = None
                for word in words:
                    word_clean = word.upper().replace("؟", "").replace("?", "")
                    if len(word_clean) >= 3 and (word_clean.isalpha() or ".CA" in word_clean):
                        possible_ticker = word_clean
                        break
                
                if possible_ticker:
                    stock = yf.Ticker(possible_ticker)
                    df = stock.history(period="2mo")
                    if not df.empty:
                        df = get_technical_indicators(df)
                        fundamentals = get_stock_fundamentals(possible_ticker)
                        response = get_ai_analysis(possible_ticker, df, fundamentals, user_query)
                        st.markdown(response)
                    else:
                        model = init_gemini()
                        if model:
                            response = model.generate_content(f"أنت خبير مالي. أجب على السؤال: {user_query}")
                            st.markdown(response.text)
                        else:
                            st.warning("⚠️ يرجى إضافة GEMINI_API_KEY لتفعيل البوت")
                else:
                    model = init_gemini()
                    if model:
                        response = model.generate_content(f"أنت خبير مالي. أجب على السؤال: {user_query}")
                        st.markdown(response.text)
                    else:
                        st.warning("⚠️ يرجى إضافة GEMINI_API_KEY لتفعيل البوت")

# ====================== Tab 4: غرفة الأخبار ======================
with tabs[3]:
    st.markdown("### 🗞️ آخر أخبار الأسواق")
    
    news_sources = ["AAPL", "MSFT", "GOOGL", "TSLA", "COMI.CA", "NVDA"]
    
    for source in news_sources:
        try:
            ticker = yf.Ticker(source)
            news = ticker.news if hasattr(ticker, 'news') else []
            if news:
                for item in news[:3]:
                    st.markdown(f"""
                    <div class="stat-card" style="text-align: right; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="badge">{source}</span>
                            <span style="font-size: 11px; color: #888;">{datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d %H:%M')}</span>
                        </div>
                        <h4 style="margin: 10px 0; font-size: 14px;">{item['title'][:150]}</h4>
                        <p style="color: #888; font-size: 12px;">📰 {item.get('publisher', 'مصدر غير معروف')}</p>
                        <a href="{item['link']}" target="_blank" style="color: #00ffcc;">📖 قراءة المزيد →</a>
                    </div>
                    """, unsafe_allow_html=True)
        except:
            pass
    
    st.info("📡 يتم تحديث الأخبار تلقائياً من مصادر موثوقة")

# ====================== شريط الأسعار المتحرك ======================
live_data = fetch_live_data(TICKER_POOL)

ticker_html = '<div class="ticker-wrapper"><div class="ticker-content">'
for item in live_data:
    color_class = "price-up" if item['change'] >= 0 else "price-down"
    arrow = "▲" if item['change'] >= 0 else "▼"
    ticker_html += f'<span class="ticker-item">{item["symbol"]} <span class="{color_class}">{item["price"]:.2f} ({arrow}{abs(item["change"]):.2f}%)</span></span>'
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# مساحة للسكرول
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

# ====================== تذييل الصفحة ======================
st.markdown("""
<div class="terminal-footer">
    🕶️ BORSAJY PRO TERMINAL | العين التي لا تنام في الأسواق<br>
    📊 البيانات من Yahoo Finance | 🤖 تحليلات Gemini AI | تحديث لحظي<br>
    © 2026 جميع الحقوق محفوظة
</div>
""", unsafe_allow_html=True)
