import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import requests
import plotly.graph_objects as go
from datetime import datetime

# ====================== 1. إعدادات الصفحة والأمان ======================
st.set_page_config(
    page_title="المحلل الذكي Pro - البورصة المصرية والعالمية",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دالة التهيئة الذكية للموديل لضمان الاستقرار
def get_ai_model():
    if "GEMINI_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # محاولة تشغيل Flash أولاً ثم Pro كخطة بديلة
        for m_name in ["gemini-1.5-flash", "gemini-pro"]:
            try:
                m = genai.GenerativeModel(m_name)
                # اختبار اتصال سريع
                m.generate_content("ping", generation_config={"max_output_tokens": 1})
                return m
            except:
                continue
    except:
        return None
    return None

# دالة إرسال التلجرام بالتنسيق الاحترافي المحسن
def send_telegram_professional(search_query, ticker, price, change, rsi, ema, stop_loss, take_profit, ai_analysis):
    try:
        token = str(st.secrets["TELEGRAM_TOKEN"])
        chat_id = str(st.secrets["TELEGRAM_CHAT_ID"])
        
        # تنسيق الرسالة الاحترافي باستخدام Markdown
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
            f"📅 *توقيت التقرير:* `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"📢 *تنبيه:* هذا التحليل استرشادي فقط وليس توصية مباشرة."
        )
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": report_msg,
            "parse_mode": "Markdown"
        }
        res = requests.post(url, data=payload)
        return res.ok
    except Exception as e:
        st.error(f"خطأ في إرسال التلجرام: {e}")
        return False

# ====================== 2. قاعدة بيانات الأسهم (البحث الذكي) ======================
STOCK_DATABASE = {
    "أرامكو (السعودية)": "2222.SR",
    "الراجحي (السعودية)": "1120.SR",
    "البنك التجاري الدولي (مصر)": "COMI.CA",
    "مجموعة طلعت مصطفى (مصر)": "TMGH.CA",
    "فوري (مصر)": "FWRY.CA",
    "حديد عز (مصر)": "ESRS.CA",
    "أبو قير للأسمدة (مصر)": "ABUK.CA",
    "إي فاينانس (مصر)": "EFIH.CA",
    "النساجون الشرقيون (مصر)": "ORWE.CA",
    "مصر للألومنيوم (مصر)": "EGAL.CA",
    "سيدي كرير (مصر)": "SKPC.CA",
    "بالم هيلز (مصر)": "PHDC.CA",
    "آبل (أمريكا)": "AAPL",
    "تسلا (أمريكا)": "TSLA",
    "إنفيديا (أمريكا)": "NVDA"
}

# ====================== 3. معالجة البيانات ======================
@st.cache_data(ttl=300)
def fetch_stock_data(symbol):
    try:
        df = yf.Ticker(symbol).history(period="1y")
        if not df.empty:
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['EMA_20'] = ta.ema(df['Close'], length=20)
            return df
    except:
        return None
    return None

# ====================== 4. الواجهة الجانبية (Sidebar) ======================
with st.sidebar:
    st.title("🔍 البحث والتحكم")
    search_query = st.selectbox("ابحث عن اسم السهم:", options=list(STOCK_DATABASE.keys()))
    ticker = STOCK_DATABASE[search_query]
    
    st.divider()
    st.subheader("📰 آخر الأخبار")
    try:
        news = yf.Ticker(ticker).news[:3]
        for item in news:
            st.caption(f"📍 [{item['title']}]({item['link']})")
    except:
        st.write("لا توجد أخبار لحظية")

# ====================== 5. المحتوى الرئيسي والعرض ======================
st.markdown(f"# 📊 شاشة تحليل: {search_query}")

data = fetch_stock_data(ticker)

if data is not None:
    curr_p = data['Close'].iloc[-1]
    prev_p = data['Close'].iloc[-2]
    change_p = ((curr_p - prev_p) / prev_p) * 100
    
    # بطاقات المؤشرات اللحظية
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر الحالي", f"{curr_p:.2f}", f"{change_p:.2f}%")
    m2.metric("RSI (14)", f"{data['RSI'].iloc[-1]:.1f}")
    
    # حساب مؤشرات الخسارة والأرباح الآلية
    stop_loss = curr_p * 0.97 # 3% وقف خسارة
    take_profit = curr_p * 1.05 # 5% هدف أول
    m3.metric("🔴 وقف الخسارة", f"{stop_loss:.2f}", delta_color="inverse")
    m4.metric("🟢 جني الأرباح", f"{take_profit:.2f}")

    # الرسم البياني
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="السعر")])
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], line=dict(color='yellow', width=1), name="EMA 20"))
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # قائمة أفضل 10 أسهم
    with st.expander("⭐ قائمة أفضل 10 أسهم للمراقبة اليومية"):
        st.info("الأسهم الأكثر نشاطاً حالياً: COMI.CA, TMGH.CA, FWRY.CA, 2222.SR, 1120.SR, NVDA, TSLA, AAPL, ESRS.CA, ABUK.CA")

    # التحليل والذكاء الاصطناعي
    st.subheader("🧠 التحليل الفني بواسطة الذكاء الاصطناعي")
    if st.button("🚀 تشغيل تحليل Gemini المعمق"):
        model = get_ai_model()
        if model:
            with st.spinner("جاري التحليل..."):
                prompt = f"حلل سهم {search_query} ({ticker}) فنياً. السعر {curr_p:.2f}، RSI {data['RSI'].iloc[-1]:.1f}. اذكر الدعم والمقاومة واقتراح التداول بالعربية."
                response = model.generate_content(prompt)
                st.session_state['report_content'] = response.text
                st.markdown("---")
                st.markdown(response.text)
        else:
            st.error("❌ فشل الاتصال بالذكاء الاصطناعي.")

    # إرسال التقرير المنسق لتلجرام
    if 'report_content' in st.session_state:
        if st.button("📢 إرسال التقرير المنسق إلى تلجرام"):
            success = send_telegram_professional(
                search_query, ticker, curr_p, change_p, 
                data['RSI'].iloc[-1], data['EMA_20'].iloc[-1],
                stop_loss, take_profit, st.session_state['report_content']
            )
            if success:
                st.success("✅ تم إرسال التقرير بنجاح وبتنسيق احترافي!")
            else:
                st.error("❌ فشل الإرسال. تحقق من إعدادات البوت.")
else:
    st.error("⚠️ تعذر جلب بيانات السهم.")
