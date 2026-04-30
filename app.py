import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sqlite3
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ====================== 1. إعدادات المنصة ======================
st.set_page_config(
    page_title="المحلل المصري المتكامل Pro", 
    page_icon="📈", 
    layout="wide"
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
        }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e222d;
            border-radius: 5px 5px 0 0;
            color: #d1d4dc;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] { background-color: #2962ff !important; }
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== 2. محرك البيانات ======================
@st.cache_data(ttl=900, show_spinner=False)
def get_cleaned_data(ticker):
    """جلب البيانات من Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        if df.empty or len(df) < 10:
            return None, None, None, None
        
        # حساب المؤشرات الفنية
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
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
        
        # جلب بيانات إضافية
        try:
            dividends = stock.dividends
        except:
            dividends = pd.Series()
        
        try:
            info = stock.info
        except:
            info = {}
        
        news_items = []
        
        return df, dividends, news_items, info
        
    except Exception as e:
        return None, None, None, None

# ====================== 3. دوال التحليل ======================
def calculate_support_resistance(df):
    """حساب الدعم والمقاومة"""
    if len(df) < 30:
        return df['Low'].min(), df['High'].max()
    
    recent_low = df['Low'].iloc[-30:].min()
    recent_high = df['High'].iloc[-30:].max()
    
    return recent_low, recent_high

def get_trading_signal(df):
    """توليد إشارة تداول"""
    if df.empty or len(df) < 2:
        return "🟡 غير متوفر", [], 0
    
    last = df.iloc[-1]
    
    signals = []
    score = 0
    
    # RSI
    if last['RSI'] < 30:
        signals.append("🔴 منطقة ذروة بيع - فرصة شراء")
        score += 2
    elif last['RSI'] > 70:
        signals.append("🟡 منطقة ذروة شراء - توخ الحذر")
        score -= 1
    
    # MACD
    if last['MACD'] > last['Signal']:
        signals.append("📈 MACD إيجابي")
        score += 1
    else:
        signals.append("📉 MACD سلبي")
        score -= 1
    
    # السعر والمتوسطات
    if last['Close'] > last['SMA20']:
        signals.append("✅ السعر فوق المتوسط 20")
        score += 1
    else:
        signals.append("⚠️ السعر تحت المتوسط 20")
        score -= 1
    
    if score >= 2:
        recommendation = "🟢 شراء"
    elif score <= -1:
        recommendation = "🔴 بيع"
    else:
        recommendation = "🟡 انتظار"
    
    return recommendation, signals, score

# ====================== 4. قائمة الأسهم ======================
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

# ====================== 5. الواجهة الجانبية ======================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=60)
    st.title("المحلل المصري Pro")
    st.divider()
    
    selected_name = st.selectbox("اختر السهم:", list(STOCKS_DB.keys()))
    manual_ticker = st.text_input("أو أدخل الرمز:", placeholder="AAPL, TSLA, 2222.SR")
    
    ticker = manual_ticker.upper().strip() if manual_ticker else STOCKS_DB[selected_name]
    st.caption(f"الرمز: `{ticker}`")
    
    st.divider()
    
    show_advanced = st.checkbox("إظهار المؤشرات المتقدمة", value=True)
    
    if st.button("🔄 تحديث البيانات", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.caption(f"📊 Yahoo Finance")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# ====================== 6. العرض الرئيسي ======================
st.markdown(f"## 📊 تحليل ومراقبة: `{ticker}`")
st.markdown("---")

with st.spinner("🔄 جاري تحميل البيانات..."):
    df, divs, news, info = get_cleaned_data(ticker)

if df is not None and not df.empty:
    # ========== البطاقات ==========
    last_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else last_price
    price_change = ((last_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
    
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume'].mean()
    volume_ratio = (current_volume / avg_volume) * 100 if avg_volume != 0 else 100
    
    rsi_val = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
    support, resistance = calculate_support_resistance(df)
    recommendation, signals, signal_score = get_trading_signal(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 السعر الحالي", f"{last_price:.2f}", f"{price_change:+.2f}%")
    with col2:
        rsi_status = "ذروة شراء" if rsi_val > 70 else ("ذروة بيع" if rsi_val < 30 else "محايد")
        st.metric(f"📊 مؤشر RSI ({rsi_status})", f"{rsi_val:.1f}")
    with col3:
        st.metric("🎯 مقاومة / دعم", f"{resistance:.2f} / {support:.2f}")
    with col4:
        st.metric("📈 حجم التداول", f"{current_volume/1000000:.1f}M", f"{volume_ratio:.0f}%")
    
    st.markdown("---")
    
    # ========== التوصية ==========
    color_map = {"🟢 شراء": "#00ff00", "🔴 بيع": "#ff4444", "🟡 انتظار": "#ffaa00"}
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e222d 0%, #131722 100%); 
                padding: 15px; border-radius: 15px; margin: 10px 0; text-align: center;'>
        <h3 style='margin: 0; color: {color_map.get(recommendation, "#ffffff")}'>
            {recommendation}
        </h3>
        <p style='margin: 5px 0 0 0; opacity: 0.8;'>درجة الإشارة: {signal_score:.1f}/3</p>
    </div>
    """, unsafe_allow_html=True)
    
    if signals:
        with st.expander("📋 تفاصيل الإشارات الفنية", expanded=False):
            for s in signals:
                st.markdown(f"- {s}")
    
    # ========== التبويبات ==========
    tab1, tab2, tab3 = st.tabs(["📈 الرسم البياني", "📰 معلومات السهم", "💰 التوزيعات"])
    
    with tab1:
        if show_advanced:
            fig = make_subplots(
                rows=3, cols=1, 
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=("السعر والمتوسطات", "مؤشر RSI", "مؤشر MACD")
            )
            
            # السعر
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="السعر"
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA20'], name="SMA 20",
                line=dict(color='#ff9800', width=1.5)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA50'], name="SMA 50",
                line=dict(color='#4caf50', width=1.5)
            ), row=1, col=1)
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Upper'], name="BB علوي",
                line=dict(color='gray', dash='dash'), opacity=0.5
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Lower'], name="BB سفلي",
                line=dict(color='gray', dash='dash'), opacity=0.5,
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)'
            ), row=1, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI'], name="RSI",
                line=dict(color='#ff5722', width=2)
            ), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.add_hrect(y0=30, y1=70, fillcolor="green", opacity=0.1, row=2, col=1)
            
            # MACD
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_Hist'], name="MACD Hist",
                marker_color='#2962ff'
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD'], name="MACD",
                line=dict(color='#ff9800', width=2)
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Signal'], name="Signal",
                line=dict(color='#4caf50', width=2)
            ), row=3, col=1)
            
        else:
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True,
                row_heights=[0.7, 0.3],
                vertical_spacing=0.05
            )
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="السعر"
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA20'], name="SMA 20",
                line=dict(color='#ff9800')
            ), row=1, col=1)
            fig.add_trace(go.Bar(
                x=df.index, y=df['Volume'], name="الحجم",
                marker_color='#2962ff'
            ), row=2, col=1)
        
        fig.update_layout(
            template="plotly_dark",
            height=650,
            margin=dict(t=50, b=0, l=0, r=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(title_text="التاريخ", row=3 if show_advanced else 2, col=1)
        fig.update_yaxes(title_text="السعر", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1) if show_advanced else None
        
        # أضف key فريد لكل رسم بياني
st.plotly_chart(fig, use_container_width=True, key="unique_chart_01")
with tab2:
        st.subheader("ℹ️ معلومات الشركة")
        
        if info:
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**القطاع:** " + str(info.get('sector', 'غير متوفر')))
                st.markdown("**السوق:** " + str(info.get('market', 'غير متوفر')))
                st.markdown("**العملة:** " + str(info.get('currency', 'غير متوفر')))
            with cols[1]:
                if info.get('marketCap'):
                    st.markdown(f"**القيمة السوقية:** ${info.get('marketCap', 0):,}")
                if info.get('trailingPE'):
                    st.markdown(f"**نسبة السعر للربح:** {info.get('trailingPE', 'غير متوفر')}")
                if info.get('dividendYield'):
                    st.markdown(f"**عائد التوزيعات:** {info.get('dividendYield', 0)*100:.2f}%")
        else:
            st.info("لا توجد معلومات إضافية متاحة")
            
            st.markdown("""
            ### 💡 نصائح للمستثمر:
            - قم بتحليل المؤشرات الفنية قبل اتخاذ القرار
            - حدد نقاط الدخول والخروج مسبقاً
            - استخدم وقف الخسارة لحماية رأس المال
            - لا تستثمر أكثر مما تستطيع تحمل خسارته
            """)
with tab3:
        st.subheader("💰 توزيعات الأرباح")
        if not divs.empty:
            div_df = pd.DataFrame({
                'التاريخ': divs.index.strftime('%Y-%m-%d'),
                'قيمة التوزيع': divs.values
            })
            st.dataframe(div_df, use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي التوزيعات", f"{divs.sum():.2f}")
            with col2:
                st.metric("متوسط التوزيع", f"{divs.mean():.3f}")
            with col3:
                st.metric("عدد التوزيعات", len(divs))
        else:
            st.info("لا توجد بيانات توزيعات متاحة لهذا السهم")
        else:
    st.error("❌ فشل جلب البيانات")
    
    st.markdown("""
    ### 📋 الحلول المقترحة:
    
    1. **تأكد من صحة رمز السهم:**
       - للأسهم الأمريكية: استخدم الرمز فقط (AAPL, TSLA)
       - للأسهم السعودية: أضف .SR (2222.SR)
       - للأسهم المصرية: أضف .CA (COMI.CA)
    
    2. **انتظر 15 دقيقة:** قد يكون هناك حظر مؤقت من Yahoo Finance
    
    3. **جرب رمز آخر:** تأكد من أن السهم لا يزال مدرجاً في البورصة
    
    ---
    
    ### ✅ أمثلة لرموز صحيحة:
    - `AAPL` (آبل)
    - `TSLA` (تسلا)
    - `2222.SR` (أرامكو السعودية)
    - `COMI.CA` (البنك التجاري المصري)
    """)

# ====================== 7. تذييل الصفحة ======================
st.markdown("---")
st.caption("""
**تنويه مهم:** هذا التحليل لأغراض تعليمية فقط وليس توصية استثمارية.
يُنصح بالتشاور مع مستشار مالي قبل اتخاذ أي قرارات استثمارية.

البيانات مقدمة من Yahoo Finance | تحديث دوري كل 15 دقيقة
""")
