import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import requests
from datetime import datetime
import sqlite3
from pathlib import Path

# ====================== 1. إعدادات المنصة والتصميم ======================
st.set_page_config(page_title="المحلل المصري المتكامل Pro", page_icon="📈", layout="wide")

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
        }
        .stTabs [aria-selected="true"] { background-color: #2962ff !important; }
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== 2. محرك البيانات (حل مشكلة الحظر) ======================
@st.cache_data(ttl=900) # تحديث كل 15 دقيقة لتجنب حظر Yahoo Finance
def get_cleaned_data(ticker):
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        
        if df.empty: return None, None, None
        
        # حساب المؤشرات الفنية يدوياً (بدون مكتبات إضافية لضمان الاستقرار)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df, stock.dividends, stock.news
    except:
        return None, None, None

# ====================== 3. واجهة التحكم الجانبية ======================
STOCKS_DB = {
    "البنك التجاري الدولي": "COMI.CA",
    "طلعت مصطفى": "TMGH.CA",
    "فوري": "FWRY.CA",
    "أرامكو": "2222.SR",
    "إنفيديا": "NVDA",
    "تسلا": "TSLA"
}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=80)
    st.title("لوحة التحكم")
    selected_name = st.selectbox("اختر السهم:", list(STOCKS_DB.keys()))
    manual_ticker = st.text_input("أو أدخل الرمز مباشرة (مثلاً: AAPL):")
    ticker = manual_ticker.upper() if manual_ticker else STOCKS_DB[selected_name]
    
    st.divider()
    if st.button("🔄 تحديث البيانات الآن", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ====================== 4. العرض الرئيسي والتحليل ======================
st.header(f"📊 تحليل ومراقبة: {ticker}")

df, divs, news = get_cleaned_data(ticker)

if df is not None:
    # بطاقات الأداء اللحظي
    last_p = df['Close'].iloc[-1]
    prev_p = df['Close'].iloc[-2]
    change = ((last_p - prev_p) / prev_p) * 100
    rsi_val = df['RSI'].iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("السعر الحالي", f"{last_p:.2f}", f"{change:.2f}%")
    col2.metric("مؤشر RSI", f"{rsi_val:.1f}")
    col3.metric("هدف قريب (5%+)", f"{last_p * 1.05:.2f}")
    col4.metric("وقف خسارة (3%-)", f"{last_p * 0.97:.2f}", delta_color="inverse")

    # نظام التبويبات المُنظم
    t_chart, t_ai, t_extra = st.tabs(["📈 الرسم البياني", "🤖 مساعد Gemini", "📰 الأخبار والبيانات"])

    with t_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="السعر"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='#ff9800')), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم", marker_color='#2962ff'), row=2, col=1)
        fig.update_layout(template="plotly_dark", height=600, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with t_ai:
        st.subheader("التحليل الفني الذكي")
        if st.button("🚀 اطلب تحليل Gemini المعمق"):
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("جاري التحليل..."):
                    prompt = f"حلل سهم {ticker} بالعربية. السعر الحالي {last_p:.2f}، RSI {rsi_val:.1f}. اذكر الدعم والمقاومة."
                    response = model.generate_content(prompt)
                    st.info(response.text)
            else:
                st.warning("⚠️ يرجى إضافة مفتاح Gemini في إعدادات Secrets.")

    with t_extra:
        c_n, c_d = st.columns(2)
        with c_n:
            st.write("📰 آخر الأخبار")
            for item in news[:5]:
                st.markdown(f"🔹 [{item['title']}]({item['link']})")
        with c_d:
            st.write("💰 سجل التوزيعات")
            if not divs.empty: st.dataframe(divs.tail(10), use_container_width=True)
            else: st.info("لا توجد بيانات توزيعات.")
else:
    st.error("❌ فشل جلب البيانات. يرجى الانتظار 15 دقيقة (بسبب قيود Yahoo Finance) ثم حاول التحديث.")
