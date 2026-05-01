# borasjy_pro_terminal.py - بورصجي Pro Terminal (الإصدار التحليلي المتقدم)
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import google.generativeai as genai
import warnings
import requests
from scipy import stats

warnings.filterwarnings('ignore')
st.set_page_config(
    page_title="بورصجي Pro | التحليل المتقدم",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# ====================== CSS ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .stApp { background: #000000; color: #e0e0e0; }
    
    /* شريط الأسعار المتحرك */
    .ticker-wrapper {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #000000; border-top: 1px solid #00ffcc;
        padding: 8px 0; z-index: 999; overflow: hidden; white-space: nowrap;
    }
    .ticker-content { display: inline-block; animation: ticker 35s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-item { display: inline-block; margin: 0 20px; color: #00ffcc; }
    .price-up { color: #00ff88; }
    .price-down { color: #ff4444; }
    
    .stat-card {
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 16px;
        padding: 20px; text-align: center; transition: 0.3s;
    }
    .stat-card:hover { border-color: #00ffcc; transform: translateY(-3px); }
    .stat-value { font-size: 28px; font-weight: bold; margin: 10px 0; color: #00ffcc; }
    .stat-label { font-size: 12px; color: #888; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #0a0a0a; padding: 8px; border-radius: 20px; }
    .stTabs [data-baseweb="tab"] { border-radius: 16px; padding: 10px 24px; }
    .stTabs [aria-selected="true"] { background: #00ffcc; color: #000 !important; }
    
    .terminal-footer { text-align: center; padding: 20px; color: #555; font-size: 11px; border-top: 1px solid #1a1a1a; }
    .live-badge { display: inline-block; background: #ff0000; color: white; font-size: 10px; padding: 2px 8px; border-radius: 20px; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# ====================== الدوال التحليلية الأساسية ======================

@st.cache_data(ttl=30)
def fetch_live_data(symbols):
    data_list = []
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                price = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = ((price - prev) / prev) * 100
                data_list.append({"symbol": sym.replace(".CA", ""), "price": price, "change": change})
        except: continue
    return data_list

@st.cache_data(ttl=60)
def get_market_indices():
    indices = {"EGX 30": "^EGX30", "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI", "ذهب": "GC=F", "نفط": "CL=F", "بيتكوين": "BTC-USD"}
    results = {}
    for name, symbol in indices.items():
        try:
            data = yf.Ticker(symbol).history(period="2d")
            if not data.empty and len(data) >= 2:
                results[name] = {"price": data['Close'].iloc[-1], "change": ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100}
        except: continue
    return results

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_technical_indicators(df):
    if df.empty or len(df) < 20: return df
    df['RSI'] = calculate_rsi(df['Close'])
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['Upper'] = df['MA20'] + (df['Close'].rolling(20).std() * 2)
    df['Lower'] = df['MA20'] - (df['Close'].rolling(20).std() * 2)
    return df

# ====================== المؤشرات المتقدمة ======================

def draw_fear_greed_gauge(rsi_value):
    """عداد الخوف والطمع"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rsi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "🔄 حالة السوق النفسية (RSI)", 'font': {'size': 20, 'color': '#00ffcc'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#888"},
            'bar': {'color': "#00ffcc"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#444",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0, 255, 136, 0.4)', 'name': "🟢 خوف - شراء"},
                {'range': [30, 70], 'color': 'rgba(255, 255, 255, 0.1)', 'name': "⚪ محايد"},
                {'range': [70, 100], 'color': 'rgba(255, 68, 68, 0.4)', 'name': "🔴 طمع - بيع"}
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': rsi_value}
        },
        delta={'reference': 50, 'increasing': {'color': "#00ff88"}, 'decreasing': {'color': "#ff4444"}}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Cairo"}, height=280)
    return fig

def draw_market_heatmap():
    """خريطة حرارة قطاعات السوق"""
    sectors = {
        "🏦 البنوك": 2.5, "🏗️ العقارات": -1.2, "📡 الاتصالات": 3.1,
        "🏭 الصناعة": 0.8, "🛒 التجارة": -0.5, "💊 الأدوية": 1.2
    }
    
    colors = ['#00ff88' if v > 0 else '#ff4444' for v in sectors.values()]
    sizes = [abs(v) * 50 + 20 for v in sectors.values()]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(sectors.keys()), y=[0]*len(sectors),
        mode='markers+text',
        marker=dict(size=sizes, color=colors, opacity=0.8, line=dict(width=2, color='white')),
        text=[f"{k}<br>{v:+.1f}%" for k, v in sectors.items()],
        textposition="middle center",
        textfont=dict(size=12, color='white')
    ))
    fig.update_layout(
        title="📊 أداء القطاعات - خريطة الحرارة",
        template="plotly_dark",
        height=200,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def monte_carlo_simulation(prices, days=30, simulations=1000):
    """محاكاة مونت كارلو لتوقع الأسعار"""
    if len(prices) < 20:
        return None
    
    returns = prices.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    
    last_price = prices.iloc[-1]
    dt = 1/252
    
    simulations_results = []
    for _ in range(simulations):
        daily_returns = np.random.normal(mu, sigma, days)
        price_path = last_price * (1 + daily_returns).cumprod()
        simulations_results.append(price_path[-1])
    
    simulations_results = np.array(simulations_results)
    
    return {
        "current_price": last_price,
        "expected_price": np.mean(simulations_results),
        "lower_bound": np.percentile(simulations_results, 5),
        "upper_bound": np.percentile(simulations_results, 95),
        "probability_up": np.mean(simulations_results > last_price) * 100,
        "risk_percent": (np.std(simulations_results) / np.mean(simulations_results)) * 100
    }

def calculate_fair_value_dcf(ticker):
    """حساب القيمة العادلة باستخدام DCF المبسط"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        cashflow = info.get('freeCashflow', 0)
        shares = info.get('sharesOutstanding', 1)
        growth_rate = 0.05  # افتراض نمو 5%
        discount_rate = 0.10  # معدل خصم 10%
        
        if cashflow and cashflow > 0:
            fcf_per_share = cashflow / shares
            fair_value = fcf_per_share * (1 + growth_rate) / (discount_rate - growth_rate)
            return fair_value
    except:
        pass
    return None

def get_accounting_values(ticker):
    """جلب القيم المحاسبية"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "pb_ratio": info.get('priceToBook', 'N/A'),
            "roe": info.get('returnOnEquity', 'N/A'),
            "debt_to_equity": info.get('debtToEquity', 'N/A'),
            "profit_margins": info.get('profitMargins', 'N/A'),
            "market_cap": info.get('marketCap', 0)
        }
    except:
        return None

def get_stock_news_sentiment(ticker):
    """تحليل مشاعر الأخبار"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news if hasattr(stock, 'news') else []
        if news:
            positive_words = ['up', 'rise', 'gain', 'profit', 'growth', 'positive', 'تحسن', 'ارتفاع', 'أرباح']
            negative_words = ['down', 'fall', 'loss', 'drop', 'negative', 'crisis', 'هبوط', 'خسارة', 'أزمة']
            
            sentiment_score = 0
            for item in news[:10]:
                title = item.get('title', '').lower()
                for word in positive_words:
                    if word in title:
                        sentiment_score += 1
                for word in negative_words:
                    if word in title:
                        sentiment_score -= 1
            
            sentiment_score = max(-1, min(1, sentiment_score / 10))
            
            if sentiment_score > 0.2:
                return {"sentiment": "positive", "score": sentiment_score, "message": "😊 أخبار إيجابية"}
            elif sentiment_score < -0.2:
                return {"sentiment": "negative", "score": sentiment_score, "message": "😞 أخبار سلبية"}
            else:
                return {"sentiment": "neutral", "score": sentiment_score, "message": "😐 أخبار محايدة"}
    except:
        pass
    return {"sentiment": "neutral", "score": 0, "message": "لا توجد أخبار كافية"}

def draw_ichimoku_cloud(df, ticker):
    """رسم سحابة إيشيموكو"""
    if len(df) < 52:
        return None
    
    # حساب مكونات إيشيموكو
    period9 = 9
    period26 = 26
    period52 = 52
    
    df['Tenkan'] = (df['High'].rolling(window=period9).max() + df['Low'].rolling(window=period9).min()) / 2
    df['Kijun'] = (df['High'].rolling(window=period26).max() + df['Low'].rolling(window=period26).min()) / 2
    df['Senkou_A'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(period26)
    df['Senkou_B'] = ((df['High'].rolling(window=period52).max() + df['Low'].rolling(window=period52).min()) / 2).shift(period26)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='السعر', line=dict(color='#00ffcc', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Tenkan'], name='Tenkan', line=dict(color='#ffaa00', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['Kijun'], name='Kijun', line=dict(color='#ff00ff', width=1, dash='dash')))
    
    # سحابة المستقبل
    fig.add_trace(go.Scatter(x=df.index, y=df['Senkou_A'], name='Senkou A', line=dict(color='rgba(0,255,204,0.5)', width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Senkou_B'], name='Senkou B', line=dict(color='rgba(255,0,255,0.5)', width=1), fill='tonexty', fillcolor='rgba(0,255,204,0.1)'))
    
    fig.update_layout(template="plotly_dark", height=500, title=f"📊 سحابة إيشيموكو - {ticker}", xaxis_title="التاريخ", yaxis_title="السعر")
    return fig

def draw_price_with_signals(df, ticker):
    """رسم السعر مع إشارات البيع والشراء"""
    if df.empty:
        return None
    
    df['RSI'] = calculate_rsi(df['Close'])
    
    # إشارات الشراء (RSI < 30)
    buy_signals = df[df['RSI'] < 30]
    # إشارات البيع (RSI > 70)
    sell_signals = df[df['RSI'] > 70]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='السعر', line=dict(color='#00ffcc', width=2), fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.05)'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='#ffaa00', width=1.5, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50', line=dict(color='#ff4444', width=1.5, dash='dot')))
    
    # إضافة إشارات الشراء (نقاط خضراء)
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='🟢 شراء', marker=dict(color='#00ff88', size=12, symbol='triangle-up')))
    
    # إضافة إشارات البيع (نقاط حمراء)
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', name='🔴 بيع', marker=dict(color='#ff4444', size=12, symbol='triangle-down')))
    
    fig.update_layout(template="plotly_dark", height=500, title=f"📈 {ticker} - إشارات البيع والشراء التلقائية", xaxis_title="التاريخ", yaxis_title="السعر")
    return fig

# ====================== إعداد Gemini ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel('gemini-1.5-pro')
    except: pass
    return None

def get_ai_deep_analysis(ticker, df, fundamentals, accounting, sentiment, mc_results):
    """تحليل عميق متكامل من الذكاء الاصطناعي"""
    if df.empty:
        return "لا توجد بيانات كافية"
    
    current_price = df['Close'].iloc[-1]
    rsi = df['RSI'].iloc[-1] if 'RSI' in df else 50
    
    prompt = f"""
    أنت خبير مالي عالمي. قم بتحليل شامل للسهم {ticker} بناءً على:
    
    📊 **البيانات الفنية:**
    - السعر: {current_price:.2f}
    - RSI: {rsi:.1f}
    - الاتجاه: {'صاعد' if df['Close'].iloc[-1] > df['MA20'].iloc[-1] else 'هابط' if df['Close'].iloc[-1] < df['MA20'].iloc[-1] else 'جانبي'}
    
    📈 **توقعات مونت كارلو:**
    - السعر المتوقع: {mc_results['expected_price']:.2f if mc_results else current_price}
    - احتمالية الصعود: {mc_results['probability_up']:.1f}% if mc_results else 'غير متاح'
    
    📋 **البيانات المحاسبية:**
    - مكرر الربحية: {accounting.get('pe_ratio', 'N/A') if accounting else 'N/A'}
    - مضاعف القيمة الدفترية: {accounting.get('pb_ratio', 'N/A') if accounting else 'N/A'}
    - العائد على حقوق الملكية: {accounting.get('roe', 'N/A') if accounting else 'N/A'}
    
    🗞️ **تحليل المشاعر:**
    - {sentiment.get('message', 'بيانات غير متاحة')}
    
    المطلوب:
    1. تقييم القيمة العادلة للسهم مقارنة بالسعر الحالي
    2. تحليل المخاطر بناءً على المؤشرات الفنية والمحاسبية
    3. توصية واضحة (شراء قوي/شراء/انتظار/بيع/بيع قوي)
    4. مستويات الدخول والخروج المقترحة
    5. ملخص تنفيذي للمستثمر
    
    الرد بالعربية بشكل احترافي ومختصر.
    """
    
    model = init_gemini()
    if model:
        try:
            response = model.generate_content(prompt)
            return response.text
        except: pass
    return "⚠️ أضف GEMINI_API_KEY لتفعيل التحليل العميق"

# ====================== البيانات ======================
TICKER_POOL = ["COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "AAPL", "NVDA", "TSLA", "MSFT", "BTC-USD", "GC=F"]

# ====================== الواجهة الرئيسية ======================

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #000; border-bottom: 1px solid #00ffcc;">
    <div>
        <span style="font-size: 28px; font-weight: 800; color: #00ffcc;">BORSAJY PRO</span>
        <span style="font-size: 12px; color: #888;">تحليل متقدم | ذكاء اصطناعي</span>
    </div>
    <div>
        <span class="live-badge">LIVE</span>
        <span style="font-size: 12px; margin-left: 15px;">📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# التبويبات
tabs = st.tabs(["🏛️ قاعة التداول", "📊 التحليل المتقدم", "🎯 القيمة العادلة", "🤖 العقل المدبر", "🗞️ الأخبار"])

# ====================== Tab 1: قاعة التداول ======================
with tabs[0]:
    st.markdown("### 📈 مؤشرات السوق اللحظية")
    
    col1, col2, col3, col4 = st.columns(4)
    indices_data = get_market_indices()
    
    for i, (name, data) in enumerate(indices_data.items()):
        if i < 4:
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">{name}</div>
                    <div class="stat-value">{data['price']:,.2f}</div>
                    <div style="color: {'#00ff88' if data['change'] >= 0 else '#ff4444'};">{data['change']:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    # خريطة الحرارة
    st.plotly_chart(draw_market_heatmap(), use_container_width=True)
    
    st.markdown("### 🔝 الأسهم الأكثر نشاطاً")
    top_stocks = ["COMI.CA", "TMGH.CA", "AAPL", "NVDA", "TSLA"]
    for stock in top_stocks:
        data = yf.Ticker(stock).history(period="1mo")
        if not data.empty:
            current = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2] if len(data) > 1 else current
            change = ((current - prev) / prev) * 100
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{stock}** {'🟢' if change >= 0 else '🔴'}\n{current:.2f}")
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], line=dict(color='#00ffcc', width=1.5), fill='tozeroy', fillcolor='rgba(0,255,204,0.1)'))
                fig.update_layout(height=50, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)

# ====================== Tab 2: التحليل المتقدم ======================
with tabs[1]:
    st.markdown("### 📊 منصة التحليل المتقدم")
    
    symbol = st.text_input("🔍 أدخل رمز السهم:", "COMI.CA").upper()
    period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y"], index=2)
    
    if symbol:
        with st.spinner("جاري التحليل المتقدم..."):
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if not df.empty and len(df) > 20:
                df = get_technical_indicators(df)
                rsi = df['RSI'].iloc[-1] if 'RSI' in df else 50
                current_price = df['Close'].iloc[-1]
                
                # عداد الخوف والطمع
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.plotly_chart(draw_fear_greed_gauge(rsi), use_container_width=True)
                    
                    # توقعات مونت كارلو
                    mc_results = monte_carlo_simulation(df['Close'])
                    if mc_results:
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-label">🎲 توقعات مونت كارلو (30 يوم)</div>
                            <div class="stat-value">{mc_results['expected_price']:.2f}</div>
                            <div>🎯 احتمالية الصعود: {mc_results['probability_up']:.0f}%</div>
                            <div>📊 نطاق التوقع: {mc_results['lower_bound']:.2f} - {mc_results['upper_bound']:.2f}</div>
                            <div>⚠️ نسبة المخاطرة: {mc_results['risk_percent']:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    # تحليل المشاعر
                    sentiment = get_stock_news_sentiment(symbol)
                    sentiment_color = "#00ff88" if sentiment['sentiment'] == 'positive' else "#ff4444" if sentiment['sentiment'] == 'negative' else "#ffaa00"
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">🗞️ تحليل المشاعر الإخبارية</div>
                        <div class="stat-value" style="color: {sentiment_color};">{sentiment['message']}</div>
                        <div>درجة المشاعر: {sentiment['score']:+.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # إشارة سريعة
                    if rsi < 30:
                        st.success("✅ **إشارة شراء قوية!** منطقة ذروة بيع")
                    elif rsi > 70:
                        st.error("⚠️ **إشارة بيع!** منطقة ذروة شراء")
                    else:
                        st.info("⚖️ منطقة محايدة - انتظار وضوح الاتجاه")
                
                # الرسم البياني مع الإشارات
                st.plotly_chart(draw_price_with_signals(df, symbol), use_container_width=True)
                
                # سحابة إيشيموكو
                ichimoku_fig = draw_ichimoku_cloud(df, symbol)
                if ichimoku_fig:
                    st.plotly_chart(ichimoku_fig, use_container_width=True)
                
                # القيم المحاسبية
                accounting = get_accounting_values(symbol)
                if accounting:
                    st.markdown("### 📊 القيم المحاسبية")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("📈 مكرر الربحية (P/E)", accounting.get('pe_ratio', 'N/A'))
                    col2.metric("💰 مضاعف القيمة الدفترية", accounting.get('pb_ratio', 'N/A'))
                    col3.metric("🏆 العائد على حقوق الملكية", f"{accounting.get('roe', 0)*100:.1f}%" if accounting.get('roe') else 'N/A')
                    col4.metric("⚖️ الدين/حقوق الملكية", f"{accounting.get('debt_to_equity', 0):.1f}%" if accounting.get('debt_to_equity') else 'N/A')
                
                # مستويات الدعم والمقاومة
                support = df['Low'].tail(50).min()
                resistance = df['High'].tail(50).max()
                col1, col2 = st.columns(2)
                col1.info(f"🛡️ **مستوى الدعم:** {support:.2f}")
                col2.warning(f"⚡ **مستوى المقاومة:** {resistance:.2f}")
                
            else:
                st.error("بيانات غير كافية للتحليل")

# ====================== Tab 3: القيمة العادلة ======================
with tabs[2]:
    st.markdown("### 🎯 نموذج القيمة العادلة (DCF)")
    
    fair_ticker = st.text_input("أدخل رمز السهم لحساب القيمة العادلة:", "COMI.CA").upper()
    
    if fair_ticker:
        with st.spinner("جاري حساب القيمة العادلة..."):
            stock = yf.Ticker(fair_ticker)
            df = stock.history(period="6mo")
            current_price = df['Close'].iloc[-1] if not df.empty else 0
            fair_value = calculate_fair_value_dcf(fair_ticker)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">💰 السعر الحالي</div>
                    <div class="stat-value">{current_price:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if fair_value:
                    discount = ((fair_value - current_price) / current_price) * 100 if current_price > 0 else 0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">🎯 القيمة العادلة (DCF)</div>
                        <div class="stat-value" style="color: {'#00ff88' if discount > 0 else '#ff4444'};">{fair_value:.2f}</div>
                        <div>{'خصم' if discount > 0 else 'علاوة'} {abs(discount):.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("لا توجد بيانات كافية لحساب القيمة العادلة")
            
            if fair_value:
                if fair_value > current_price:
                    st.success(f"✅ **السهم مقيم بأقل من قيمته!** القيمة العادلة أعلى بنسبة {((fair_value - current_price)/current_price*100):.1f}% من السعر الحالي")
                else:
                    st.error(f"⚠️ **السهم مقيم بأعلى من قيمته!** القيمة العادلة أقل بنسبة {((current_price - fair_value)/current_price*100):.1f}% من السعر الحالي")

# ====================== Tab 4: العقل المدبر ======================
with tabs[3]:
    st.markdown("### 🤖 العقل المدبر - تحليل الذكاء الاصطناعي المتكامل")
    
    ai_ticker = st.text_input("أدخل رمز السهم للتحليل العميق:", "COMI.CA").upper()
    
    if st.button("🚀 تشغيل التحليل المتكامل", use_container_width=True):
        with st.spinner("العقل المدبر يحلل السهم..."):
            stock = yf.Ticker(ai_ticker)
            df = stock.history(period="6mo")
            
            if not df.empty:
                df = get_technical_indicators(df)
                accounting = get_accounting_values(ai_ticker)
                sentiment = get_stock_news_sentiment(ai_ticker)
                mc_results = monte_carlo_simulation(df['Close'])
                
                analysis = get_ai_deep_analysis(ai_ticker, df, None, accounting, sentiment, mc_results)
                st.markdown("### 🧠 تقرير العقل المدبر")
                st.markdown(analysis)
            else:
                st.error("لا توجد بيانات كافية")

# ====================== Tab 5: الأخبار ======================
with tabs[4]:
    st.markdown("### 🗞️ آخر أخبار الأسواق")
    
    news_sources = ["AAPL", "MSFT", "GOOGL", "TSLA", "COMI.CA", "NVDA"]
    for source in news_sources:
        try:
            ticker = yf.Ticker(source)
            if hasattr(ticker, 'news') and ticker.news:
                for item in ticker.news[:2]:
                    st.markdown(f"""
                    <div class="stat-card" style="text-align: right; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #00ffcc;">{source}</span>
                            <span style="font-size: 11px;">{datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d %H:%M')}</span>
                        </div>
                        <h4 style="margin: 10px 0;">{item['title'][:150]}</h4>
                        <a href="{item['link']}" target="_blank" style="color: #00ffcc;">📖 قراءة المزيد →</a>
                    </div>
                    """, unsafe_allow_html=True)
        except: pass

# ====================== شريط الأسعار المتحرك ======================
live_data = fetch_live_data(TICKER_POOL)
ticker_html = '<div class="ticker-wrapper"><div class="ticker-content">'
for item in live_data:
    color = "price-up" if item['change'] >= 0 else "price-down"
    arrow = "▲" if item['change'] >= 0 else "▼"
    ticker_html += f'<span class="ticker-item">{item["symbol"]} <span class="{color}">{item["price"]:.2f} ({arrow}{abs(item["change"]):.2f}%)</span></span>'
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)

st.markdown("""
<div class="terminal-footer">
    🕶️ BORSAJY PRO | تحليل فني • أساسي • كمي • ذكاء اصطناعي<br>
    📊 البيانات من Yahoo Finance | 🤖 Gemini AI | تحديث لحظي
</div>
""", unsafe_allow_html=True)
