import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import requests
from datetime import datetime

# ====================== 1. إعدادات الهوية البصرية (UI/UX) ======================
st.set_page_config(page_title="المحلل الذكي Pro", page_icon="📈", layout="wide")

def apply_styling():
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        [data-testid="stMetric"] {
            background-color: #1e222d !important;
            border: 1px solid #2a2e39 !important;
            padding: 15px !important;
            border-radius: 10px !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #d1d4dc;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2962ff !important;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_styling()

# ====================== 2. محرك جلب البيانات (مقاوم للحظر) ======================
@st.cache_data(ttl=900) # تخزين مؤقت لمدة 15 دقيقة لتجنب الحظر
def fetch_data_safe(ticker):
    try:
        # استخدام User-Agent لمحاكاة متصفح حقيقي وتجنب حظر ياهو
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        
        if df.empty: return None, None, None
        
        # حساب المؤشرات الفنية يدوياً لضمان الاستقرار
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df, stock.dividends, stock.news
    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب البيانات: {e}")
        return None, None, None

# ====================== 3. القائمة الجانبية والتحكم ======================
STOCKS_DB = {
    "البنك التجاري الدولي": "COMI.CA",
    "طلعت مصطفى": "TMGH.CA",
    "فوري": "FWRY.CA",
    "أرامكو": "2222.SR",
    "تسلا": "TSLA",
    "إنفيديا": "NVDA"
}

with st.sidebar:
    st.title("🏦 التحكم")
    choice = st.selectbox("اختر السهم المفضل:", list(STOCKS_DB.keys()))
    manual_input = st.text_input("أو اكتب رمز السهم مباشرة:")
    active_ticker = manual_input.upper() if manual_input else STOCKS_DB[choice]
    
    st.divider()
    if st.button("🔄 تحديث شامل للبيانات", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ====================== 4. المحتوى الرئيسي والتبويبات ======================
st.header(f"📊 تحليل سهم: {active_ticker}")

df, divs, news = fetch_data_safe(active_ticker)

if df is not None:
    # [span_0](start_span)عرض المؤشرات العلوية[span_0](end_span)
    curr_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    change = ((curr_price - prev_price) / prev_price) * 100
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("السعر الحالي", f"{curr_price:.2f}", f"{change:.2f}%")
    c2.metric("مؤشر RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
    c3.metric("هدف قريب (5%+)", f"{curr_price * 1.05:.2f}")
    c4.metric("وقف خسارة (3%-)", f"{curr_price * 0.97:.2f}", delta_color="inverse")

    # تقسيم المحتوى لتبويبات منظمة
    t_chart, t_ai, t_news = st.tabs(["📈 الرسم البياني", "🤖 تحليل AI", "📰 الأخبار والمالية"])

    with t_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='#ff9800')), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='#2962ff'), row=2, col=1)
        
        fig.update_layout(template="plotly_dark", height=600, margin=dict(t=10, b=10, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with t_ai:
        st.subheader("تحليل الذكاء الاصطناعي (Gemini)")
        if st.button("🚀 تشغيل تحليل معمق"):
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("جاري التحليل..."):
                    prompt = f"حلل سهم {active_ticker} بالعربية. السعر {curr_price:.2f}، RSI {df['RSI'].iloc[-1]:.1f}. قدم نصيحة تداول."
                    response = model.generate_content(prompt)
                    st.info(response.text)
            else:
                st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات Secrets.")

    with t_news:
        col_n, col_d = st.columns(2)
        with col_n:
            st.subheader("📰 آخر الأخبار")
            [span_1](start_span)for item in news[:5]: # عرض أول 5 أخبار[span_1](end_span)
                st.markdown(f"🔹 [{item['title']}]({item['link']})")
        with col_d:
            st.subheader("💰 التوزيعات النقدية")
            [span_2](start_span)if not divs.empty: st.dataframe(divs.tail(10), use_container_width=True) # عرض آخر 10 توزيعات[span_2](end_span)
            else: st.write("لا توجد بيانات توزيعات.")
else:
    st.error("❌ فشل جلب البيانات. يرجى الانتظار 15 دقيقة (بسبب قيود ياهو فاينانس) ثم حاول التحديث.")
