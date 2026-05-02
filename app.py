# app.py - التطبيق الرئيسي المصحح بالكامل
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
import sqlite3
import os

# إخفاء التحذيرات
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title="البورصجي AI - تحليل الأسهم",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استيراد الملفات المحلية
try:
    import core
    from database import MARKETS_DATA, get_stocks_count
except ImportError as e:
    st.error(f"خطأ في استيراد الملفات: {e}")
    st.stop()

# ========== العنوان ==========
st.title("📈 البورصجي AI - نظام تحليل الأسهم الذكي")
st.markdown("**البورصة المصرية 🇪🇬 | تداول السعودية 🇸🇦 | التحليل الفني + الذكاء الاصطناعي**")
st.divider()

# ========== الشريط الجانبي ==========
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    
    # عرض إحصائيات الأسهم
    st.markdown("### 📊 إحصائيات الأسواق")
    for market_key, market_data in MARKETS_DATA.items():
        count = len(market_data['stocks'])
        st.metric(market_data['label'], f"{count} سهماً")
    
    st.divider()
    
    # إعدادات API
    st.markdown("### 🔑 الإعدادات")
    api_key = st.text_input("مفتاح Gemini API", type="password", help="للتحليل بالذكاء الاصطناعي")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            st.success("✅ Gemini AI: متصل")
        except Exception as e:
            st.error(f"❌ خطأ: {e}")
    
    st.divider()
    
    # معلومات النظام
    st.markdown("### ℹ️ معلومات")
    st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption(f"عدد الأسهم: {core.get_total_count()}")

# ========== البحث والاختيار ==========
st.subheader("🔍 اختر السهم للتحليل")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    stock_names = core.get_all_stock_names()
    selected_name = st.selectbox("", stock_names)

with col2:
    period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

with col3:
    if st.button("🔄 تحديث", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if selected_name:
    ticker = core.get_ticker(selected_name)
    st.info(f"📌 **السهم:** {selected_name} | **الرمز:** `{ticker}`")
    
    # ========== جلب البيانات ==========
    @st.cache_data(ttl=300)
    def load_stock_data(ticker, period):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            info = stock.info
            return hist, info
        except Exception as e:
            return None, None
    
    with st.spinner("جاري تحميل البيانات..."):
        hist, info = load_stock_data(ticker, period)
    
    if hist is not None and not hist.empty:
        # حساب المؤشرات الفنية
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        
        # حساب RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # البيانات الحالية
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = ((current_price - prev_price) / prev_price) * 100
        current_rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
        current_sma20 = hist['SMA_20'].iloc[-1] if not pd.isna(hist['SMA_20'].iloc[-1]) else current_price
        
        # ========== عرض المقاييس ==========
        st.subheader("📊 المقاييس الأساسية")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 السعر الحالي", f"{current_price:.2f}", f"{change:+.2f}%")
        col2.metric("📈 RSI", f"{current_rsi:.1f}")
        col3.metric("📊 SMA 20", f"{current_sma20:.2f}")
        col4.metric("🏢 السوق", info.get('market', 'غير محدد')[:20])
        col5.metric("⏰ التحديث", datetime.now().strftime("%H:%M:%S"))
        
        # ========== تنبيه RSI ==========
        if current_rsi > 70:
            st.error("⚠️ **تنبيه: منطقة ذروة شراء!** مؤشر RSI فوق 70 يشير إلى احتمالية تصحيح.")
        elif current_rsi < 30:
            st.success("✅ **فرصة: منطقة ذروة بيع!** مؤشر RSI أقل من 30 قد يكون فرصة للشراء.")
        else:
            st.info(f"ℹ️ السهم في منطقة آمنة (RSI: {current_rsi:.1f})")
        
        # ========== الرسم البياني ==========
        st.subheader("📈 الرسم البياني الفني")
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=("السعر والمتوسطات المتحركة", "مؤشر RSI", "حجم التداول")
        )
        
        # خط السعر
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['Close'],
            name="السعر", line=dict(color='cyan', width=2)
        ), row=1, col=1)
        
        # SMA 20
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['SMA_20'],
            name="SMA 20", line=dict(color='orange', width=1.5, dash='dash')
        ), row=1, col=1)
        
        # SMA 50
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['SMA_50'],
            name="SMA 50", line=dict(color='yellow', width=1.5, dash='dot')
        ), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist['RSI'],
            name="RSI", line=dict(color='magenta', width=2)
        ), row=2, col=1)
        
        # خطوط RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     annotation_text="ذروة شراء", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     annotation_text="ذروة بيع", row=2, col=1)
        
        # حجم التداول
        colors = ['red' if hist['Close'].iloc[i] < hist['Open'].iloc[i] else 'green'
                 for i in range(len(hist))]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist['Volume'],
            name="الحجم", marker_color=colors, opacity=0.5
        ), row=3, col=1)
        
        # تنسيق الرسم
        fig.update_layout(
            height=700,
            template="plotly_dark",
            showlegend=True,
            title_text=f"تحليل {selected_name} ({ticker})"
        )
        
        fig.update_yaxes(title_text="السعر", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="الحجم", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ========== نقاط الدعم والمقاومة ==========
        st.subheader("📊 نقاط الدعم والمقاومة")
        
        # حساب الدعم والمقاومة من آخر 50 يوم
        recent_high = hist['High'].tail(50).max()
        recent_low = hist['Low'].tail(50).min()
        current = current_price
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🔼 المقاومة R1", f"{recent_high:.2f}")
        col2.metric("📍 السعر الحالي", f"{current:.2f}")
        col3.metric("🔽 الدعم S1", f"{recent_low:.2f}")
        
        # ========== التحليل بالذكاء الاصطناعي ==========
        st.subheader("🤖 التحليل الذكي بالذكاء الاصطناعي")
        
        if st.button("ابدأ التحليل الذكي", type="primary", use_container_width=True):
            if api_key:
                with st.spinner("جاري تحليل السوق بالذكاء الاصطناعي..."):
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        prompt = f"""
                        أنت محلل مالي محترف. حلل السهم التالي:
                        
                        السهم: {selected_name}
                        الرمز: {ticker}
                        السعر الحالي: {current_price:.2f}
                        التغير اليومي: {change:+.2f}%
                        مؤشر RSI: {current_rsi:.1f}
                        المتوسط المتحرك 20: {current_sma20:.2f}
                        
                        أجب بالعربية في نقاط:
                        1. تقييم الاتجاه العام
                        2. هل الوقت مناسب للشراء أو البيع؟
                        3. مستوى المخاطرة المتوقع
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.success("✅ نتيجة التحليل:")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"خطأ في التحليل: {e}")
            else:
                st.warning("⚠️ يرجى إدخال مفتاح Gemini API في الشريط الجانبي")
        
        # ========== معلومات إضافية ==========
        with st.expander("📋 معلومات إضافية عن الشركة"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")
                st.write(f"**الصناعة:** {info.get('industry', 'غير متوفر')}")
            with col2:
                st.write(f"**القيمة السوقية:** {info.get('marketCap', 'غير متوفر')}")
                st.write(f"**P/E Ratio:** {info.get('trailingPE', 'غير متوفر')}")
        
    else:
        st.error("❌ تعذر جلب البيانات. تأكد من اتصال الإنترنت وصحة رمز السهم")

# ========== إنشاء قاعدة البيانات إذا لم تكن موجودة ==========
def init_database():
    """تهيئة قاعدة البيانات"""
    conn = sqlite3.connect('boursagi.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            name TEXT,
            signal_type TEXT,
            rsi REAL,
            price REAL,
            risk_level TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_database()

# ========== التذييل ==========
st.divider()
st.caption("⚠️ **تنبيه:** البيانات مقدمة من Yahoo Finance | التحليل للاستخدام التعليمي فقط | استشر مستشاراً مالياً قبل اتخاذ قرارات الاستثمار")
