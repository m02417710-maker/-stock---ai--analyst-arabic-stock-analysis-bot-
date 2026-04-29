import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import requests
import plotly.graph_objects as go
from datetime import datetime

# ====================== 1. إعدادات الأمان والصفحة ======================
st.set_page_config(page_title="Stock Master AI", layout="wide")

# دالة التهيئة الذكية للموديل (تجنب خطأ 404)
def get_ai_model():
    if "GEMINI_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # محاولة تشغيل الأسرع ثم الأضمن
        for m_name in ["gemini-1.5-flash", "gemini-pro"]:
            try:
                m = genai.GenerativeModel(m_name)
                m.generate_content("ping", generation_config={"max_output_tokens": 1})
                return m
            except: continue
    except: return None
    return None

# دالة إرسال تلجرام المحمية
def safe_send_telegram(message):
    try:
        if "TELEGRAM_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            res = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
            return res.ok
    except: return False
    return False

# ====================== 2. واجهة المستخدم (Sidebar) ======================
with st.sidebar:
    st.header("⚡ التحكم السريع")
    ticker = st.text_input("رمز السهم (مثال: 2222.SR)", "2222.SR").upper()
    
    st.subheader("أسهم مقترحة")
    cols = st.columns(2)
    if cols[0].button("أرامكو"): ticker = "2222.SR"
    if cols[1].button("الراجحي"): ticker = "1120.SR"
    
    period = st.select_slider("فترة البيانات", options=["3mo", "6mo", "1y", "2y"], value="1y")

# ====================== 3. معالجة البيانات (Logic) ======================
@st.cache_data(ttl=3600) # تخزين مؤقت لمدة ساعة لسرعة الأداء
def fetch_data(symbol, prd):
    try:
        df = yf.Ticker(symbol).history(period=prd)
        if not df.empty:
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            return df
    except: return None
    return None

# ====================== 4. العرض الرئيسي ======================
st.title("🚀 محلل الأسهم الذكي V2")

data = fetch_data(ticker, period)

if data is not None:
    # عرض الأسعار الحالية
    last_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    change = last_price - prev_price
    
    col1, col2, col3 = st.columns(3)
    col1.metric("السعر الحالي", f"{last_price:.2f}", f"{change:.2f}")
    col2.metric("RSI (14)", f"{data['RSI'].iloc[-1]:.1f}")
    col3.metric("تحديث", datetime.now().strftime("%H:%M"))

    # الرسم البياني المحسن
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="السعر")])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], line=dict(color='orange', width=1), name="متوسط 20"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # التحليل الذكي
    if st.button("🔍 تشغيل تحليل الذكاء الاصطناعي"):
        model = get_ai_model()
        if model:
            with st.spinner("جاري قراءة الشارت..."):
                prompt = f"""حلل سهم {ticker} فنياً للعرب. 
                السعر: {last_price:.2f}. RSI: {data['RSI'].iloc[-1]:.1f}. 
                أعطِ نقاط الدعم والمقاومة وتوقع الاتجاه بنقاط مختصرة مع ايموجي."""
                
                try:
                    response = model.generate_content(prompt)
                    st.session_state['report'] = response.text
                    st.markdown("---")
                    st.markdown(f"### 📝 تقرير الخبير:\n{response.text}")
                except Exception as e:
                    st.error(f"عذراً، حدث خطأ في التحليل: {e}")
        else:
            st.error("الـ API Key غير صالح أو غير موجود في Secrets.")

    # إرسال تلجرام
    if 'report' in st.session_state:
        if st.button("📱 إرسال التقرير إلى تلجرام"):
            full_msg = f"📌 *تقرير سهم {ticker}*\n\n{st.session_state['report']}"
            if safe_send_telegram(full_msg):
                st.success("تم الإرسال!")
            else:
                st.error("فشل الإرسال. تحقق من التوكن و Chat ID.")

else:
    st.warning("الرجاء التأكد من رمز السهم بشكل صحيح.")
