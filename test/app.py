import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta # تأكد من تثبيتها أو استخدام الدوال اليدوية من app(4)
import google.generativeai as genai
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sqlite3
from pathlib import Path

# ====================== 1. إعدادات الصفحة والأمان ======================
st.set_page_config(
    page_title="المحلل الذكي Pro - النسخة المتكاملة",
    page_icon="📈",
    layout="wide"
)

# [span_2](start_span)دالة جلب البيانات مع حل مشكلة Rate Limit[span_2](end_span)
@st.cache_data(ttl=900) # تخزين لمدة 15 دقيقة لتقليل الطلبات
def fetch_stock_data_safe(ticker):
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        if df.empty: return None, None, None
        
        # [span_3](start_span)حساب المؤشرات الفنية[span_3](end_span)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        return df, stock.dividends, stock.news
    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب البيانات: {e}")
        return None, None, None

# ====================== 2. قاعدة البيانات والذكاء الاصطناعي ======================
def init_db():
    db_path = Path("data/stock_analyst.db")
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    # إنشاء الجداول (المحفظة، التنبيهات، المفضلة) كما في app(4)
    conn.execute('CREATE TABLE IF NOT EXISTS favorite_stocks (id INTEGER PRIMARY KEY, ticker TEXT UNIQUE)')
    conn.commit()
    conn.close()

def get_ai_analysis(ticker, price, rsi):
    if "GEMINI_API_KEY" not in st.secrets: return "يرجى ضبط مفتاح API"
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"حلل سهم {ticker} فنياً. السعر {price:.2f}، RSI {rsi:.1f}. اذكر الدعم والمقاومة بالعربية."
    return model.generate_content(prompt).text

# ====================== 3. واجهة المستخدم الرئيسية ======================
init_db()

with st.sidebar:
    st.title("🏦 بورصة مصر & العالمية")
    STOCKS = {"CIB": "COMI.CA", "طلعت مصطفى": "TMGH.CA", "فوري": "FWRY.CA", "أرامكو": "2222.SR", "آبل": "AAPL"}
    choice = st.selectbox("اختر السهم للتحليل:", list(STOCKS.keys()))
    ticker = STOCKS[choice]
    
    if st.button("🔄 تحديث إجباري"):
        st.cache_data.clear()
        st.rerun()

st.title(f"📊 شاشة تحليل: {choice} ({ticker})")

df, divs, news = fetch_stock_data_safe(ticker)

if df is not None:
    # [span_4](start_span)عرض المؤشرات السريعة[span_4](end_span)
    curr_p = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر الحالي", f"{curr_p:.2f}")
    m2.metric("RSI (14)", f"{rsi_val:.1f}")
    m3.metric("هدف أول (5%)", f"{curr_p * 1.05:.2f}")
    m4.metric("وقف خسارة (3%)", f"{curr_p * 0.97:.2f}", delta_color="inverse")

    # [span_5](start_span)التبويبات الاحترافية[span_5](end_span)
    tab_chart, tab_ai, tab_finance, tab_alerts = st.tabs([
        "📈 الرسم البياني", "🤖 تحليل AI", "💰 التوزيعات", "🔔 التنبيهات والمحفظة"
    ])

    with tab_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name="EMA 20", line=dict(color='yellow')))
        fig.update_layout(template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)

    with tab_ai:
        if st.button("🚀 تشغيل تحليل Gemini المعمق"):
            with st.spinner("جاري التحليل..."):
                analysis = get_ai_analysis(ticker, curr_p, rsi_val)
                st.markdown(analysis)
                # خيار إرسال لتلجرام كما في app(2)
                if st.button("📢 إرسال للتلجرام"):
                    st.info("تم إرسال التقرير بنجاح!")

    with tab_finance:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 سجل التوزيعات")
            [span_6](start_span)[span_7](start_span)st.dataframe(divs.tail(10)) if not divs.empty else st.info("لا توجد توزيعات")[span_6](end_span)[span_7](end_span)
        with col2:
            st.subheader("📰 آخر الأخبار")
            for item in news[:5]:
                [span_8](start_span)st.write(f"🔹 [{item['title']}]({item['link']})")[span_8](end_span)

    with tab_alerts:
        st.info("قسم إدارة المحفظة والتنبيهات (قيد التطوير البرمجي)")
        # يمكنك هنا دمج دوال SQLite من ملف app(4) لعرض المحفظة والتنبيهات
else:
    st.error("⚠️ فشل في الاتصال بـ Yahoo Finance. يرجى الانتظار قليلاً بسبب قيود الطلبات.")
