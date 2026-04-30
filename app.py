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

# ====================== 1. إعدادات الصفحة ======================
st.set_page_config(page_title="محلل مصر الذكي Pro", page_icon="📈", layout="wide")

# حل مشكلة الأقواس في CSS باستخدام دالة منفصلة لتجنب TypeError
def apply_custom_style():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        [data-testid="stMetric"] {
            background-color: #1e222d !important;
            border: 1px solid #2a2e39 !important;
            padding: 20px !important;
            border-radius: 12px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e222d;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            color: #d1d4dc;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2962ff !important;
        }
        </style>
    """, unsafe_allow_name=True)

apply_custom_style()

# ====================== 2. الدوال الأساسية ======================

@st.cache_data(ttl=900)
def fetch_data_safe(ticker):
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        if df.empty: return None, None, None
        
        # مؤشرات فنية
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df, stock.dividends, stock.news
    except:
        return None, None, None

# تهيئة قاعدة البيانات
def init_db():
    db_path = Path("data/stock_pro.db")
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute('CREATE TABLE IF NOT EXISTS portfolio (ticker TEXT, shares REAL, price REAL)')
    conn.commit()
    conn.close()

init_db()

# ====================== 3. الواجهة الجانبية ======================
STOCKS_DICT = {"البنك التجاري الدولي": "COMI.CA", "طلعت مستطفى": "TMGH.CA", "فوري": "FWRY.CA", "السويدي": "SWDY.CA"}

with st.sidebar:
    st.header("🏦 التحكم")
    choice = st.selectbox("اختر السهم:", list(STOCKS_DICT.keys()))
    manual = st.text_input("أو رمز يدوي (مثل AAPL):")
    ticker = manual.upper() if manual else STOCKS_DICT[choice]
    
    if st.button("🔄 تحديث"):
        st.cache_data.clear()
        st.rerun()

# ====================== 4. عرض البيانات والتحليل ======================
df, divs, news = fetch_data_safe(ticker)

if df is not None:
    curr_p = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    change = ((curr_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

    # عرض المؤشرات
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("السعر الحالي", f"{curr_p:.2f}", f"{change:.2f}%")
    c2.metric("RSI", f"{rsi_val:.1f}")
    c3.metric("هدف (5%)", f"{curr_p * 1.05:.2f}")
    c4.metric("وقف (3%)", f"{curr_p * 0.97:.2f}", delta_color="inverse")

    tab_chart, tab_ai = st.tabs(["📈 الرسم البياني", "🤖 تحليل الذكاء الاصطناعي"])

    with tab_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='#2962ff'), row=2, col=1)
        fig.update_layout(template="plotly_dark", height=500, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab_ai:
        if st.button("🚀 اطلب تحليل Gemini"):
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"حلل سهم {ticker} بسعر {curr_p} و RSI {rsi_val}")
                st.write(response.text)
            else:
                st.error("Missing Gemini API Key in Secrets!")
else:
    st.warning("⚠️ لا يمكن الوصول للبيانات حالياً. يرجى التأكد من الرمز أو المحاولة لاحقاً.")
