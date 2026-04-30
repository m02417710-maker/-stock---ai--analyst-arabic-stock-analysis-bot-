import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import requests
import sqlite3
from pathlib import Path
from datetime import datetime

# ====================== 1. إعدادات الصفحة والتصميم الآمن ======================
st.set_page_config(
    page_title="المحلل المصري الذكي Pro",
    page_icon="📈",
    layout="wide"
)

# دالة التصميم باستخدام نظام محمي لتجنب أخطاء التنسيق
def apply_ui_design():
    style = """
    <style>
        /* التنسيق العام */
        .stApp { background-color: #0e1117; color: white; }
        
        /* تنسيق بطاقات المؤشرات */
        div[data-testid="stMetric"] {
            background-color: #1e222d !important;
            border: 1px solid #2a2e39 !important;
            padding: 15px !important;
            border-radius: 10px !important;
            text-align: center !important;
        }
        
        /* تنسيق التبويبات */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e222d;
            border-radius: 5px 5px 0 0;
            padding: 8px 20px;
            color: #d1d4dc;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2962ff !important;
            color: white !important;
        }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)

apply_ui_design()

# ====================== 2. الدوال التقنية (بيانات + قاعدة بيانات) ======================

@st.cache_data(ttl=900) # تخزين مؤقت لمدة 15 دقيقة لمنع الحظر
def get_stock_data(ticker):
    try:
        # استخدام Session لتقليل احتمالية الحظر
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        
        if df.empty: return None, None, None
        
        # حساب المؤشرات يدوياً (RSI & SMA)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df, stock.dividends, stock.news
    except:
        return None, None, None

def init_local_db():
    path = Path("data/app_db.db")
    path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute('CREATE TABLE IF NOT EXISTS portfolio (ticker TEXT, shares REAL, price REAL)')
    conn.commit()
    conn.close()

init_local_db()

# ====================== 3. القائمة الجانبية ======================
STOCKS_MAP = {
    "البنك التجاري الدولي": "COMI.CA",
    "طلعت مصطفى": "TMGH.CA",
    "فوري": "FWRY.CA",
    "أرامكو": "2222.SR",
    "آبل": "AAPL"
}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=100)
    st.title("لوحة التحكم")
    selected_name = st.selectbox("اختر السهم:", list(STOCKS_MAP.keys()))
    manual_ticker = st.text_input("أو اكتب الرمز مباشرة:")
    active_ticker = manual_ticker.upper() if manual_ticker else STOCKS_MAP[selected_name]
    
    st.divider()
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ====================== 4. العرض الرئيسي والتحليل ======================
st.header(f"📊 مراقبة سهم: {active_ticker}")

df, dividends, news = get_stock_data(active_ticker)

if df is not None:
    # 1. شريط الأرقام (Metrics)
    last_price = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    change = ((last_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر الحالي", f"{last_price:.2f}", f"{change:.2f}%")
    m2.metric("مؤشر RSI", f"{rsi_val:.1f}")
    m3.metric("المقاومة (5%)", f"{last_price * 1.05:.2f}")
    m4.metric("الدعم (5%)", f"{last_price * 0.95:.2f}", delta_color="inverse")

    # 2. التبويبات
    tab_chart, tab_ai, tab_finance = st.tabs(["📈 الرسم البياني", "🤖 تحليل AI", "💰 الأخبار والمالية"])

    with tab_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.03)
        # الشموع
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="السعر"), row=1, col=1)
        # المتوسط
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='#ff9800')), row=1, col=1)
        # الحجم
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="حجم التداول", marker_color='#2962ff'), row=2, col=1)
        
        fig.update_layout(template="plotly_dark", height=600, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tab_ai:
        st.subheader("تحليل خبير AI (Gemini)")
        if st.button("🚀 ابدأ التحليل المعمق"):
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("جاري التحليل..."):
                    prompt = f"حلل سهم {active_ticker} بالعربية. السعر {last_price:.2f} و RSI {rsi_val:.1f}. قدم نصيحة تداول."
                    resp = model.generate_content(prompt)
                    st.write(resp.text)
            else:
                st.error("Missing Gemini API Key in Secrets!")

    with tab_finance:
        col_news, col_divs = st.columns(2)
        with col_news:
            st.write("📰 آخر الأخبار")
            for item in news[:5]:
                st.markdown(f"🔹 [{item['title']}]({item['link']})")
        with col_divs:
            st.write("💰 التوزيعات")
            if not dividends.empty: st.dataframe(dividends.tail(10))
            else: st.info("لا توجد بيانات توزيعات متاحة.")
else:
    st.error("⚠️ فشل في جلب البيانات. يرجى الانتظار 15 دقيقة أو التحقق من الرمز.")
