# app.py - النسخة المعمارية المتكاملة
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# استيرادات جديدة
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

# استيراد من ملفاتنا
import core
from database import get_market_statistics, get_market_info

# إعداد الصفحة
st.set_page_config(
    page_title="Stock AI Analyst - Enterprise 🏢",
    page_icon="🏢",
    layout="wide"
)

# ====================== إعداد Gemini ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي"""
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel("gemini-1.5-flash")
    return None

# ====================== دوال التنبيهات ======================
def show_rsi_alert(rsi_value: float):
    """عرض تنبيه بناءً على قيمة RSI"""
    if rsi_value > 70:
        st.error("""
        ⚠️ **تنبيه: منطقة تشبع شرائي!**  
        مؤشر RSI فوق 70 يشير إلى أن السهم في منطقة ذروة شراء.  
        💡 قد يكون مناسباً لجني الأرباح أو الانتظار.
        """)
    elif rsi_value < 30:
        st.success("""
        ✅ **فرصة: منطقة تشبع بيعي!**  
        مؤشر RSI أقل من 30 يشير إلى أن السهم في منطقة ذروة بيع.  
        💡 قد تكون فرصة مناسبة للشراء.
        """)
    else:
        st.info(f"""
        ℹ️ **السهم في منطقة حيادية**  
        مؤشر RSI عند {rsi_value:.1f} - وهي منطقة آمنة نسبياً.
        """)

def show_market_alert(market: str):
    """عرض معلومات عن السوق"""
    market_info = get_market_info(market)
    if market_info:
        st.info(f"""
        📊 **معلومات السوق:**  
        • ⏰ وقت التداول: {market_info.get('market_hours', 'غير محدد')}  
        • 💵 العملة: {market_info.get('currency', 'غير محدد')}  
        • 🌍 المنطقة الزمنية: {market_info.get('timezone', 'غير محدد')}
        """)

# ====================== دالة البحث ======================
def stock_search_interface():
    """واجهة البحث المتقدم عن الأسهم"""
    st.markdown("### 🔍 ابحث عن سهم")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "اكتب اسم السهم أو رمزه",
            placeholder="مثال: الراجحي أو 1120.SR",
            help="يمكنك البحث باللغة العربية أو الإنجليزية"
        )
    
    if search_term:
        results = core.search_stocks_by_keyword(search_term)
        
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            # عرض النتائج
            for stock_name, stock_data in results.items():
                with st.expander(f"📈 {stock_name}"):
                    st.write(f"**الرمز:** `{stock_data['ticker']}`")
                    st.write(f"**السوق:** {stock_data['market']}")
                    st.write(f"**العملة:** {stock_data['currency']}")
                    
                    if st.button(f"تحليل {stock_name}", key=stock_data['ticker']):
                        return stock_data['ticker'], stock_name
        else:
            st.warning("❌ لم يتم العثور على نتائج. جرب كلمة بحث أخرى")
    
    return None, None

# ====================== الدالة الرئيسية ======================
def main():
    st.title("🏢 بوت تحليل الأسهم - النسخة المتكاملة")
    st.markdown("**دعم أسواق: مصر 🇪🇬 • السعودية 🇸🇦 • الإمارات 🇦🇪 • أمريكا 🇺🇸**")
    
    # عرض إحصائيات في الشريط الجانبي
    with st.sidebar:
        st.markdown("## 📊 إحصائيات الأسواق")
        stats = get_market_statistics()
        
        for market, data in stats.items():
            if market != 'TOTAL':
                st.metric(data['name'], data['count'])
        
        st.divider()
        st.metric("📈 إجمالي الأسهم", stats['TOTAL'])
        st.divider()
        
        # حالة الذكاء الاصطناعي
        model = init_gemini()
        if model:
            st.success("🤖 Gemini AI: متصل")
        else:
            st.warning("⚠️ أضف GEMINI_API_KEY في secrets")
    
    # تبويبين: بحث أو تصفح
    tab1, tab2 = st.tabs(["🔍 بحث عن سهم", "📋 تصفح جميع الأسهم"])
    
    selected_ticker = None
    selected_name = None
    
    with tab1:
        ticker, name = stock_search_interface()
        if ticker:
            selected_ticker = ticker
            selected_name = name
    
    with tab2:
        # تصنيف الأسهم حسب الأسواق
        market_filter = st.selectbox(
            "فلتر حسب السوق",
            ["جميع الأسواق", "🇪🇬 البورصة المصرية", "🇸🇦 تداول السعودية", "🇦🇪 سوق أبوظبي", "🇦🇪 سوق دبي", "🇺🇸 الأسهم الأمريكية"]
        )
        
        # فلتر الأسهم حسب الاختيار
        filtered_stocks = core.STOCK_NAMES
        if market_filter != "جميع الأسواق":
            filtered_stocks = [s for s in core.STOCK_NAMES if market_filter in s]
        
        selected_name = st.selectbox(
            "اختر سهم من القائمة",
            filtered_stocks,
            format_func=lambda x: f"{x} ({core.get_stock_ticker(x)})"
        )
        
        if selected_name:
            selected_ticker = core.get_stock_ticker(selected_name)
    
    # ====================== التحليل ======================
    if selected_ticker and selected_name:
        st.divider()
        st.header(f"📈 تحليل: {selected_name}")
        
        # معلومات السوق
        market = core.get_stock_market(selected_name)
        if market:
            show_market_alert(market)
        
        # فترة التحليل
        period = st.selectbox(
            "📅 الفترة الزمنية للتحليل",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            index=3
        )
        
        # جلب البيانات
        with st.spinner("جاري تحميل البيانات..."):
            try:
                stock = yf.Ticker(selected_ticker)
                hist = stock.history(period=period)
                
                if not hist.empty:
                    # المؤشرات الفنية
                    hist['SMA_20'] = ta.sma(hist['Close'], length=20)
                    hist['RSI'] = ta.rsi(hist['Close'], length=14)
                    
                    curr_price = hist['Close'].iloc[-1]
                    rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
                    
                    # عرض المقاييس
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("💰 السعر", f"{curr_price:.2f}")
                    col2.metric("📊 RSI", f"{rsi:.1f}")
                    col3.metric("🔄 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
                    col4.metric("🎯 السوق", market if market else "غير محدد")
                    
                    # تنبيه RSI
                    show_rsi_alert(rsi)
                    
                    # رسم بياني
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", line=dict(dash='dash')), row=1, col=1)
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI"), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    fig.update_layout(height=600, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # زر التحليل الذكي
                    if st.button("🤖 تحليل ذكي بالذكاء الاصطناعي", type="primary"):
                        model = init_gemini()
                        if model:
                            with st.spinner("جاري التحليل..."):
                                prompt = f"""
                                حلل السهم {selected_name} (الرمز: {selected_ticker})
                                السعر: {curr_price:.2f}
                                RSI: {rsi:.1f}
                                السوق: {market}
                                
                                قدم تحليلاً فنياً مختصراً بالعربية: الاتجاه، الدعم والمقاومة، التوصية.
                                """
                                response = model.generate_content(prompt)
                                st.success(response.text)
                        else:
                            st.error("الذكاء الاصطناعي غير متوفر - أضف مفتاح API")
                else:
                    st.error("لا توجد بيانات لهذا السهم")
                    
            except Exception as e:
                st.error(f"خطأ في جلب البيانات: {e}")
    
    # تذييل
    st.divider()
    st.caption("📊 البيانات من Yahoo Finance | 🧠 التحليل بـ Google Gemini | 🏗️ النسخة المتكاملة")

if __name__ == "__main__":
    main()
