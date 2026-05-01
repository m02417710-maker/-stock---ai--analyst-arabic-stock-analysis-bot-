# app.py - التطبيق الرئيسي النهائي
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة أولاً
st.set_page_config(
    page_title="Stock AI Analyst Pro - المؤسسي 🏢",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== التهيئة الأمنية ======================
from security import initialize_security, validate_ticker, get_safe_ticker
initialize_security()

# ====================== الاستيرادات ======================
from pathlib import Path
import tempfile
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas_ta as ta
from datetime import datetime
import io

# استيراد الوحدات الخاصة بنا
import core
from database import get_all_stocks, search_stock, MARKETS_DATA
from news_manager import render_news_section
from config import APP_VERSION

# ====================== إعداد Gemini ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        pass
    return None

# ====================== واجهة المستخدم ======================
def main():
    st.title("🏢 بوت تحليل الأسهم المتكامل")
    st.markdown(f"**الإصدار {APP_VERSION}** | دعم: مصر 🇪🇬 • السعودية 🇸🇦 • الإمارات 🇦🇪 • أمريكا 🇺🇸")
    st.markdown("---")
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 📊 لوحة التحكم")
        
        # إحصائيات الأسواق
        total_stocks = len(get_all_stocks())
        st.metric("📈 إجمالي الأسهم", total_stocks)
        
        # حالة الذكاء الاصطناعي
        model = init_gemini()
        if model:
            st.success("🤖 Gemini: متصل")
        else:
            st.warning("⚠️ أضف GEMINI_API_KEY")
        
        st.divider()
        
        # إعدادات إضافية
        st.markdown("### ⚙️ الإعدادات")
        debug_mode = st.checkbox("وضع التصحيح", value=False)
        if debug_mode:
            st.session_state.debug = True
    
    # التبويبات الرئيسية
    tabs = st.tabs(["📈 تحليل الأسهم", "📰 مركز الأخبار", "🔍 بحث متقدم", "ℹ️ عن التطبيق"])
    
    with tabs[0]:
        st.header("تحليل سهم فردي")
        
        # اختيار السهم
        search_term = st.text_input("🔍 ابحث عن سهم بالاسم أو الرمز", placeholder="مثال: CIB أو البنك التجاري")
        
        if search_term:
            results = search_stock(search_term)
            if results:
                st.success(f"تم العثور على {len(results)} نتيجة")
                selected = st.selectbox("اختر السهم", list(results.keys()))
                ticker = results[selected]['ticker']
                market = results[selected]['market']
                
                # جلب البيانات والتحليل
                with st.spinner("جاري تحليل السهم..."):
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period="1y")
                        
                        if not hist.empty:
                            # حساب المؤشرات
                            hist['RSI'] = ta.rsi(hist['Close'], length=14)
                            hist['SMA_20'] = ta.sma(hist['Close'], length=20)
                            
                            curr_price = hist['Close'].iloc[-1]
                            rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("💰 السعر", f"{curr_price:.2f}")
                            col2.metric("📊 RSI", f"{rsi:.1f}")
                            col3.metric("🏷️ السوق", market)
                            
                            # رسم بياني
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر"))
                            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", line=dict(dash='dash')))
                            fig.update_layout(template="plotly_dark", height=500)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # تحليل RSI
                            if rsi > 70:
                                st.error("⚠️ تنبيه: منطقة تشبع شرائي (RSI > 70)")
                            elif rsi < 30:
                                st.success("✅ فرصة: منطقة تشبع بيعي (RSI < 30)")
                            
                            # تحليل الذكاء الاصطناعي
                            if st.button("🤖 تحليل ذكي", type="primary") and model:
                                with st.spinner("جاري التحليل..."):
                                    prompt = f"حلل سهم {ticker} فنياً: السعر {curr_price:.2f}، RSI {rsi:.1f}"
                                    response = model.generate_content(prompt)
                                    st.write(response.text)
                    except Exception as e:
                        st.error(f"خطأ: {e}")
            else:
                st.warning("لم يتم العثور على نتائج")
    
    with tabs[1]:
        # عرض قسم الأخبار الكامل
        render_news_section()
    
    with tabs[2]:
        st.header("🔍 البحث المتقدم")
        st.info("""
        ### ميزات البحث:
        - البحث بالاسم العربي أو الإنجليزي
        - البحث بالرمز
        - تصفية حسب السوق
        - الحصول على معلومات مفصلة
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            market_filter = st.selectbox("فلتر بالسوق", ["الكل"] + list(MARKETS_DATA.keys()))
        with col2:
            keyword = st.text_input("كلمة البحث", placeholder="اسم الشركة أو الرمز")
        
        if keyword:
            results = search_stock(keyword)
            if market_filter != "الكل":
                results = {k: v for k, v in results.items() if v['market'] == market_filter}
            
            if results:
                st.dataframe(pd.DataFrame([{
                    "السهم": name,
                    "الرمز": data['ticker'],
                    "السوق": data['market'],
                    "العملة": data['currency']
                } for name, data in results.items()]), use_container_width=True)
    
    with tabs[3]:
        st.header("ℹ️ معلومات عن التطبيق")
        st.markdown(f"""
        ### 🏆 Stock AI Analyst Pro - الإصدار {APP_VERSION}
        
        **الميزات الرئيسية:**
        - ✅ دعم 5 أسواق مالية (مصر، السعودية، الإمارات، أمريكا)
        - ✅ أكثر من 100 سهم في قاعدة البيانات
        - ✅ تحليل فني متقدم (RSI, SMA, MACD)
        - ✅ نظام أمان متكامل ضد الاختراق
        - ✅ أخبار السوق العالمية والمحلية
        - ✅ تحليل بالذكاء الاصطناعي Gemini
        
        **المصادر:**
        - 📊 البيانات: Yahoo Finance API
        - 🧠 الذكاء الاصطناعي: Google Gemini
        - 📰 الأخبار: Yahoo Finance, Google News
        
        **التنصل:**
        هذا التطبيق للأغراض التعليمية فقط. لا يقدم نصائح استثمارية.
        
        **عن أخبار ثاندر (Thndr):**
        تطبيق ثاندر هو منصة وساطة مالية مصرية مرخصة هيئة الرقابة المالية.
        للحصول على أخبار ثاندر الرسمية، يُرجى تحميل التطبيق من المتجر الرسمي.
        
        ---
        **مطور التطبيق:** Stock AI Analyst Team
        **آخر تحديث:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
        """)

if __name__ == "__main__":
    main()
