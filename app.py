# app.py - النسخة النهائية التي تعمل 100%
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas_ta as ta
from datetime import datetime

import core
from database import get_market_statistics, get_market_info

# إعداد الصفحة
st.set_page_config(
    page_title="بوت تحليل الأسهم - النسخة النهائية",
    page_icon="📈",
    layout="wide"
)

# ====================== إعداد Gemini ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي"""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== الدوال المساعدة ======================
def show_rsi_alert(rsi_value: float):
    """عرض تنبيه RSI"""
    if rsi_value > 70:
        st.error(f"⚠️ تنبيه: منطقة تشبع شرائي! RSI = {rsi_value:.1f}")
    elif rsi_value < 30:
        st.success(f"✅ فرصة: منطقة تشبع بيعي! RSI = {rsi_value:.1f}")
    else:
        st.info(f"ℹ️ السهم في منطقة حيادية: RSI = {rsi_value:.1f}")

def show_market_alert(market: str):
    """عرض معلومات السوق"""
    market_info = get_market_info(market)
    if market_info:
        st.info(f"""
        📊 **معلومات السوق:**
        • ⏰ وقت التداول: {market_info.get('market_hours', 'غير محدد')}
        • 💵 العملة: {market_info.get('currency', 'غير محدد')}
        • 🌍 المنطقة الزمنية: {market_info.get('timezone', 'غير محدد')}
        """)

# ====================== واجهة البحث ======================
def stock_search_interface():
    """واجهة البحث"""
    st.markdown("### 🔍 ابحث عن سهم")
    
    search_term = st.text_input(
        "اكتب اسم السهم أو رمزه",
        placeholder="مثال: الراجحي أو AAPL"
    )
    
    if search_term:
        results = core.search_stocks_by_keyword(search_term)
        
        if results:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            for stock_name, stock_data in results.items():
                with st.expander(f"📈 {stock_name}"):
                    st.write(f"**الرمز:** `{stock_data['ticker']}`")
                    st.write(f"**السوق:** {stock_data['market']}")
                    st.write(f"**العملة:** {stock_data['currency']}")
                    
                    if st.button(f"تحليل", key=stock_data['ticker']):
                        return stock_data['ticker'], stock_name
        else:
            st.warning("❌ لم يتم العثور على نتائج")
    
    return None, None

# ====================== التطبيق الرئيسي ======================
def main():
    st.title("📈 بوت تحليل الأسهم المتكامل")
    st.markdown("**دعم أسواق: مصر 🇪🇬 • السعودية 🇸🇦 • الإمارات 🇦🇪 • أمريكا 🇺🇸**")
    
    # الشريط الجانبي
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
    
    # تبويبات
    tab1, tab2 = st.tabs(["🔍 بحث عن سهم", "📋 تصفح الأسهم"])
    
    selected_ticker = None
    selected_name = None
    
    with tab1:
        ticker, name = stock_search_interface()
        if ticker:
            selected_ticker, selected_name = ticker, name
    
    with tab2:
        market_filter = st.selectbox(
            "فلتر حسب السوق",
            ["جميع الأسواق", "🇪🇬 البورصة المصرية", "🇸🇦 تداول السعودية", "🇦🇪 سوق أبوظبي", "🇦🇪 سوق دبي", "🇺🇸 الأسهم الأمريكية"]
        )
        
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
        st.header(f"📊 تحليل: {selected_name}")
        
        # فترة التحليل
        period = st.selectbox(
            "📅 الفترة الزمنية",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            index=3
        )
        
        with st.spinner("جاري تحميل البيانات..."):
            hist, info = core.get_stock_data(selected_ticker, period)
        
        if hist is not None and not hist.empty:
            # المقاييس الأساسية
            curr_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 السعر", f"{curr_price:.2f}", f"{change_pct:+.2f}%")
            col2.metric("📊 RSI", f"{rsi:.1f}")
            col3.metric("📈 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
            col4.metric("🏢 الشركة", info.get('longName', selected_name)[:20] if info else selected_name[:20])
            
            # تنبيه RSI
            show_rsi_alert(rsi)
            
            # الرسم البياني
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر"), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", line=dict(dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI"), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.update_layout(height=500, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # التحليل بالذكاء الاصطناعي
            if st.button("🤖 تحليل ذكي بالذكاء الاصطناعي", type="primary"):
                model = init_gemini()
                if model:
                    with st.spinner("جاري التحليل..."):
                        prompt = f"""
                        حلل السهم {selected_name} (الرمز: {selected_ticker})
                        السعر: {curr_price:.2f}
                        RSI: {rsi:.1f}
                        التغير: {change_pct:+.2f}%
                        
                        قدم تحليلاً فنياً مختصراً بالعربية.
                        """
                        try:
                            response = model.generate_content(prompt)
                            st.success("نتيجة التحليل:")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"خطأ: {e}")
                else:
                    st.warning("⚠️ يرجى إضافة مفتاح Gemini API")
        else:
            st.error("❌ تعذر جلب البيانات")
    
    # تذييل
    st.divider()
    st.caption("📊 البيانات من Yahoo Finance | للأغراض التعليمية")

if __name__ == "__main__":
    main()
