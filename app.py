# app.py - النسخة النهائية المصححة
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas_ta as ta
from datetime import datetime
import random

from database import (
    get_all_egyptian_stocks, 
    get_stocks_by_sector, 
    get_all_sectors,
    search_stock,
    get_market_statistics,
    get_market_info,
    EGYPTIAN_STOCKS
)

# استيراد وحدات البحث
from search_utils import (
    search_google, 
    search_stock_news, 
    search_market_news,
    search_commodity_news,
    smart_search,
    analyze_news_with_gemini
)

# إعداد الصفحة
st.set_page_config(
    page_title="تحليل البورصة المصرية - المنصة المتكاملة",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ====================== تهيئة حالة الجلسة ======================
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = None
if 'refresh_market_news' not in st.session_state:
    st.session_state.refresh_market_news = True
if 'search_stock_news' not in st.session_state:
    st.session_state.search_stock_news = None
if 'button_counter' not in st.session_state:
    st.session_state.button_counter = 0

def get_unique_button_id():
    """توليد معرف فريد لكل زر"""
    st.session_state.button_counter += 1
    return f"btn_{st.session_state.button_counter}_{random.randint(10000, 99999)}"

# ====================== CSS للتنسيق ======================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 14px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px 0;
        text-align: left;
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #444;
        color: white;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2a2a3e, #3a3a4e);
        transform: translateY(-2px);
        border-color: #ff4b4b;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ====================== إعداد Gemini ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي"""
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            return None
        
        api_key = st.secrets["GEMINI_API_KEY"]
        
        if not api_key or api_key == "your_gemini_api_key_here":
            return None
        
        genai.configure(api_key=api_key)
        
        models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                test_response = model.generate_content("Test")
                if test_response:
                    return model
            except:
                continue
        
        return None
            
    except Exception as e:
        return None

def basic_technical_analysis(rsi: float, change_pct: float, price: float, name: str):
    """تحليل فني أساسي بدون API"""
    
    analysis = []
    
    if rsi > 70:
        analysis.append(f"🔴 تحليل RSI: السهم في منطقة ذروة شراء ({rsi:.1f}) - احتمال تصحيح سعري")
    elif rsi < 30:
        analysis.append(f"🟢 تحليل RSI: السهم في منطقة ذروة بيع ({rsi:.1f}) - فرصة شراء محتملة")
    else:
        analysis.append(f"🟡 تحليل RSI: السهم في منطقة حيادية ({rsi:.1f})")
    
    if change_pct > 2:
        analysis.append(f"📈 ارتفاع قوي بنسبة {change_pct:.2f}%")
    elif change_pct < -2:
        analysis.append(f"📉 انخفاض قوي بنسبة {change_pct:.2f}%")
    else:
        analysis.append(f"➡️ حركة جانبية بنسبة {change_pct:.2f}%")
    
    analysis.append(f"💰 السعر الحالي: {price:.2f} جنيه مصري")
    
    analysis.append("\n📋 التوصية:")
    if rsi < 35:
        analysis.append("✅ فرصة شراء مناسبة")
    elif rsi > 65:
        analysis.append("⚠️ تجنب الشراء حالياً - انتظر تصحيحاً")
    else:
        analysis.append("⏸ مراقبة السهم - انتظر إشارة أوضح")
    
    return "\n".join(analysis)

def get_gemini_analysis(stock_name: str, stock_ticker: str, curr_price: float, rsi: float, change_pct: float):
    """الحصول على تحليل من Gemini API"""
    model = init_gemini()
    if model:
        try:
            prompt = f"""
            حلل السهم التالي في البورصة المصرية:
            
            السهم: {stock_name}
            الرمز: {stock_ticker}
            السعر: {curr_price:.2f} جنيه
            RSI: {rsi:.1f}
            التغير: {change_pct:+.2f}%
            
            قدم تحليلاً مختصراً بالعربية مع توصية.
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return None
    return None

# ====================== دوال التحليل ======================
@st.cache_data(ttl=300)
def get_stock_data(ticker: str, period: str = "1y"):
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return None, None
        
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['EMA_9'] = ta.ema(df['Close'], length=9)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        return df, stock.info
    except Exception as e:
        return None, None

@st.cache_data(ttl=300)
def get_stock_signal(ticker: str):
    """الحصول على إشارة السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        if df.empty or len(df) < 14:
            return "neutral", 50, 0, df['Close'].iloc[-1] if not df.empty else 0
        
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        
        if rsi < 30:
            return "buy", rsi, change_pct, current_price
        elif rsi > 70:
            return "sell", rsi, change_pct, current_price
        else:
            return "neutral", rsi, change_pct, current_price
    except:
        return "neutral", 50, 0, 0

def show_rsi_alert(rsi_value: float):
    """عرض تنبيه RSI"""
    if rsi_value > 70:
        st.error(f"⚠️ تنبيه: منطقة تشبع شرائي! RSI = {rsi_value:.1f}")
    elif rsi_value < 30:
        st.success(f"✅ فرصة: منطقة تشبع بيعي! RSI = {rsi_value:.1f}")
    else:
        st.info(f"ℹ️ السهم في منطقة حيادية - RSI = {rsi_value:.1f}")

def select_stock(ticker: str, name: str):
    """اختيار السهم"""
    st.session_state.selected_ticker = ticker
    st.session_state.selected_name = name
    st.rerun()

def clear_selection():
    """مسح الاختيار"""
    st.session_state.selected_ticker = None
    st.session_state.selected_name = None
    st.rerun()

# ====================== عرض التحليل الفني ======================
def display_technical_analysis():
    """عرض التحليل الفني"""
    
    if st.session_state.selected_ticker is None:
        return False
    
    st.markdown("---")
    st.header(f"📈 التحليل الفني: {st.session_state.selected_name}")
    st.caption(f"الرمز: {st.session_state.selected_ticker} | السوق: البورصة المصرية")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        period = st.selectbox("الفترة الزمنية", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    with col2:
        auto_analyze = st.checkbox("تحليل تلقائي", value=False)
    with col3:
        if st.button("مسح والعودة"):
            clear_selection()
    
    with st.spinner("جاري تحميل البيانات..."):
        hist, info = get_stock_data(st.session_state.selected_ticker, period)
    
    if hist is not None and not hist.empty:
        curr_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
        change_pct = ((curr_price - prev_price) / prev_price) * 100 if prev_price != 0 else 0
        rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("السعر الحالي", f"{curr_price:.2f} ج.م", f"{change_pct:+.2f}%")
        col2.metric("مؤشر RSI", f"{rsi:.1f}")
        col3.metric("SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
        col4.metric("حجم التداول", f"{hist['Volume'].iloc[-1]:,.0f}")
        
        show_rsi_alert(rsi)
        
        # رسم بياني
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="السعر", line=dict(color='cyan', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name="SMA 20", line=dict(dash='dash', color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI", line=dict(color='magenta')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.update_layout(height=500, template="plotly_dark")
        fig.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # التحليل
        if auto_analyze or st.button("تحليل ذكي", type="primary"):
            with st.spinner("جاري التحليل..."):
                gemini_analysis = get_gemini_analysis(
                    st.session_state.selected_name,
                    st.session_state.selected_ticker,
                    curr_price, rsi, change_pct
                )
                
                if gemini_analysis:
                    st.success(gemini_analysis)
                else:
                    basic_analysis = basic_technical_analysis(rsi, change_pct, curr_price, st.session_state.selected_name)
                    st.info(basic_analysis)
        
        return True
    else:
        st.error("تعذر جلب بيانات السهم")
        return True

# ====================== عرض زر السهم ======================
def display_stock_card(name: str, ticker: str, signal_data: tuple, unique_id: int = 0):
    """عرض زر سهم"""
    
    signal, rsi, change_pct, price = signal_data
    
    if signal == "buy":
        emoji = "🟢"
        signal_text = "شراء"
    elif signal == "sell":
        emoji = "🔴"
        signal_text = "بيع"
    else:
        emoji = "🟡"
        signal_text = "مراقبة"
    
    change_symbol = "▲" if change_pct >= 0 else "▼"
    button_text = f"{emoji} {name[:40]} | سعر:{price:.2f} | {change_symbol}{abs(change_pct):.1f}% | RSI:{rsi:.0f} | {signal_text}"
    
    if st.button(button_text, key=f"btn_{ticker}_{unique_id}", use_container_width=True):
        select_stock(ticker, name)

# ====================== الدالة الرئيسية ======================
def main():
    """التطبيق الرئيسي"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🇪🇬 منصة تحليل البورصة المصرية</h1>
        <p>تحليل فني | إشارات شراء/بيع | أخبار فورية</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_market_statistics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الأسهم", stats['total_stocks'])
    col2.metric("عدد القطاعات", stats['sectors'])
    col3.metric("العملة", stats['currency'])
    col4.metric("وقت التداول", stats['trading_hours'])
    
    st.markdown("---")
    
    if st.session_state.selected_ticker is not None:
        display_technical_analysis()
    else:
        st.markdown("### 📋 أسهم البورصة المصرية")
        
        all_stocks = get_all_egyptian_stocks()
        
        buy_list = []
        sell_list = []
        neutral_list = []
        
        with st.spinner("جاري تحليل الأسهم..."):
            for name, ticker in list(all_stocks.items())[:50]:
                signal_data = get_stock_signal(ticker)
                signal = signal_data[0]
                
                if signal == "buy":
                    buy_list.append((name, ticker, signal_data))
                elif signal == "sell":
                    sell_list.append((name, ticker, signal_data))
                else:
                    neutral_list.append((name, ticker, signal_data))
        
        if sell_list:
            st.markdown("## 🔴 أسهم يوصى ببيعها")
            for idx, (name, ticker, sig_data) in enumerate(sell_list):
                display_stock_card(name, ticker, sig_data, idx)
        
        if buy_list:
            st.markdown("## 🟢 أسهم يوصى بشرائها")
            for idx, (name, ticker, sig_data) in enumerate(buy_list):
                display_stock_card(name, ticker, sig_data, idx + 100)
        
        if neutral_list:
            st.markdown("## 🟡 أسهم للمراقبة")
            for idx, (name, ticker, sig_data) in enumerate(neutral_list):
                display_stock_card(name, ticker, sig_data, idx + 200)
    
    st.markdown("---")
    st.caption("البورصة المصرية (EGX) | البيانات من Yahoo Finance | للأغراض التعليمية")

if __name__ == "__main__":
    main()
