import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import requests
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ====================== 1. إعدادات المنصة والتصميم ======================
st.set_page_config(
    page_title="المحلل المصري المتكامل Pro", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_style():
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        [data-testid="stMetric"] {
            background-color: #1e222d !important;
            border: 1px solid #2a2e39 !important;
            padding: 15px !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e222d;
            border-radius: 5px 5px 0 0;
            color: #d1d4dc;
            padding: 10px 20px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #2962ff !important;
            color: white !important;
        }
        div[data-testid="stAlert"] {
            border-radius: 10px;
            border-right: 4px solid #2962ff;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== 2. إعداد قاعدة البيانات ======================
def init_database():
    """تهيئة قاعدة البيانات لتخزين بيانات المستخدم"""
    db_path = Path("stock_analyzer.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # جدول لتفضيلات المستخدم
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                 (id INTEGER PRIMARY KEY, 
                  watchlist TEXT,
                  last_ticker TEXT,
                  notification_enabled BOOLEAN)''')
    
    # جدول للتنبيهات
    c.execute('''CREATE TABLE IF NOT EXISTS price_alerts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ticker TEXT,
                  target_price REAL,
                  alert_type TEXT,
                  created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_database()

# ====================== 3. محرك البيانات المحسن ======================
@st.cache_data(ttl=900, show_spinner=False)
def get_cleaned_data(ticker):
    """جلب البيانات مع معالجة الأخطاء بشكل احترافي"""
    try:
        # إعداد الجلسة مع User-Agent حقيقي
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        stock = yf.Ticker(ticker, session=session)
        
        # محاولة جلب البيانات مع إعادة المحاولة
        for attempt in range(3):
            try:
                df = stock.history(period="6mo", interval="1d")
                if not df.empty:
                    break
            except:
                if attempt == 2:
                    return None, None, None
                import time
                time.sleep(1)
        
        if df.empty or len(df) < 20:
            return None, None, None
        
        # حساب المؤشرات الفنية المحسنة
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['MA10'] = df['Close'].rolling(window=10).mean()
        
        # RSI محسن
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # حجم التداول المتوسط
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # جلب بيانات إضافية
        try:
            dividends = stock.dividends
            info = stock.info
        except:
            dividends = pd.Series()
            info = {}
        
        # جلب الأخبار (محاولة بديلة)
        news_items = []
        try:
            news = stock.news
            if news:
                news_items = news[:5]
        except:
            news_items = []
        
        return df, dividends, news_items, info
        
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return None, None, None, None

# ====================== 4. دوال إضافية للتحليل ======================
def calculate_support_resistance(df):
    """حساب مستويات الدعم والمقاومة"""
    if len(df) < 50:
        return None, None
    
    recent_highs = df['High'].rolling(window=20, center=True).max()
    recent_lows = df['Low'].rolling(window=20, center=True).min()
    
    resistance = recent_highs.iloc[-30:].mode()
    support = recent_lows.iloc[-30:].mode()
    
    return (support.iloc[0] if len(support) > 0 else df['Low'].min(),
            resistance.iloc[0] if len(resistance) > 0 else df['High'].max())

def get_trading_signal(df):
    """توليد إشارة تداول بناءً على المؤشرات"""
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = []
    score = 0
    
    # RSI
    if last['RSI'] < 30:
        signals.append("🔴 منطقة ذروة بيع - فرصة شراء محتملة")
        score += 2
    elif last['RSI'] > 70:
        signals.append("🟡 منطقة ذروة شراء - توخ الحذر")
        score -= 1
    
    # MACD
    if last['MACD'] > last['Signal'] and prev['MACD'] <= prev['Signal']:
        signals.append("📈 تقاطع MACD إيجابي - إشارة شراء")
        score += 2
    elif last['MACD'] < last['Signal'] and prev['MACD'] >= prev['Signal']:
        signals.append("📉 تقاطع MACD سلبي - إشارة بيع")
        score -= 1
    
    # السعر مقابل المتوسطات
    if last['Close'] > last['SMA20'] and last['Close'] > last['SMA50']:
        signals.append("✅ السعر أعلى من المتوسطات المتحركة - اتجاه صاعد")
        score += 1
    elif last['Close'] < last['SMA20'] and last['Close'] < last['SMA50']:
        signals.append("⚠️ السعر أقل من المتوسطات المتحركة - اتجاه هابط")
        score -= 1
    
    # Bollinger Bands
    if last['Close'] <= last['BB_Lower']:
        signals.append("📊 السعر عند الحد السفلي لبولينجر - ارتداد محتمل")
        score += 1
    elif last['Close'] >= last['BB_Upper']:
        signals.append("⚠️ السعر عند الحد العلوي لبولينجر - تصحيح محتمل")
        score -= 0.5
    
    # تحديد التوصية النهائية
    if score >= 2:
        recommendation = "🟢 **توصية: شراء** 🟢"
        color = "green"
    elif score <= -1:
        recommendation = "🔴 **توصية: بيع** 🔴"
        color = "red"
    else:
        recommendation = "🟡 **توصية: انتظار** 🟡"
        color = "yellow"
    
    return recommendation, signals, score

# ====================== 5. واجهة التحكم الجانبية المحسنة ======================
STOCKS_DB = {
    "البنك التجاري الدولي (مصر)": "COMI.CA",
    "طلعت مصطفى (مصر)": "TMGH.CA", 
    "فوري (مصر)": "FWRY.CA",
    "أرامكو (السعودية)": "2222.SR",
    "الراجحي (السعودية)": "1120.SR",
    "إنفيديا (أمريكا)": "NVDA",
    "تسلا (أمريكا)": "TSLA",
    "آبل (أمريكا)": "AAPL",
    "مايكروسوفت (أمريكا)": "MSFT"
}

with st.sidebar:
    # الشعار والترحيب
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=50)
    with col2:
        st.markdown("### المحلل المصري Pro")
    
    st.divider()
    
    # قسم اختيار السهم
    st.markdown("#### 🔍 اختيار السهم")
    selected_name = st.selectbox("من القائمة:", list(STOCKS_DB.keys()), key="stock_select")
    manual_ticker = st.text_input("أو أدخل رمز السهم:", placeholder="مثال: AAPL, TSLA, 2222.SR")
    
    ticker = manual_ticker.upper().strip() if manual_ticker else STOCKS_DB[selected_name]
    
    # عرض معلومات السهم
    st.caption(f"الرمز الحالي: `{ticker}`")
    
    st.divider()
    
    # إعدادات التحليل
    st.markdown("#### ⚙️ إعدادات التحليل")
    analysis_period = st.selectbox("فترة التحليل:", ["1mo", "3mo", "6mo", "1y"], index=2)
    show_advanced = st.checkbox("إظهار المؤشرات المتقدمة", value=True)
    
    st.divider()
    
    # أزرار التحكم
    if st.button("🔄 تحديث البيانات", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.success("✅ تم تحديث البيانات بنجاح!")
        st.rerun()
    
    st.markdown("---")
    st.caption("📊 البيانات من Yahoo Finance")
    st.caption(f"🕐 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")

# ====================== 6. العرض الرئيسي ======================
st.markdown(f"# 📊 تحليل ومراقبة: `{ticker}`")
st.markdown("---")

# جلب البيانات
with st.spinner("🔄 جاري تحميل البيانات..."):
    df, divs, news, info = get_cleaned_data(ticker)

if df is not None and not df.empty:
    # ========== بطاقات الأداء ==========
    last_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = ((last_price - prev_price) / prev_price) * 100
    
    # حساب الفترة الحالية والسابقة للحجم
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume'].mean()
    volume_ratio = (current_volume / avg_volume) * 100
    
    # الحصول على الإشارات
    recommendation, signals, signal_score = get_trading_signal(df)
    support, resistance = calculate_support_resistance(df)
    
    # عرض البطاقات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 السعر الحالي", 
            value=f"{last_price:.2f}", 
            delta=f"{price_change:+.2f}%",
            help="آخر سعر إغلاق"
        )
    
    with col2:
        rsi_val = df['RSI'].iloc[-1]
        rsi_status = "ذروة شراء" if rsi_val > 70 else ("ذروة بيع" if rsi_val < 30 else "محايد")
        st.metric(
            label=f"📊 مؤشر RSI ({rsi_status})", 
            value=f"{rsi_val:.1f}",
            delta=f"منذ يوم: {(rsi_val - df['RSI'].iloc[-2]):+.1f}"
        )
    
    with col3:
        if support and resistance:
            st.metric(
                label="🎯 مستويات رئيسية", 
                value=f"{resistance:.2f} / {support:.2f}",
                help="مقاومة / دعم"
            )
        else:
            st.metric("🎯 مستويات رئيسية", "قيد الحساب")
    
    with col4:
        st.metric(
            label="📈 حجم التداول", 
            value=f"{current_volume/1000000:.1f}M",
            delta=f"{volume_ratio:.0f}% من المتوسط"
        )
    
    st.markdown("---")
    
    # ========== التوصية ==========
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e222d 0%, #131722 100%); 
                padding: 20px; border-radius: 15px; margin: 15px 0; text-align: center;'>
        <h3 style='margin: 0; color: {'#00ff00' if 'شراء' in recommendation else '#ff4444' if 'بيع' in recommendation else '#ffff00'}'>
            {recommendation}
        </h3>
        <p style='margin: 10px 0 0 0; opacity: 0.8;'>درجة الإشارة: {signal_score:.1f}/3</p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض الإشارات
    if signals:
        with st.expander("📋 تفاصيل الإشارات الفنية", expanded=False):
            for signal in signals:
                st.markdown(f"- {signal}")
    
    # ========== التبويبات ==========
    tab1, tab2, tab3, tab4 = st.tabs(["📈 الرسم البياني", "🤖 مساعد الذكاء", "📰 الأخبار", "💰 التوزيعات"])
    
    with tab1:
        # رسم بياني متقدم
        if show_advanced:
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.15, 0.2, 0.15],
                subplot_titles=("السعر والمتوسطات", "RSI", "MACD", "حجم التداول")
            )
            
            # السعر والمتوسطات
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                         low=df['Low'], close=df['Close'], name="السعر"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", 
                                     line=dict(color='#ff9800', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name="SMA 50", 
                                     line=dict(color='#4caf50', width=1.5)), row=1, col=1)
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name="BB علوي", 
                                     line=dict(color='gray', dash='dash'), opacity=0.5), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name="BB سفلي", 
                                     line=dict(color='gray', dash='dash'), opacity=0.5, 
                                     fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)'), row=1, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", 
                                     line=dict(color='#ff5722', width=2)), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="green", opacity=0.1, row=2, col=1)
            
            # MACD
            fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name="MACD Hist", 
                                 marker_color='#2962ff'), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", 
                                     line=dict(color='#ff9800', width=2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name="Signal", 
                                     line=dict(color='#4caf50', width=2)), row=3, col=1)
            
            # الحجم
            colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                     for i in range(len(df))]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم", 
                                 marker_color=colors), row=4, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['Volume_MA'], name="Avg Volume", 
                                     line=dict(color='cyan', width=2)), row=4, col=1)
            
        else:
            # رسم بياني بسيط
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                row_heights=[0.7, 0.3], vertical_spacing=0.05)
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], 
                                         low=df['Low'], close=df['Close'], name="السعر"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", 
                                     line=dict(color='#ff9800')), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم", 
                                 marker_color='#2962ff'), row=2, col=1)
        
        fig.update_layout(
            template="plotly_dark",
            height=700,
            margin=dict(t=50, b=0, l=0, r=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_xaxes(title_text="التاريخ", row=4 if show_advanced else 2, col=1)
        fig.update_yaxes(title_text="السعر", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1) if show_advanced else None
        
        st.plotly_chart(fig, use_container_width=True)
        
        # معلومات إضافية
        with st.expander("ℹ️ معلومات السهم الأساسية"):
            if info:
                cols = st.columns(3)
                with cols[0]:
                    st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")
                    st.write(f"**سوق:** {info.get('market', 'غير متوفر')}")
                with cols[1]:
                    st.write(f"**القيمة السوقية:** ${info.get('marketCap', 'غير متوفر'):,}")
                    st.write(f"**نسبة السعر للربح:** {info.get('trailingPE', 'غير متوفر')}")
                with cols[2]:
                    st.write(f"**أعلى 52 أسبوع:** ${info.get('fiftyTwoWeekHigh', 'غير متوفر')}")
                    st.write(f"**أقل 52 أسبوع:** ${info.get('fiftyTwoWeekLow', 'غير متوفر')}")
    
    with tab2:
        st.subheader("🤖 تحليل الذكاء الاصطناعي")
        
        ai_model = st.radio("اختر نموذج الذكاء:", ["Gemini", "تحليل فني أساسي"], horizontal=True)
        
        if st.button("🔍 تشغيل التحليل الذكي", type="primary", use_container_width=True):
            if ai_model == "Gemini":
                if "GEMINI_API_KEY" in st.secrets:
                    try:
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        with st.spinner("✨ جاري تحليل Gemini..."):
                            prompt = f"""
                            قم بتحليل سهم {ticker} باللغة العربية بشكل احترافي:
                            
                            البيانات الحالية:
                            - السعر: {last_price:.2f}
                            - التغير: {price_change:+.2f}%
                            - RSI: {rsi_val:.1f}
                            - المتوسط 20 يوم: {df['SMA20'].iloc[-1]:.2f}
                            - المتوسط 50 يوم: {df['SMA50'].iloc[-1]:.2f}
                            
                            المطلوب:
                            1. تقييم الوضع الحالي
                            2. تحليل المؤشرات الفنية
                            3. مستويات الدعم والمقاومة المتوقعة
                            4. توصية وأهداف سعرية قريبة وبعيدة المدى
                            5. نقاط القوة والضعف
                            
                            قدم إجابة مفصلة ومهنية.
                            """
                            response = model.generate_content(prompt)
                            st.markdown(response.text)
                    except Exception as e:
                        st.error(f"خطأ في Gemini: {str(e)}")
                else:
                    st.warning("⚠️ مفتاح Gemini غير موجود. يرجى إضافته في Secrets.")
                    st.info("للحصول على مفتاح API، قم بزيارة: https://makersuite.google.com/app/apikey")
            
            else:
                # تحليل فني أساسي متقدم
                with st.spinner("📊 جاري التحليل الفني..."):
                    analysis = []
                    
                    # تحليل الاتجاه
                    sma20_trend = "صاعد" if df['SMA20'].iloc[-1] > df['SMA20'].iloc[-5] else "هابط"
                    sma50_trend = "صاعد" if df['SMA50'].iloc[-1] > df['SMA50'].iloc[-5] else "هابط"
                    
                    analysis.append(f"### 📈 تحليل الاتجاه العام")
                    analysis.append(f"- المتوسط المتحرك 20 يوم: اتجاه **{sma20_trend}**")
                    analysis.append(f"- المتوسط المتحرك 50 يوم: اتجاه **{sma50_trend}**")
                    
                    if df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
                        analysis.append("- ✅ السعر فوق المتوسطات المتحركة (اتجاه صاعد)")
                    else:
                        analysis.append("- ⚠️ السعر تحت المتوسطات المتحركة (اتجاه هابط)")
                    
                    # تحليل الزخم
                    analysis.append(f"\n### ⚡ تحليل الزخم")
                    analysis.append(f"- **RSI:** {rsi_val:.1f} - {'قوي جداً' if rsi_val > 70 else 'ضعيف' if rsi_val < 30 else 'متوسط'}")
                    
                    macd_trend = "إيجابي" if df['MACD'].iloc[-1] > df['Signal'].iloc[-1] else "سلبي"
                    analysis.append(f"- **MACD:** اتجاه {macd_trend}")
                    
                    # التوقعات والأهداف
                    analysis.append(f"\n### 🎯 التوقعات والأهداف")
                    if support and resistance:
                        analysis.append(f"- **الدعم الرئيسي:** {support:.2f}")
                        analysis.append(f"- **المقاومة الرئيسية:** {resistance:.2f}")
                    
                    # أهداف محتملة
                    target_up = last_price * 1.05
                    target_down = last_price * 0.95
                    analysis.append(f"- **هدف صاعد (5%):** {target_up:.2f}")
                    analysis.append(f"- **هدف نازل (5%):** {target_down:.2f}")
                    
                    # التوصية النهائية
                    analysis.append(f"\n### 💡 التوصية الختامية")
                    analysis.append(f"{recommendation}")
                    
                    st.markdown("\n".join(analysis))
    
    with tab3:
        st.subheader("📰 آخر الأخبار والتقارير")
        
        if news and len(news) > 0:
            for idx, item in enumerate(news):
                with st.container():
                    st.markdown(f"#### {idx+1}. {item.get('title', 'عنوان غير متوفر')}")
                    if 'publisher' in item:
                        st.caption(f"📌 المصدر: {item['publisher']}")
                    if 'link' in item:
                        st.markdown(f"[اقرأ المزيد]({item['link']})")
                    st.divider()
        else:
            st.info("لا توجد أخبار حديثة متاحة حالياً")
            
            # عرض تغذية بديلة للأسهم
            st.markdown("### 💡 نصائح تحليلية")
            st.markdown("""
            - **راقب المؤشرات الفنية** واستخدمها كدليل
            - **تابع أخبار السوق** بشكل عام للتأثير على السهم
            - **حدد أهداف واضحة** للدخول والخروج
            - **استخدم إدارة المخاطر** وحدد وقف الخسارة
            """)
    
    with tab4:
        st.subheader("💰 توزيعات الأرباح")
        
        if divs is not None and not divs.empty:
            # بيانات التوزيعات
            div_df = pd.DataFrame({
                'التاريخ': divs.index.strftime('%Y-%m-%d'),
                'قيمة التوزيع': divs.values
            })
            
            st.dataframe(div_df, use_container_width=True, hide_index=True)
            
            # رسم بياني للتوزيعات
            fig_div = go.Figure()
            fig_div.add_trace(go.Scatter(x=divs.index, y=divs.values, mode='lines+markers',
                                        name='التوزيعات', line=dict(color='#4caf50', width=2),
                                        marker=dict(size=8, color='#ff9800')))
            fig_div.update_layout(template="plotly_dark", height=400, 
                                 title="تاريخ توزيعات الأرباح",
                                 xaxis_title="التاريخ", yaxis_title="القيمة")
            st.plotly_chart(fig_div, use_container_width=True)
            
            # إحصائيات
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي التوزيعات", f"{divs.sum():.2f}")
            with col2:
                st.metric("متوسط التوزيع", f"{divs.mean():.3f}")
            with col3:
                st.metric("عدد التوزيعات", len(divs))
        else:
            st.info("لا توجد بيانات توزيعات متاحة لهذا السهم")
            
            # شرح للمستخدم
            st.markdown("""
            ### ℹ️ عن توزيعات الأرباح
            
            توزيعات الأرباح هي جزء من أرباح الشركة يتم توزيعها على المساهمين.
            
            **ملاحظات:**
            - قد لا تتوفر بيانات توزيعات لجميع الأسهم
            - الأسهم النامية قد لا توزع أرباحاً
            - الأسهم السعودية والمصرية قد تحتاج لرموز خاصة
            """)

else:
    # عرض رسالة خطأ مفصلة
    st.error("❌ فشل في جلب البيانات")
    
    st.markdown("""
    ### 💡 حلول مقترحة:
    
    1. **انتظر 15 دقيقة** - Yahoo Finance قد يحظر الطلبات المتكررة مؤقتاً
    2. **تحقق من رمز السهم** - تأكد من صحة الرمز
       - للأسهم السعودية: أضف `.SR` (مثال: `2222.SR`)
       - للأسهم المصرية: أضف `.CA` (مثال: `COMI.CA`)
       - للأسهم الأمريكية: استخدم الرمز فقط (مثال: `AAPL`)
    3. **حاول تحديث الصفحة** - استخدم زر التحديث في القائمة الجانبية
    4. **جرب رمز آخر** - قد يكون السهم غير متوفر حالياً
    
    ---
    
    ### ✅ أمثلة لرموز صحيحة:
    - `AAPL` (آبل)
    - `TSLA` (تسلا)
    - `2222.SR` (أرامكو السعودية)
    - `COMI.CA` (البنك التجاري المصري)
    """)

# ====================== 7. تذييل الصفحة ======================
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.caption("""
    ### 📊 المحلل المصري المتكامل Pro
    
    **تنويه مهم:** هذا التحليل لأغراض تعليمية فقط وليس توصية استثمارية.
    يُنصح بالتشاور مع مستشار مالي قبل اتخاذ أي قرارات استثمارية.
    
    البيانات مقدمة من Yahoo Finance | تحديث دوري كل 15 دقيقة
    """)
