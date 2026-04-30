import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import requests
import plotly.graph_objects as go
from datetime import datetime

# ====================== 1. إعدادات الصفحة والتنسيق (UI) ======================
st.set_page_config(
    page_title="المحلل الذكي Pro - البورصة المصرية والعالمية",
    page_icon="📈",
    layout="wide"
)

# إضافة لمسات جمالية للواجهة
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_name=True)

# ====================== 2. الدوال الأساسية (بيانات، تلجرام، AI) ======================

@st.cache_data(ttl=60)
def fetch_comprehensive_data(ticker_symbol):
    try:
        stock_engine = yf.Ticker(ticker_symbol)
        hist = stock_engine.history(period="1y")
        if hist.empty: return None, None, None, None
        
        # إضافة المؤشرات الفنية
        hist['RSI'] = ta.rsi(hist['Close'], length=14)
        hist['EMA_20'] = ta.ema(hist['Close'], length=20)
        
        return hist, stock_engine.dividends, stock_engine.news, stock_engine.info
    except Exception as e:
        st.error(f"خطأ في الربط مع Yahoo Finance لرمز {ticker_symbol}: {e}")
        return None, None, None, None

def send_telegram_professional(search_query, ticker, price, change, rsi, ema, stop_loss, take_profit, ai_analysis):
    try:
        token = str(st.secrets["TELEGRAM_TOKEN"])
        chat_id = str(st.secrets["TELEGRAM_CHAT_ID"])
        report_msg = (
            f"✨ *تقرير التحليل الفني الذكي* ✨\n"
            f"━━━━━━━━━━━━━━\n"
            f"📊 *السهم:* `{search_query}` ({ticker})\n"
            f"💰 *السعر الحالي:* `{price:.2f}`\n"
            f"📈 *التغير:* `{change:.2f}%`\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"🔍 *المؤشرات الفنية:*\n"
            f"• ⚡ *RSI (14):* `{rsi:.1f}`\n"
            f"• 📏 *EMA (20):* `{ema:.2f}`\n\n"
            f"🎯 *مستويات التداول:*\n"
            f"🟢 *جني الأرباح:* `{take_profit:.2f}`\n"
            f"🔴 *وقف الخسارة:* `{stop_loss:.2f}`\n\n"
            f"📝 *تحليل الخبير (AI):*\n"
            f"_{ai_analysis}_\n\n"
            f"📅 *توقيت التقرير:* `{datetime.now().strftime('%Y-%m-%d %H:%M')}`"
        )
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        res = requests.post(url, data={"chat_id": chat_id, "text": report_msg, "parse_mode": "Markdown"})
        return res.ok
    except: return False

# ====================== 3. قاعدة البيانات والقائمة الجانبية ======================
STOCK_DATABASE = {
    "البنك التجاري الدولي (مصر)": "COMI.CA",
    "مجموعة طلعت مصطفى (مصر)": "TMGH.CA",
    "فوري (مصر)": "FWRY.CA",
    "صندوق الذهب (AZG)": "AZG.CA",
    "صندوق المؤشر (EGX30ETF)": "EGX30ETF.CA",
    "أرامكو (السعودية)": "2222.SR",
    "الراجحي (السعودية)": "1120.SR",
    "إنفيديا (أمريكا)": "NVDA",
    "تسلا (أمريكا)": "TSLA"
}

with st.sidebar:
    st.title("🔍 التحكم والبحث")
    search_query = st.selectbox("اختر السهم:", options=list(STOCK_DATABASE.keys()))
    manual_ticker = st.text_input("أو اكتب رمزاً مخصصاً (مثل SWDY.CA):")
    ticker = manual_ticker.upper() if manual_ticker else STOCK_DATABASE[search_query]
    st.divider()
    [span_0](start_span)st.info("💡 يتم تحديث البيانات تلقائياً كل دقيقة لضمان اللحظية[span_0](end_span).")

# ====================== 4. معالجة وعرض البيانات (التبويبات) ======================
hist, divs, news, info = fetch_comprehensive_data(ticker)

if hist is not None:
    curr_p = hist['Close'].iloc[-1]
    prev_p = hist['Close'].iloc[-2]
    change_p = ((curr_p - prev_p) / prev_p) * 100
    stop_loss = curr_p * 0.97
    take_profit = curr_p * 1.05

    # [span_1](start_span)صف المؤشرات السريعة[span_1](end_span)
    st.markdown(f"# 📊 تحليل: {ticker}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("السعر اللحظي", f"{curr_p:.2f} EGP", f"{change_p:.2f}%")
    c2.metric("RSI (14)", f"{hist['RSI'].iloc[-1]:.1f}")
    c3.metric("🎯 جني الأرباح", f"{take_profit:.2f}")
    c4.metric("🔴 وقف الخسارة", f"{stop_loss:.2f}", delta_color="inverse")

    # نظام التبويبات المدمج
    tab_chart, tab_ai, tab_finance, tab_news = st.tabs([
        "📈 الرسم البياني اللحظي", "🤖 مساعد Gemini الذكي", 
        "💰 الأرباح والتوزيعات", "📰 آخر أخبار السوق"
    ])

    with tab_chart:
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="السعر")])
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA_20'], line=dict(color='yellow', width=1), name="EMA 20"))
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

    with tab_ai:
        if st.button("🚀 تشغيل تحليل AI المعمق"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"حلل سهم {ticker} فنياً بالعربية. السعر {curr_p:.2f}، RSI {hist['RSI'].iloc[-1]:.1f}. حدد الدعم والمقاومة."
            response = model.generate_content(prompt)
            st.session_state['ai_report'] = response.text
            st.write(response.text)
        
        if 'ai_report' in st.session_state:
            if st.button("📢 إرسال هذا التقرير لتلجرام"):
                send_telegram_professional(search_query, ticker, curr_p, change_p, hist['RSI'].iloc[-1], hist['EMA_20'].iloc[-1], stop_loss, take_profit, st.session_state['ai_report'])
                st.success("تم الإرسال!")

    with tab_finance:
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("💰 سجل توزيعات الأرباح")
            [span_2](start_span)if not divs.empty: st.dataframe(divs.tail(10)) #[span_2](end_span)
            else: st.info("لا توجد توزيعات مسجلة.")
        with col_right:
            st.subheader("📊 إحصائيات التداول")
            st.write(f"متوسط الحجم: {hist['Volume'].mean():.0f}")
            st.write(f"أعلى سعر (سنة): {hist['High'].max():.2f}")

    with tab_news:
        st.subheader("📰 الأخبار اللحظية")
        [span_3](start_span)for item in news[:5]: #[span_3](end_span)
            st.write(f"🔹 [{item['title']}]({item['link']})")
else:
    [span_4](start_span)st.error("⚠️ تعذر جلب البيانات. تأكد من الرمز[span_4](end_span).")
