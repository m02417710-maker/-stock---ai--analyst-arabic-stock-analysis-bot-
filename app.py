# app.py - البورصجي AI - النسخة العلوية (Tabs Edition) 🕶️
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ====================== إعدادات الصفحة ======================
st.set_page_config(
    page_title="البورصجي AI - المنصة الذكية",
    page_icon="🕶️",
    layout="wide",
    initial_sidebar_state="collapsed"  # ✅ القائمة الجانبية مغلقة افتراضياً
)

# ====================== تهيئة الجلسة ======================
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'language' not in st.session_state:
    st.session_state.language = 'ar'
if 'notifications_enabled' not in st.session_state:
    st.session_state.notifications_enabled = True
if 'risk_percentage' not in st.session_state:
    st.session_state.risk_percentage = 2.0
if 'capital' not in st.session_state:
    st.session_state.capital = 100000
if 'user_id' not in st.session_state:
    st.session_state.user_id = "mysterious_user"

# ====================== CSS الاحترافي ======================
def apply_custom_style():
    if st.session_state.theme == 'dark':
        bg_color = "#0a0a0f"
        card_bg = "#14141e"
        border_color = "#2a2a3e"
        accent_color = "#00ffcc"
    else:
        bg_color = "#f0f2f6"
        card_bg = "#ffffff"
        border_color = "#e0e0e0"
        accent_color = "#00b4d8"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Cairo', sans-serif;
        box-sizing: border-box;
    }}
    
    .stApp {{
        background: {bg_color};
    }}
    
    /* تنسيق الشعار العلوي */
    .header-container {{
        text-align: center;
        padding: 15px 20px;
        margin-bottom: 20px;
        border-bottom: 1px solid {border_color};
        background: {card_bg}80;
        backdrop-filter: blur(10px);
        position: sticky;
        top: 0;
        z-index: 100;
    }}
    
    .main-title {{
        font-size: 42px;
        background: linear-gradient(135deg, #00ffcc, #00b4d8, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        display: inline-block;
    }}
    
    .subtitle {{
        color: {accent_color}80;
        font-size: 12px;
        margin-top: -5px;
    }}
    
    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {card_bg};
        padding: 10px;
        border-radius: 16px;
        margin-bottom: 20px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 12px;
        padding: 8px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {accent_color}20;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {accent_color}, #ff00ff);
        color: #000 !important;
    }}
    
    /* الشبكة الرئيسية */
    .dashboard-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }}
    
    .grid-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .grid-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {accent_color}, #ff00ff);
    }}
    
    .grid-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 255, 204, 0.1);
    }}
    
    .grid-value {{
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, {accent_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }}
    
    .grid-label {{
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* شريط المؤشرات المتحرك */
    .ticker-tape {{
        background: linear-gradient(90deg, {accent_color}, #ff00ff, {accent_color});
        background-size: 200% 100%;
        animation: gradient 3s ease infinite;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 20px;
        overflow: hidden;
        white-space: nowrap;
        font-weight: bold;
        color: #000;
    }}
    
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    .ticker-content {{
        display: inline-block;
        animation: scroll 25s linear infinite;
    }}
    
    @keyframes scroll {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    
    /* بطاقات الأسهم */
    .stock-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }}
    
    .stock-card:hover {{
        border-color: {accent_color};
        transform: translateX(5px);
    }}
    
    .profit-positive {{
        color: #00ff88;
        font-weight: bold;
    }}
    
    .profit-negative {{
        color: #ff4444;
        font-weight: bold;
    }}
    
    /* شارات */
    .badge {{
        display: inline-block;
        background: {accent_color}20;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 10px;
        color: {accent_color};
        margin: 2px;
    }}
    
    /* فرص الاستثمار */
    .opportunity-card {{
        background: linear-gradient(135deg, {card_bg}, #1a1a2e);
        border-left: 4px solid #00ff88;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }}
    
    /* زر مخصص */
    .custom-button {{
        background: linear-gradient(135deg, #ff00ff, {accent_color});
        border: none;
        padding: 10px 20px;
        border-radius: 30px;
        color: #000;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
    }}
    
    /* تذييل */
    .footer {{
        text-align: center;
        padding: 20px;
        color: #444;
        font-size: 11px;
        margin-top: 30px;
        border-top: 1px solid {border_color};
    }}
    
    /* تحديث المؤشر */
    .refresh-indicator {{
        text-align: right;
        font-size: 10px;
        color: #555;
        margin-bottom: 15px;
        font-family: monospace;
    }}
    
    /* شريط جانبي صغير للإعدادات */
    .settings-bar {{
        background: {card_bg};
        border-radius: 12px;
        padding: 10px 15px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid {border_color};
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== الترجمة ======================
STRINGS = {
    "ar": {
        "app_name": "🕶️ البورصجي AI",
        "subtitle": "العين التي لا تنام في الأسواق",
        "buying_power": "القوة الشرائية",
        "investment_value": "قيمة الاستثمار",
        "today_profit": "أرباح اليوم",
        "win_rate": "نسبة النجاح",
        "portfolio": "المحفظة السرية",
        "radar": "رادار الأسواق",
        "lab": "المختبر الذكي",
        "dashboard": "لوحة التحكم",
        "add_stock": "إضافة سهم",
        "ticker": "الرمز",
        "price": "السعر",
        "quantity": "الكمية",
        "analyze": "تحليل",
        "delete": "حذف"
    },
    "en": {
        "app_name": "🕶️ Al-Boursagi AI",
        "subtitle": "The Eye That Never Sleeps",
        "buying_power": "Buying Power",
        "investment_value": "Investment Value",
        "today_profit": "Today's Profit",
        "win_rate": "Win Rate",
        "portfolio": "Secret Portfolio",
        "radar": "Market Radar",
        "lab": "AI Lab",
        "dashboard": "Dashboard",
        "add_stock": "Add Stock",
        "ticker": "Ticker",
        "price": "Price",
        "quantity": "Quantity",
        "analyze": "Analyze",
        "delete": "Delete"
    }
}

def t(key):
    return STRINGS[st.session_state.language].get(key, key)

# ====================== الاستيرادات ======================
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import requests

# ====================== التهيئة ======================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "boursagi.db"

# ====================== قاعدة البيانات ======================
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            ticker TEXT,
            name TEXT,
            avg_price REAL,
            quantity INTEGER,
            buy_date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_database()

# ====================== إعداد Gemini ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== إعداد تليجرام ======================
def send_telegram_alert(message: str, priority: str = "info"):
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            icons = {"danger": "🚨", "warning": "⚠️", "success": "✅", "info": "📊"}
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": f"{icons.get(priority, '📊')} {message}", "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
    except:
        pass

# ====================== التحليل الفني ======================
def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def analyze_stock(ticker: str) -> Optional[Dict]:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="2mo")
        
        if df.empty or len(df) < 20:
            return None
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        daily_change = ((current_price - prev_price) / prev_price) * 100
        
        rsi = calculate_rsi(df['Close'])
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current_price
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        if rsi < 30:
            signal = "buy"
            action = "🟢 شراء قوي"
        elif rsi < 40:
            signal = "buy_weak"
            action = "🟡 شراء تدريجي"
        elif rsi > 70:
            signal = "sell"
            action = "🔴 بيع"
        elif rsi > 60:
            signal = "sell_weak"
            action = "🟠 مراقبة"
        else:
            signal = "hold"
            action = "⚪ انتظار"
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "daily_change": daily_change,
            "rsi": rsi,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "support": support,
            "resistance": resistance,
            "signal": signal,
            "action": action
        }
    except Exception as e:
        return None

def create_advanced_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """إنشاء رسم بياني مع تدرج لوني"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        name='السعر',
        line=dict(color='#00ffcc', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 204, 0.15)'
    ))
    
    if 'SMA_20' not in df.columns:
        df['SMA_20'] = df['Close'].rolling(20).mean()
    if 'SMA_50' not in df.columns:
        df['SMA_50'] = df['Close'].rolling(50).mean()
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_20'],
        mode='lines',
        name='SMA 20',
        line=dict(color='#ffaa00', width=1.5, dash='dash')
    ))
    
    fig.update_layout(
        title=f'{ticker} - التحليل الفني',
        template='plotly_dark',
        height=450,
        xaxis_title='التاريخ',
        yaxis_title='السعر',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# ====================== إدارة المحفظة ======================
class PortfolioManager:
    @staticmethod
    def add_stock(user_id: str, ticker: str, name: str, avg_price: float, quantity: int):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO portfolio (user_id, ticker, name, avg_price, quantity, buy_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, ticker.upper(), name, avg_price, quantity, datetime.now()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def remove_stock(user_id: str, ticker: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM portfolio WHERE user_id = ? AND ticker = ?', (user_id, ticker.upper()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_portfolio(user_id: str) -> List[Dict]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT ticker, name, avg_price, quantity FROM portfolio WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"ticker": r[0], "name": r[1], "avg_price": r[2], "quantity": r[3]} for r in rows]
    
    @staticmethod
    def get_portfolio_value(user_id: str) -> Dict:
        stocks = PortfolioManager.get_portfolio(user_id)
        total_invested = 0
        total_current = 0
        today_profit = 0
        
        for stock in stocks:
            analysis = analyze_stock(stock['ticker'])
            if analysis:
                invested = stock['avg_price'] * stock['quantity']
                current = analysis['current_price'] * stock['quantity']
                total_invested += invested
                total_current += current
                today_profit += (analysis['daily_change'] / 100) * invested
        
        return {
            "total_invested": total_invested,
            "total_current": total_current,
            "total_profit": total_current - total_invested,
            "total_profit_pct": ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            "today_profit": today_profit
        }

# ====================== رادار السوق ======================
MARKET_STOCKS = [
    "COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "EAST.CA",
    "2222.SR", "1120.SR", "7010.SR",
    "AAPL", "MSFT", "TSLA", "NVDA", "GOOGL"
]

def run_market_scanner() -> List[Dict]:
    opportunities = []
    for ticker in MARKET_STOCKS:
        analysis = analyze_stock(ticker)
        if analysis and analysis['signal'] in ['buy', 'buy_weak']:
            opportunities.append(analysis)
    opportunities.sort(key=lambda x: 0 if x['signal'] == 'buy' else 1)
    return opportunities

# ====================== شريط المؤشرات ======================
def display_ticker_tape():
    try:
        indices = {"EGX 30": "^EGX30", "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "TASI": "^TASI"}
        items = []
        for name, ticker in indices.items():
            try:
                data = yf.Ticker(ticker).history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    prev = data['Close'].iloc[-2] if len(data) > 1 else price
                    change = ((price - prev) / prev) * 100
                    arrow = "▲" if change >= 0 else "▼"
                    color = "#00ff88" if change >= 0 else "#ff4444"
                    items.append(f'{name}: <span style="color:#00ffcc">{price:.0f}</span> <span style="color:{color}">{arrow} {change:+.2f}%</span>')
            except:
                pass
        if items:
            st.markdown(f'''
            <div class="ticker-tape">
                <div class="ticker-content">🔴 LIVE | {" | ".join(items)} | 🔴 أسرار السوق</div>
            </div>
            ''', unsafe_allow_html=True)
    except:
        pass

# ====================== الواجهة الرئيسية ======================

def main():
    model = init_gemini()
    
    # ====================== الهيدر العلوي ======================
    st.markdown(f'''
    <div class="header-container">
        <div>
            <span class="main-title">{t('app_name')}</span>
        </div>
        <div class="subtitle">{t('subtitle')}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # ====================== شريط الإعدادات العلوي ======================
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    with col1:
        st.markdown(f'<div class="refresh-indicator">🕐 {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🌓", help="تغيير المظهر"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    with col3:
        if st.button("🌐", help="تغيير اللغة"):
            st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
            st.rerun()
    with col4:
        if model:
            st.markdown('<div style="text-align: right; color: #00ffcc;">🧠 الذكاء الغامض: نشط</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align: right; color: #ff4444;">⚠️ أضف مفتاح API</div>', unsafe_allow_html=True)
    
    # ====================== التبويبات العلوية ======================
    tabs = st.tabs(["📊 " + t('dashboard'), "💼 " + t('portfolio'), "📡 " + t('radar'), "🧠 " + t('lab')])
    
    # ====================== التبويب 1: لوحة التحكم ======================
    with tabs[0]:
        display_ticker_tape()
        
        portfolio_value = PortfolioManager.get_portfolio_value(st.session_state.user_id)
        
        # شبكة المؤشرات (4 بطاقات)
        st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="grid-card">
            <div class="grid-label">💰 {t('buying_power')}</div>
            <div class="grid-value">{st.session_state.capital - portfolio_value['total_invested']:,.0f}</div>
        </div>
        <div class="grid-card">
            <div class="grid-label">📈 {t('investment_value')}</div>
            <div class="grid-value">{portfolio_value['total_current']:,.0f}</div>
        </div>
        <div class="grid-card">
            <div class="grid-label">📊 {t('today_profit')}</div>
            <div class="grid-value" style="color: {"#00ff88" if portfolio_value['today_profit'] >= 0 else "#ff4444"}">
                {portfolio_value['today_profit']:+,.0f}
            </div>
        </div>
        <div class="grid-card">
            <div class="grid-label">🏆 {t('win_rate')}</div>
            <div class="grid-value">93<span style="font-size:18px">%</span></div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # رسم بياني للسوق العام
        st.markdown("### 📈 مؤشر السوق العام (S&P 500)")
        try:
            df_market = yf.Ticker("^GSPC").history(period="1mo")
            if not df_market.empty:
                fig = create_advanced_chart(df_market, "S&P 500")
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("جاري تحميل بيانات السوق...")
        
        # إحصائيات سريعة
        col1, col2 = st.columns(2)
        with col1:
            stocks_count = len(PortfolioManager.get_portfolio(st.session_state.user_id))
            st.metric("📊 عدد الأسهم في المحفظة", stocks_count)
        with col2:
            st.metric("💵 رأس المال المتبقي", f"{st.session_state.capital - portfolio_value['total_invested']:,.0f}")
    
    # ====================== التبويب 2: المحفظة السرية ======================
    with tabs[1]:
        st.markdown(f"### 💼 {t('portfolio')}")
        
        # قسم إضافة سهم جديد
        with st.expander("➕ " + t('add_stock')):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                new_ticker = st.text_input(t('ticker'), placeholder="COMI.CA").upper()
            with col2:
                new_name = st.text_input("الاسم", placeholder="البنك التجاري")
            with col3:
                buy_price = st.number_input(t('price'), min_value=0.0, step=0.5)
            with col4:
                quantity = st.number_input(t('quantity'), min_value=1, step=1)
            
            if st.button("✨ أضف للمحفظة السرية", use_container_width=True):
                if new_ticker and buy_price and quantity:
                    PortfolioManager.add_stock(st.session_state.user_id, new_ticker, new_name or new_ticker, buy_price, int(quantity))
                    st.success(f"✅ تم إضافة {new_ticker} إلى المحفظة السرية")
                    st.rerun()
        
        # عرض الأسهم
        portfolio_stocks = PortfolioManager.get_portfolio(st.session_state.user_id)
        
        if portfolio_stocks:
            for stock in portfolio_stocks:
                analysis = analyze_stock(stock['ticker'])
                if analysis:
                    profit_pct = ((analysis['current_price'] - stock['avg_price']) / stock['avg_price']) * 100
                    profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
                    
                    st.markdown(f'''
                    <div class="stock-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 16px; font-weight: bold;">{stock['name']}</span>
                                <span class="badge">{stock['ticker']}</span>
                            </div>
                            <div class="{profit_class}">{profit_pct:+.1f}%</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <div>💰 شراء: {stock['avg_price']:.2f}</div>
                            <div>📊 حالياً: {analysis['current_price']:.2f}</div>
                            <div>📈 RSI: {analysis['rsi']:.1f}</div>
                            <div>{analysis['action']}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button(f"📊 رسم", key=f"chart_{stock['ticker']}"):
                            df = yf.Ticker(stock['ticker']).history(period="2mo")
                            if not df.empty:
                                fig = create_advanced_chart(df, stock['ticker'])
                                st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        if st.button(f"🧠 تحليل", key=f"ai_{stock['ticker']}"):
                            if model:
                                with st.spinner("الذكاء الغامض يفكر..."):
                                    prompt = f"حلل سهم {stock['name']}: السعر {analysis['current_price']:.2f}, RSI {analysis['rsi']:.1f}"
                                    response = model.generate_content(prompt)
                                    st.info(f"🕶️ {response.text}")
                    with col3:
                        if st.button(f"📢 تنبيه", key=f"alert_{stock['ticker']}"):
                            msg = f"🔔 تنبيه: {stock['name']} سعره {analysis['current_price']:.2f}"
                            send_telegram_alert(msg, "info")
                            st.toast("✅ تم إرسال التنبيه")
                    with col4:
                        if st.button(f"🗑️ حذف", key=f"del_{stock['ticker']}"):
                            PortfolioManager.remove_stock(st.session_state.user_id, stock['ticker'])
                            st.rerun()
                    
                    # تنبيه وقف الخسارة
                    stop_loss = stock['avg_price'] * 0.95
                    if analysis['current_price'] <= stop_loss:
                        st.error(f"⚠️ **تنبيه!** {stock['name']} وصل إلى {analysis['current_price']:.2f}")
        else:
            st.info("📭 المحفظة السرية فارغة... أضف أسهمك الأولى")
    
    # ====================== التبويب 3: رادار الأسواق ======================
    with tabs[2]:
        st.markdown(f"### 📡 {t('radar')}")
        
        if st.button("🔍 تشغيل الرادار الخفي", type="primary", use_container_width=True):
            with st.spinner("جاري مسح الترددات..."):
                opportunities = run_market_scanner()
                st.session_state['scan_results'] = opportunities
                st.success(f"✅ تم كشف {len(opportunities)} سر في السوق")
        
        if 'scan_results' in st.session_state and st.session_state['scan_results']:
            for opp in st.session_state['scan_results'][:8]:
                st.markdown(f'''
                <div class="opportunity-card">
                    🕶️ <b>{opp['ticker']}</b> - السعر: {opp['current_price']:.2f} | RSI: {opp['rsi']:.1f} | {opp['action']}
                    <div style="font-size: 11px; color: #888;">
                        🛡️ دعم: {opp['support']:.2f} | 🚀 مقاومة: {opp['resistance']:.2f}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # إرسال تنبيه للفرص القوية
                if opp['signal'] == 'buy' and st.session_state.notifications_enabled:
                    send_telegram_alert(f"🚀 فرصة شراء: {opp['ticker']} بسعر {opp['current_price']:.2f}", "success")
        else:
            st.info("اضغط على 'تشغيل الرادار الخفي' لكشف الأسرار المخفية")
    
    # ====================== التبويب 4: المختبر الذكي ======================
    with tabs[3]:
        st.markdown(f"### 🧠 {t('lab')}")
        st.markdown("اسأل البورصجي AI عن أي سهم أو استفسار مالي...")
        
        query = st.chat_input("اكتب سؤالك هنا...")
        if query:
            if model:
                with st.chat_message("assistant", avatar="🕶️"):
                    with st.spinner("الذكاء الغامض يفكر..."):
                        response = model.generate_content(query)
                        st.write(response.text)
            else:
                st.warning("⚠️ الذكاء الغامض غير متوفر - أضف مفتاح Gemini API في secrets")
        
        # اقتراحات أسئلة
        st.markdown("---")
        st.markdown("### 💡 اقتراحات للاستفسار:")
        suggestions = ["حلل لي سهم Apple", "ما هي توقعات الذهب؟", "شرح مؤشر RSI باختصار"]
        for s in suggestions:
            if st.button(s, key=s):
                st.session_state['suggestion'] = s
                st.rerun()
        
        if 'suggestion' in st.session_state and model:
            with st.chat_message("assistant", avatar="🕶️"):
                response = model.generate_content(st.session_state['suggestion'])
                st.write(response.text)
            del st.session_state['suggestion']
    
    # ====================== تذييل ======================
    st.markdown(f'''
    <div class="footer">
        🕶️ {t('app_name')} - العين التي لا تنام | تحديث لحظي | أسرار السوق<br>
        © 2024 - بعض الأسرار لا تُكشف...
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
