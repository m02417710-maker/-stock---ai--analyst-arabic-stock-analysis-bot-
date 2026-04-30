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

# ====================== 1. إعدادات الصفحة والأمان ======================
st.set_page_config(page_title="المحلل المصري Pro - نظام متكامل", page_icon="📈", layout="wide")

# حل مشكلة الحظر (Rate Limit) باستخدام Session و TTL مرتفع
@st.cache_data(ttl=900)
def fetch_data_pro(ticker):
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period="1y")
        if df.empty: return None, None, None
        
        # حساب المؤشرات يدوياً لضمان السرعة والدقة
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        # حساب RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df, stock.dividends, stock.news
    except:
        return None, None, None

# ====================== 2. إدارة قاعدة البيانات (المحفظة والتنبيهات) ======================
def init_db():
    db_path = Path("data/stock_pro.db")
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS portfolio (ticker TEXT, shares REAL, price REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS favorites (ticker TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS alerts (ticker TEXT, type TEXT, target REAL)')
    conn.commit()
    conn.close()

# ====================== 3. التكامل مع الذكاء الاصطناعي والتلجرام ======================
def get_ai_analysis(ticker, price, rsi):
    if "GEMINI_API_KEY" not in st.secrets: return "يرجى إضافة مفتاح Gemini في الإعدادات."
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"حلل سهم {ticker} فنياً بالعربية. السعر الحالي {price:.2f} ومؤشر RSI هو {rsi:.1f}. حدد نقاط الدعم والمقاومة بوضوح."
    try:
        return model.generate_content(prompt).text
    except: return "فشل الاتصال بمحرك الذكاء الاصطناعي."

def send_to_telegram(msg):
    if "TELEGRAM_TOKEN" in st.secrets:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

# ====================== 4. واجهة المستخدم الرئيسية ======================
init_db()
EGYPT_STOCKS = {"CIB": "COMI.CA", "طلعت مصطفى": "TMGH.CA", "فوري": "FWRY.CA", "السويدي": "SWDY.CA", "حديد عز": "ESRS.CA"}

with st.sidebar:
    st.title("🏦 التحكم الذكي")
    choice = st.selectbox("اختر السهم من القائمة:", list(EGYPT_STOCKS.keys()))
    manual = st.text_input("أو اكتب رمزاً مخصصاً:")
    ticker = manual.upper() if manual else EGYPT_STOCKS[choice]
    st.divider()
    if st.button("⭐ إضافة للمفضلة"):
        conn = sqlite3.connect("data/stock_pro.db"); conn.execute('INSERT OR IGNORE INTO favorites VALUES (?)', (ticker,)); conn.commit(); conn.close()
        st.success("تمت الإضافة!")

st.title(f"📈 منصة التحليل المتكاملة: {ticker}")

df, divs, news = fetch_data_pro(ticker)

if df is not None:
    curr_p = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    
    # صف المؤشرات اللحظية
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر الحالي", f"{curr_p:.2f}")
    m2.metric("مؤشر RSI", f"{rsi_val:.1f}")
    m3.metric("هدف جني الأرباح", f"{curr_p * 1.05:.2f}")
    m4.metric("وقف الخسارة", f"{curr_p * 0.97:.2f}", delta_color="inverse")

    # التبويبات المنظمة
    tab_chart, tab_ai, tab_portfolio, tab_news = st.tabs(["📈 الشارت المتقدم", "🤖 تحليل الذكاء الاصطناعي", "💰 المحفظة والتنبيهات", "📰 الأخبار"])

    with tab_chart:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="السعر"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name="SMA 20", line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="حجم التداول", marker_color='blue'), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab_ai:
        if st.button("🚀 تشغيل تحليل Gemini المعمق"):
            with st.spinner("جاري التفكير..."):
                report = get_ai_analysis(ticker, curr_p, rsi_val)
                st.markdown(report)
                if st.button("📢 إرسال هذا التحليل إلى تلجرام"):
                    send_to_telegram(f"تقرير {ticker}:\n{report}")
                    st.success("تم الإرسال!")

    with tab_portfolio:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("➕ إضافة صفقة")
            p_shares = st.number_input("عدد الأسهم", min_value=1)
            p_price = st.number_input("سعر الشراء", min_value=0.1)
            if st.button("حفظ في المحفظة"):
                conn = sqlite3.connect("data/stock_pro.db"); conn.execute('INSERT INTO portfolio VALUES (?,?,?)', (ticker, p_shares, p_price)); conn.commit(); conn.close()
                st.success("تم الحفظ!")
        with c2:
            st.subheader("🔔 ضبط تنبيه")
            a_target = st.number_input("تنبيه عند سعر:")
            if st.button("تفعيل التنبيه"):
                conn = sqlite3.connect("data/stock_pro.db"); conn.execute('INSERT INTO alerts VALUES (?,?,?)', (ticker, 'price', a_target)); conn.commit(); conn.close()
                st.info("سيعمل التنبيه عبر GitHub Actions")

    with tab_news:
        st.subheader("📰 الأخبار والتوزيعات")
        for n in news[:5]: st.write(f"🔹 [{n['title']}]({n['link']})")
        if not divs.empty: st.write("💰 آخر التوزيعات:"), st.dataframe(divs.tail(5))

else:
    st.error("❌ عذراً، فشل جلب البيانات. يرجى الانتظار 10 دقائق بسبب قيود سيرفرات Yahoo.")
