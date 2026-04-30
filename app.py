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

# ====================== 1. إعدادات التصميم الاحترافي (CSS) ======================
st.set_page_config(page_title="محلل مصر الذكي Pro", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* تغيير خلفية التطبيق */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* تنسيق بطاقات المؤشرات (Metrics) */
    [data-testid="stMetric"] {
        background-color: #1e222d;
        border: 1px solid #2a2e39;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    /* تحسين شكل التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0e1117;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e222d;
        border: 1px solid #2a2e39;
        border-radius: 8px 8px 0 0;
        padding: 10px 25px;
        color: #d1d4dc;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2962ff !important;
        color: white !important;
        border: none;
    }
    /* تنسيق القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #131722;
        border-left: 1px solid #2a2e39;
    }
    </style>
    """, unsafe_allow_name=True)

# ====================== 2. الدوال الذكية (بيانات، AI، قاعدة بيانات) ======================

@st.cache_data(ttl=900)
def fetch_data_safe(ticker):
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        if df.empty: return None, None, None
        
        # مؤشرات فنية ذاتية لضمان السرعة
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df, stock.dividends, stock.news
    except: return None, None, None

def init_db():
    db_path = Path("data/stock_pro.db")
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute('CREATE TABLE IF NOT EXISTS portfolio (ticker TEXT, shares REAL, price REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS favorites (ticker TEXT UNIQUE)')
    conn.commit()
    conn.close()

# ====================== 3. الواجهة الجانبية (Sidebar) ======================
init_db()
STOCKS_DICT = {"البنك التجاري الدولي": "COMI.CA", "طلعت مصطفى": "TMGH.CA", "فوري": "FWRY.CA", "السويدي": "SWDY.CA", "أرامكو": "2222.SR"}

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏦 لوحة التحكم</h2>", unsafe_allow_name=True)
    choice = st.selectbox("اختر السهم من القائمة:", list(STOCKS_DICT.keys()))
    manual_input = st.text_input("أو اكتب رمز السهم يدوياً:")
    ticker = manual_input.upper() if manual_input else STOCKS_DICT[choice]
    
    st.divider()
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ====================== 4. المحتوى الرئيسي والتبويبات ======================
st.markdown(f"<h1 style='color: #2962ff;'>📊 تحليل {ticker}</h1>", unsafe_allow_name=True)

df, divs, news = fetch_data_safe(ticker)

if df is not None:
    # شريط المؤشرات العلوية
    curr_p = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    change = ((curr_p - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("السعر الحالي", f"{curr_p:.2f}", f"{change:.2f}%")
    col2.metric("مؤشر RSI (14)", f"{rsi_val:.1f}")
    col3.metric("المقاومة المتوقعة", f"{curr_p * 1.05:.2f}")
    col4.metric("الدعم المتوقع", f"{curr_p * 0.95:.2f}", delta_color="inverse")

    # نظام التبويبات المطور
    tab_chart, tab_ai, tab_finance, tab_portfolio = st.tabs([
        "📈 الرسم البياني المتقدم", "🤖 تحليل الذكاء الاصطناعي", "💰 البيانات المالية", "💼 المحفظة"
    ])

    with tab_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        # الشموع اليابانية
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        # متوسط 20
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='#ff9800', width=1)), row=1, col=1)
        # حجم التداول
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='#2962ff', opacity=0.5), row=2, col=1)
        
        fig.update_layout(template="plotly_dark", height=600, showlegend=False, 
                          margin=dict(l=10, r=10, t=10, b=10),
                          plot_bgcolor='#131722', paper_bgcolor='#131722')
        st.plotly_chart(fig, use_container_width=True)

    with tab_ai:
        st.subheader("🤖 استشارة الخبير الذكي (Gemini AI)")
        if st.button("🚀 توليد تحليل معمق الآن"):
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("جاري تحليل البيانات..."):
                    prompt = f"حلل سهم {ticker} فنياً بالعربية. السعر {curr_p:.2f}، RSI {rsi_val:.1f}. حدد التوصية (شراء/بيع/انتظار)."
                    response = model.generate_content(prompt)
                    st.info(response.text)
            else:
                st.warning("⚠️ يرجى ضبط مفتاح API الخاص بـ Gemini في إعدادات Secrets.")

    with tab_finance:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💰 آخر التوزيعات")
            st.dataframe(divs.tail(5), use_container_width=True) if not divs.empty else st.write("لا توجد بيانات توزيعات.")
        with c2:
            st.subheader("📰 أخبار السوق")
            for item in news[:5]:
                st.markdown(f"🔹 [{item['title']}]({item['link']})")

    with tab_portfolio:
        st.subheader("💼 إدارة المحفظة")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            shares = st.number_input("عدد الأسهم المشتراة", min_value=1)
            buy_price = st.number_input("سعر الشراء الكلي", min_value=0.1)
            if st.button("حفظ في المحفظة الشخصية"):
                conn = sqlite3.connect("data/stock_pro.db")
                conn.execute('INSERT INTO portfolio VALUES (?,?,?)', (ticker, shares, buy_price))
                conn.commit()
                st.success("تم الحفظ بنجاح!")
        with p_col2:
            st.info("سيظهر ملخص أداء محفظتك هنا في التحديث القادم.")

else:
    st.error("⚠️ خطأ في جلب البيانات. قد يكون ذلك بسبب كثرة الطلبات (Rate Limit). يرجى المحاولة بعد 15 دقيقة.")
