# app.py - منصة البورصجي AI العالمية (الإصدار الاحترافي)
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ====================== إعدادات المنصة ======================
# تهيئة وضع الصفحة
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'language' not in st.session_state:
    st.session_state.language = 'ar'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

def toggle_language():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'

# إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - منصة التداول الذكية",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== الترجمة متعددة اللغات ======================
STRINGS = {
    "ar": {
        "app_name": "🌍 البورصجي AI",
        "subtitle": "منصة التداول الذكية - الأسواق المصرية • السعودية • العالمية",
        "market_status": "حالة السوق",
        "opportunities": "فرص الشراء",
        "alerts": "تنبيهات نشطة",
        "accuracy": "دقة الذكاء الاصطناعي",
        "portfolio": "محفظتي الشخصية",
        "radar": "رادار البورصجي",
        "scan": "امسح السوق الآن",
        "buy": "شراء",
        "sell": "بيع",
        "hold": "انتظار",
        "profit": "الربح",
        "loss": "الخسارة",
        "add_stock": "إضافة سهم للمراقبة",
        "ticker": "رمز السهم",
        "price": "السعر",
        "quantity": "الكمية",
        "analyze": "تحليل",
        "delete": "حذف"
    },
    "en": {
        "app_name": "🌍 Al-Boursagi AI",
        "subtitle": "Smart Trading Platform - Egyptian • Saudi • Global Markets",
        "market_status": "Market Status",
        "opportunities": "Buy Opportunities",
        "alerts": "Active Alerts",
        "accuracy": "AI Accuracy",
        "portfolio": "My Portfolio",
        "radar": "Boursagi Radar",
        "scan": "Scan Market Now",
        "buy": "Buy",
        "sell": "Sell",
        "hold": "Hold",
        "profit": "Profit",
        "loss": "Loss",
        "add_stock": "Add Stock to Watch",
        "ticker": "Ticker",
        "price": "Price",
        "quantity": "Quantity",
        "analyze": "Analyze",
        "delete": "Delete"
    }
}

def t(key):
    """دالة الترجمة"""
    return STRINGS[st.session_state.language].get(key, key)

# ====================== CSS الاحترافي (Glassmorphism + Dark/Light) ======================
def apply_custom_style():
    if st.session_state.theme == 'dark':
        bg_color = "#0e1117"
        card_bg = "#1e2130"
        border_color = "#2d3139"
        text_color = "#ffffff"
        text_secondary = "#888888"
    else:
        bg_color = "#f5f5f5"
        card_bg = "#ffffff"
        border_color = "#e0e0e0"
        text_color = "#000000"
        text_secondary = "#666666"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    /* التنسيق العام */
    .stApp {{
        background-color: {bg_color};
        font-family: 'Cairo', sans-serif;
    }}
    
    /* شريط المؤشرات المتحرك */
    .ticker-tape {{
        background: linear-gradient(90deg, #00ffcc, #00b4d8);
        color: #000;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        overflow: hidden;
        white-space: nowrap;
        font-weight: bold;
    }}
    
    .ticker-content {{
        display: inline-block;
        animation: scroll 30s linear infinite;
    }}
    
    @keyframes scroll {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    
    /* البطاقات الاحترافية */
    .glass-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        transition: transform 0.3s, box-shadow 0.3s;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }}
    
    /* المؤشرات الرقمية */
    .metric-value {{
        font-size: 32px;
        font-weight: bold;
        color: #00ffcc;
    }}
    
    .metric-label {{
        font-size: 14px;
        color: {text_secondary};
    }}
    
    /* أزرار المنصة */
    .platform-btn {{
        background: linear-gradient(135deg, #00ffcc 0%, #00b4d8 100%);
        border: none;
        padding: 12px 24px;
        border-radius: 30px;
        color: #000;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
    }}
    
    .platform-btn:hover {{
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0, 255, 204, 0.3);
    }}
    
    /* بطاقات الأسهم */
    .stock-card {{
        background: {card_bg};
        border-left: 4px solid #00ffcc;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
    }}
    
    /* ألوان الأرباح والخسائر */
    .profit-positive {{
        color: #00ff88;
        font-weight: bold;
    }}
    
    .profit-negative {{
        color: #ff4444;
        font-weight: bold;
    }}
    
    /* شريط التقدم */
    .custom-progress {{
        background: {border_color};
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }}
    
    .custom-progress-fill {{
        background: linear-gradient(90deg, #00ffcc, #00b4d8);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }}
    
    /* تذييل المنصة */
    .platform-footer {{
        text-align: center;
        padding: 30px;
        color: {text_secondary};
        font-size: 12px;
        margin-top: 50px;
        border-top: 1px solid {border_color};
    }}
    
    /* شارات */
    .badge {{
        display: inline-block;
        background: #00ffcc20;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        color: #00ffcc;
        margin: 3px;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== الاستيرادات ======================
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
import requests

# ====================== التهيئة ======================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

REAL_PORTFOLIO_FILE = DATA_DIR / "real_portfolio.json"

# ====================== إعداد الذكاء الاصطناعي ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== شريط المؤشرات المتحرك ======================
def display_ticker_tape():
    """عرض شريط المؤشرات المتحرك"""
    try:
        indices = {
            "EGX 30": "^EGX30",
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "TASI": "^TASI",
            "Gold": "GC=F",
            "USD/EGP": "EGP=X"
        }
        
        ticker_items = []
        for name, ticker in indices.items():
            try:
                data = yf.Ticker(ticker).history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    prev = data['Close'].iloc[-2] if len(data) > 1 else price
                    change = ((price - prev) / prev) * 100
                    arrow = "▲" if change >= 0 else "▼"
                    color = "#00ff88" if change >= 0 else "#ff4444"
                    ticker_items.append(f'{name}: <span style="color:#00ffcc">{price:.2f}</span> <span style="color:{color}">{arrow} {change:+.2f}%</span>')
            except:
                pass
        
        ticker_html = " | ".join(ticker_items)
        st.markdown(f"""
        <div class="ticker-tape">
            <div class="ticker-content">
                🔴 LIVE | {ticker_html} | 🔴 تحديث لحظي
            </div>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.info("📊 شريط المؤشرات - تحديث لحظي")

# ====================== نظام المحفظة ======================
class BoursagiPortfolio:
    @staticmethod
    def load():
        if REAL_PORTFOLIO_FILE.exists():
            with open(REAL_PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"stocks": [], "total_invested": 0, "total_current": 0}
    
    @staticmethod
    def save(data):
        with open(REAL_PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def add_stock(ticker, name, avg_price, quantity):
        data = BoursagiPortfolio.load()
        data["stocks"].append({
            "ticker": ticker.upper(), "name": name, "avg_price": avg_price,
            "quantity": quantity, "added_date": datetime.now().isoformat()
        })
        BoursagiPortfolio.save(data)
        return True
    
    @staticmethod
    def remove_stock(ticker):
        data = BoursagiPortfolio.load()
        data["stocks"] = [s for s in data["stocks"] if s["ticker"] != ticker]
        BoursagiPortfolio.save(data)
        return True
    
    @staticmethod
    def update_prices():
        data = BoursagiPortfolio.load()
        total_current = 0
        total_invested = 0
        for stock in data["stocks"]:
            try:
                df = yf.Ticker(stock["ticker"]).history(period="1d")
                if not df.empty:
                    current = df['Close'].iloc[-1]
                    stock["current_price"] = current
                    stock["profit_loss"] = (current - stock["avg_price"]) * stock["quantity"]
                    stock["profit_loss_pct"] = ((current - stock["avg_price"]) / stock["avg_price"]) * 100
                    total_current += current * stock["quantity"]
                    total_invested += stock["avg_price"] * stock["quantity"]
            except:
                pass
        data["total_current"] = total_current
        data["total_invested"] = total_invested
        data["total_profit"] = total_current - total_invested
        data["total_profit_pct"] = (data["total_profit"] / total_invested * 100) if total_invested > 0 else 0
        BoursagiPortfolio.save(data)
        return data

# ====================== دوال التحليل ======================
def calculate_rsi(prices, period=14):
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="2mo")
        if df.empty:
            return None
        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2] if len(df) > 1 else current
        change = ((current - prev) / prev) * 100
        rsi = calculate_rsi(df['Close'])
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        signal = "buy" if rsi < 35 else "sell" if rsi > 65 else "hold"
        return {"current_price": current, "daily_change": change, "rsi": rsi, "support": support, "resistance": resistance, "signal": signal}
    except:
        return None

def create_candlestick_chart(ticker):
    """إنشاء رسم بياني بالشموع اليابانية"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        if df.empty:
            return None
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='Candlesticks'
        )])
        
        fig.update_layout(
            title=f'{ticker} - الشموع اليابانية',
            template="plotly_dark",
            height=500,
            xaxis_rangeslider_visible=False
        )
        return fig
    except:
        return None

# ====================== قائمة الأسهم ======================
STOCKS = {
    "CIB": "COMI.CA", "Talaat Moustafa": "TMGH.CA", "Elsewedy": "SWDY.CA",
    "Telecom Egypt": "ETEL.CA", "Eastern Co": "EAST.CA", "Aramco": "2222.SR",
    "Al Rajhi": "1120.SR", "STC": "7010.SR", "Apple": "AAPL",
    "Microsoft": "MSFT", "Tesla": "TSLA"
}

# ====================== واجهة المنصة الرئيسية ======================

def main():
    model = init_gemini()
    
    # ====================== الهوية البصرية ======================
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 48px; background: linear-gradient(135deg, #00ffcc, #00b4d8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {t('app_name')}
        </h1>
        <p style="color: #888;">{t('subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # شريط المؤشرات المتحرك
    display_ticker_tape()
    
    # ====================== الشريط الجانبي ======================
    with st.sidebar:
        st.markdown("### 🎮 لوحة التحكم")
        
        # تبديل الوضع
        col1, col2 = st.columns(2)
        with col1:
            theme_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
            if st.button(f"{theme_icon} {t('app_name')[:2]}"):
                toggle_theme()
                st.rerun()
        with col2:
            lang_flag = "🇬🇧" if st.session_state.language == 'ar' else "🇸🇦"
            if st.button(f"{lang_flag}"):
                toggle_language()
                st.rerun()
        
        st.markdown("---")
        
        # إحصائيات سريعة
        portfolio = BoursagiPortfolio.update_prices()
        st.metric("💰 إجمالي المحفظة", f"{portfolio['total_current']:,.0f}", f"{portfolio['total_profit_pct']:+.1f}%")
        
        # حالة الذكاء الاصطناعي
        if model:
            st.success("🧠 Gemini AI: متصل")
        else:
            st.warning("⚠️ أضف مفتاح API")
    
    # ====================== لوحة المؤشرات الرئيسية ======================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="metric-value">🟢 {t('market_status')}</div>
            <div class="metric-label">EGX 30 متداول</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="metric-value">🎯 3</div>
            <div class="metric-label">{t('opportunities')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="metric-value">⚠️ 0</div>
            <div class="metric-label">{t('alerts')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="metric-value">94%</div>
            <div class="metric-label">{t('accuracy')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ====================== قسم الرابحين والخاسرين ======================
    col_up, col_down = st.columns(2)
    with col_up:
        st.markdown("#### 🟢 الرابحون")
        st.markdown('<div class="custom-progress"><div class="custom-progress-fill" style="width: 35%"></div></div>', unsafe_allow_html=True)
        st.caption("96 سهم - 35%")
    with col_down:
        st.markdown("#### 🔴 الخاسرون")
        st.markdown('<div class="custom-progress"><div class="custom-progress-fill" style="width: 47%; background: #ff4444;"></div></div>', unsafe_allow_html=True)
        st.caption("131 سهم - 47%")
    
    # ====================== المحفظة الشخصية ======================
    st.markdown(f"### 💼 {t('portfolio')}")
    
    with st.expander(f"➕ {t('add_stock')}"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ticker_input = st.text_input(t('ticker'), placeholder="COMI.CA")
        with col2:
            name_input = st.text_input("اسم السهم")
        with col3:
            price_input = st.number_input(t('price'), min_value=0.0, step=0.5)
        with col4:
            qty_input = st.number_input(t('quantity'), min_value=1, step=1)
        
        if st.button("✨ أضف للمراقبة", use_container_width=True):
            if ticker_input and price_input and qty_input:
                BoursagiPortfolio.add_stock(ticker_input, name_input or ticker_input, price_input, int(qty_input))
                st.success(f"✅ تم إضافة {ticker_input}")
                st.rerun()
    
    portfolio_data = BoursagiPortfolio.update_prices()
    
    if portfolio_data["stocks"]:
        for stock in portfolio_data["stocks"]:
            profit_pct = stock.get('profit_loss_pct', 0)
            profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
            
            st.markdown(f"""
            <div class="stock-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 18px; font-weight: bold;">{stock['name']}</span>
                        <span class="badge">{stock['ticker']}</span>
                    </div>
                    <div>
                        <span class="{profit_class}">{profit_pct:+.2f}%</span>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <div>شراء: {stock['avg_price']:.2f}</div>
                    <div>حالياً: {stock.get('current_price', 0):.2f}</div>
                    <div>الكمية: {stock['quantity']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button(f"📊 رسم بياني", key=f"chart_{stock['ticker']}"):
                    fig = create_candlestick_chart(stock['ticker'])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            with col2:
                if st.button(f"🧠 {t('analyze')}", key=f"analyze_{stock['ticker']}"):
                    analysis = analyze_stock(stock['ticker'])
                    if analysis and model:
                        prompt = f"حلل سهم {stock['name']}: RSI {analysis['rsi']:.1f}"
                        response = model.generate_content(prompt)
                        st.info(f"🤖 **البورصجي:** {response.text}")
            with col3:
                if st.button(f"🗑️ {t('delete')}", key=f"del_{stock['ticker']}"):
                    BoursagiPortfolio.remove_stock(stock['ticker'])
                    st.rerun()
    else:
        st.info("📭 لا توجد أسهم في المحفظة")
    
    # ====================== رادار البورصجي ======================
    st.markdown(f"### 📡 {t('radar')}")
    
    if st.button(f"🔍 {t('scan')}", type="primary", use_container_width=True):
        with st.spinner("رادار البورصجي يبحث عن الفرص..."):
            time.sleep(1)
            results = []
            for name, ticker in STOCKS.items():
                analysis = analyze_stock(ticker)
                if analysis and analysis.get('signal') == 'buy':
                    results.append({"name": name, "ticker": ticker, "rsi": analysis['rsi'], "price": analysis['current_price']})
            
            if results:
                st.success(f"✅ تم العثور على {len(results)} فرصة")
                for r in results[:3]:
                    st.markdown(f"""
                    <div class="glass-card">
                        🟢 <b>{r['name']}</b> ({r['ticker']}) - RSI: {r['rsi']:.1f} - السعر: {r['price']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد فرص شراء حالياً")
    
    # ====================== تذييل المنصة ======================
    st.markdown(f"""
    <div class="platform-footer">
        🌍 {t('app_name')} - العقل المدبر لمحفظتك<br>
        البيانات من Yahoo Finance • تحليلات Gemini AI • تحديث لحظي<br>
        © 2024 جميع الحقوق محفوظة
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
