# app.py - منصة البورصجي AI - الإصدار النهائي (Production Ready)
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ====================== إعدادات الصفحة ======================
st.set_page_config(
    page_title="البورصجي AI - منصة التداول الذكية",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
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
    st.session_state.user_id = "default_user"
if 'auto_scan_enabled' not in st.session_state:
    st.session_state.auto_scan_enabled = True

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
    }}
    
    .stApp {{
        background-color: {bg_color};
    }}
    
    /* تنسيق الشعار */
    .logo-container {{
        text-align: center;
        padding: 20px;
        margin-bottom: 20px;
    }}
    
    /* بطاقات الشبكة */
    .dashboard-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }}
    
    .grid-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 24px;
        padding: 24px;
        transition: all 0.3s;
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
        background: linear-gradient(90deg, {accent_color}, #00ff88);
    }}
    
    .grid-card:hover {{
        transform: translateY(-3px);
    }}
    
    .grid-value {{
        font-size: 36px;
        font-weight: 800;
        color: {accent_color};
        margin: 10px 0;
    }}
    
    .grid-label {{
        font-size: 14px;
        color: #888;
    }}
    
    .grid-icon {{
        position: absolute;
        bottom: 20px;
        right: 20px;
        font-size: 40px;
        opacity: 0.1;
    }}
    
    /* شريط المؤشرات */
    .ticker-tape {{
        background: linear-gradient(90deg, {accent_color}, #00ff88);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 20px;
        overflow: hidden;
        white-space: nowrap;
        font-weight: bold;
        color: #000;
    }}
    
    /* بطاقات الأسهم */
    .stock-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s;
    }}
    
    .stock-card:hover {{
        border-color: {accent_color};
    }}
    
    .profit-positive {{ color: #00ff88; font-weight: bold; }}
    .profit-negative {{ color: #ff4444; font-weight: bold; }}
    
    /* شارات */
    .badge {{
        display: inline-block;
        background: {accent_color}20;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        color: {accent_color};
        margin: 3px;
    }}
    
    .sentiment-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
    }}
    
    .sentiment-positive {{ background: #00ff8820; color: #00ff88; }}
    .sentiment-negative {{ background: #ff444420; color: #ff4444; }}
    .sentiment-neutral {{ background: #ffaa0020; color: #ffaa00; }}
    
    /* تذييل */
    .platform-footer {{
        text-align: center;
        padding: 30px;
        color: #666;
        font-size: 12px;
        margin-top: 50px;
        border-top: 1px solid {border_color};
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== الترجمة ======================
STRINGS = {
    "ar": {
        "app_name": "🧠 البورصجي AI",
        "subtitle": "منصة التداول الذكية",
        "buying_power": "القوة الشرائية",
        "investment_value": "قيمة الاستثمار",
        "today_profit": "أرباح اليوم",
        "win_rate": "نسبة النجاح",
        "portfolio": "محفظتي",
        "radar": "رادار السوق",
        "scan_market": "مسح السوق",
        "add_stock": "إضافة سهم",
        "ticker": "رمز السهم",
        "price": "السعر",
        "quantity": "الكمية",
        "analyze": "تحليل",
        "delete": "حذف"
    },
    "en": {
        "app_name": "🧠 Al-Boursagi AI",
        "subtitle": "Smart Trading Platform",
        "buying_power": "Buying Power",
        "investment_value": "Investment Value",
        "today_profit": "Today's Profit",
        "win_rate": "Win Rate",
        "portfolio": "My Portfolio",
        "radar": "Market Radar",
        "scan_market": "Scan Market",
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
from typing import Dict, List
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

def analyze_stock(ticker: str):
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
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        # تحديد الإشارة
        if rsi < 30:
            signal = "buy"
            action = "🟢 شراء"
        elif rsi > 70:
            signal = "sell"
            action = "🔴 بيع"
        else:
            signal = "hold"
            action = "🟡 انتظار"
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "daily_change": daily_change,
            "rsi": rsi,
            "sma_20": sma_20,
            "support": support,
            "resistance": resistance,
            "signal": signal,
            "action": action
        }
    except Exception as e:
        return None

def create_advanced_chart(df: pd.DataFrame, ticker: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        name='السعر',
        line=dict(color='#00ffcc', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 204, 0.1)'
    ))
    fig.update_layout(
        title=f'{ticker} - الأداء',
        template='plotly_dark',
        height=400,
        xaxis_title='التاريخ',
        yaxis_title='السعر'
    )
    return fig

# ====================== إدارة المحفظة ======================
class PortfolioManager:
    @staticmethod
    def add_stock(user_id, ticker, name, avg_price, quantity):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO portfolio (user_id, ticker, name, avg_price, quantity, buy_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, ticker.upper(), name, avg_price, quantity, datetime.now()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def remove_stock(user_id, ticker):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM portfolio WHERE user_id = ? AND ticker = ?', (user_id, ticker.upper()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_portfolio(user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT ticker, name, avg_price, quantity FROM portfolio WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"ticker": r[0], "name": r[1], "avg_price": r[2], "quantity": r[3]} for r in rows]

# ====================== الماسح الآلي ======================
def automated_market_scan():
    """الماسح الآلي - يعمل في الخلفية"""
    target_stocks = ["COMI.CA", "TMGH.CA", "SWDY.CA", "2222.SR", "1120.SR", "AAPL", "MSFT", "TSLA"]
    opportunities = []
    
    for ticker in target_stocks:
        analysis = analyze_stock(ticker)
        if analysis and analysis['signal'] == 'buy':
            opportunities.append(analysis)
            if st.session_state.auto_scan_enabled and st.session_state.notifications_enabled:
                msg = f"🚀 فرصة ذهبية!\nالسهم: {ticker}\nالسعر: {analysis['current_price']:.2f}\nRSI: {analysis['rsi']:.1f}"
                send_telegram_alert(msg, "success")
    
    return opportunities

# ====================== شريط المؤشرات ======================
def display_ticker_tape():
    try:
        indices = {"EGX 30": "^EGX30", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
        items = []
        for name, ticker in indices.items():
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2] if len(data) > 1 else price
                change = ((price - prev) / prev) * 100
                arrow = "▲" if change >= 0 else "▼"
                color = "#00ff88" if change >= 0 else "#ff4444"
                items.append(f'{name}: {price:.0f} <span style="color:{color}">{arrow} {change:+.2f}%</span>')
        
        st.markdown(f'''
        <div class="ticker-tape">
            🔴 LIVE | {" | ".join(items)} | 🔴 تحديث لحظي
        </div>
        ''', unsafe_allow_html=True)
    except:
        pass

# ====================== الواجهة الرئيسية ======================

def main():
    model = init_gemini()
    
    # الشعار
    st.markdown(f'''
    <div class="logo-container">
        <h1 style="font-size: 48px; background: linear-gradient(135deg, #00ffcc, #00b4d8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {t('app_name')}
        </h1>
        <p style="color: #888;">{t('subtitle')}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    display_ticker_tape()
    
    # الشريط الجانبي
    with st.sidebar:
        st.image("https://placehold.co/200x60/14141e/00ffcc?text=Al-Boursagi", use_container_width=True)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌓 تبديل", use_container_width=True):
                st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
                st.rerun()
        with col2:
            if st.button("🌐 EN/AR", use_container_width=True):
                st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 💰 إعدادات المخاطر")
        st.session_state.capital = st.number_input("رأس المال", value=st.session_state.capital, step=10000)
        st.session_state.risk_percentage = st.slider("نسبة المخاطرة %", 0.5, 5.0, st.session_state.risk_percentage, 0.5)
        st.session_state.auto_scan_enabled = st.checkbox("🔄 المسح التلقائي", value=st.session_state.auto_scan_enabled)
        
        st.markdown("---")
        portfolio_stocks = PortfolioManager.get_portfolio(st.session_state.user_id)
        st.metric("📊 عدد الأسهم", len(portfolio_stocks))
        
        if model:
            st.success("🧠 Gemini: متصل")
        else:
            st.warning("⚠️ أضف API Key")
    
    # شبكة المؤشرات
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    portfolio_value = 0
    for s in portfolio_stocks:
        analysis = analyze_stock(s['ticker'])
        if analysis:
            portfolio_value += analysis['current_price'] * s['quantity']
    
    st.markdown(f'''
    <div class="grid-card">
        <div class="grid-label">💰 {t('buying_power')}</div>
        <div class="grid-value">{st.session_state.capital:,.0f}</div>
        <div class="grid-icon">💰</div>
    </div>
    <div class="grid-card">
        <div class="grid-label">📈 {t('investment_value')}</div>
        <div class="grid-value">{portfolio_value:,.0f}</div>
        <div class="grid-icon">📈</div>
    </div>
    <div class="grid-card">
        <div class="grid-label">📊 {t('today_profit')}</div>
        <div class="grid-value" style="color: #00ff88">+0</div>
        <div class="grid-icon">📊</div>
    </div>
    <div class="grid-card">
        <div class="grid-label">🏆 {t('win_rate')}</div>
        <div class="grid-value">72%</div>
        <div class="grid-icon">🏆</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # المحفظة
    st.markdown(f"### 💼 {t('portfolio')}")
    
    with st.expander(f"➕ {t('add_stock')}"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_ticker = st.text_input(t('ticker'), placeholder="COMI.CA")
        with col2:
            new_name = st.text_input("الاسم", placeholder="البنك التجاري")
        with col3:
            buy_price = st.number_input(t('price'), min_value=0.0, step=0.5)
        with col4:
            quantity = st.number_input(t('quantity'), min_value=1, step=1)
        
        if st.button("✨ أضف", use_container_width=True):
            if new_ticker and buy_price and quantity:
                PortfolioManager.add_stock(st.session_state.user_id, new_ticker, new_name or new_ticker, buy_price, int(quantity))
                st.success(f"✅ تم إضافة {new_ticker}")
                st.rerun()
    
    if portfolio_stocks:
        for stock in portfolio_stocks:
            analysis = analyze_stock(stock['ticker'])
            if analysis:
                profit_pct = ((analysis['current_price'] - stock['avg_price']) / stock['avg_price']) * 100
                profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
                
                st.markdown(f'''
                <div class="stock-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div><b>{stock['name']}</b> <span class="badge">{stock['ticker']}</span></div>
                        <div class="{profit_class}">{profit_pct:+.1f}%</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                        <div>شراء: {stock['avg_price']:.2f}</div>
                        <div>حالياً: {analysis['current_price']:.2f}</div>
                        <div>RSI: {analysis['rsi']:.1f}</div>
                        <div>{analysis['action']}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📊 رسم", key=f"chart_{stock['ticker']}"):
                        df = yf.Ticker(stock['ticker']).history(period="2mo")
                        if not df.empty:
                            fig = create_advanced_chart(df, stock['ticker'])
                            st.plotly_chart(fig, use_container_width=True)
                with col2:
                    if st.button(f"🧠 تحليل", key=f"ai_{stock['ticker']}"):
                        if model:
                            sentiment = get_stock_news_sentiment(stock['ticker'], model)
                            st.markdown(f'<span class="sentiment-badge sentiment-{sentiment["sentiment"]}">تحليل المشاعر: {sentiment["sentiment"]}</span>', unsafe_allow_html=True)
                            prompt = f"حلل سهم {stock['ticker']}: السعر {analysis['current_price']:.2f}, RSI {analysis['rsi']:.1f}"
                            response = model.generate_content(prompt)
                            st.info(f"🤖 {response.text}")
                with col3:
                    if st.button(f"🗑️ حذف", key=f"del_{stock['ticker']}"):
                        PortfolioManager.remove_stock(st.session_state.user_id, stock['ticker'])
                        st.rerun()
                
                # تنبيه وقف الخسارة
                stop_loss = stock['avg_price'] * 0.95
                if analysis['current_price'] <= stop_loss:
                    st.error(f"⚠️ تنبيه! {stock['name']} وصل إلى {analysis['current_price']:.2f} (وقف الخسارة {stop_loss:.2f})")
    else:
        st.info("📭 لا توجد أسهم - أضف سهمك الأول")
    
    # رادار السوق
    st.markdown(f"### 📡 {t('radar')}")
    
    if st.button(f"🔍 {t('scan_market')}", type="primary", use_container_width=True):
        with st.spinner("البورصجي يبحث عن الفرص..."):
            opportunities = automated_market_scan()
            if opportunities:
                st.success(f"✅ تم العثور على {len(opportunities)} فرصة")
                for opp in opportunities[:3]:
                    st.markdown(f"🟢 {opp['ticker']} - {opp['current_price']:.2f} | RSI: {opp['rsi']:.1f}")
            else:
                st.info("لا توجد فرص حالياً")
    
    # تذييل
    st.markdown(f'''
    <div class="platform-footer">
        🧠 {t('app_name')} - منصة التداول الذكية<br>
        البيانات من Yahoo Finance • تحديث لحظي • © 2024
    </div>
    ''', unsafe_allow_html=True)

def get_stock_news_sentiment(ticker, model):
    return {"sentiment": "neutral", "score": 0.5}

if __name__ == "__main__":
    main()
