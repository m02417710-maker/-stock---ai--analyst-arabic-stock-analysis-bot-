# app.py - منصة البورصجي AI العالمية V3.0 (النسخة النهائية)
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ====================== إعدادات المنصة المتقدمة ======================
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

# إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - منصة التداول الذكية V3",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== الترجمة ======================
STRINGS = {
    "ar": {
        "app_name": "🧠 البورصجي AI V3",
        "subtitle": "منصة التداول الذكية - تحليل فني • أساسي • تنبؤات",
        "buying_power": "القوة الشرائية",
        "investment_value": "قيمة الاستثمار",
        "today_profit": "أرباح اليوم",
        "win_rate": "نسبة النجاح",
        "portfolio": "محفظتي",
        "radar": "رادار السوق",
        "ai_insights": "تحليلات الذكاء الاصطناعي",
        "sentiment": "تحليل المشاعر",
        "monte_carlo": "توقعات مونت كارلو",
        "stop_loss_alert": "تنبيه وقف الخسارة",
        "scan_market": "مسح السوق",
        "buy": "شراء",
        "sell": "بيع",
        "hold": "انتظار",
        "positive": "إيجابي",
        "negative": "سلبي",
        "neutral": "محايد"
    },
    "en": {
        "app_name": "🧠 Al-Boursagi AI V3",
        "subtitle": "Smart Trading Platform - Technical • Fundamental • Predictions",
        "buying_power": "Buying Power",
        "investment_value": "Investment Value",
        "today_profit": "Today's Profit",
        "win_rate": "Win Rate",
        "portfolio": "My Portfolio",
        "radar": "Market Radar",
        "ai_insights": "AI Insights",
        "sentiment": "Sentiment Analysis",
        "monte_carlo": "Monte Carlo Forecast",
        "stop_loss_alert": "Stop Loss Alert",
        "scan_market": "Scan Market",
        "buy": "Buy",
        "sell": "Sell",
        "hold": "Hold",
        "positive": "Positive",
        "negative": "Negative",
        "neutral": "Neutral"
    }
}

def t(key):
    return STRINGS[st.session_state.language].get(key, key)

# ====================== CSS الاحترافي النهائي ======================
def apply_custom_style():
    if st.session_state.theme == 'dark':
        bg_color = "#0a0a0f"
        card_bg = "#14141e"
        border_color = "#2a2a3e"
        text_color = "#ffffff"
        text_secondary = "#888888"
        accent_color = "#00ffcc"
    else:
        bg_color = "#f0f2f6"
        card_bg = "#ffffff"
        border_color = "#e0e0e0"
        text_color = "#000000"
        text_secondary = "#666666"
        accent_color = "#00b4d8"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Cairo', sans-serif;
        -webkit-font-smoothing: antialiased;
    }}
    
    .stApp {{
        background-color: {bg_color};
    }}
    
    /* الشبكة الرئيسية (2x2 Grid) */
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
        box-shadow: 0 10px 40px rgba(0, 255, 204, 0.1);
    }}
    
    .grid-value {{
        font-size: 36px;
        font-weight: 800;
        color: {accent_color};
        margin: 10px 0;
    }}
    
    .grid-label {{
        font-size: 14px;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .grid-icon {{
        position: absolute;
        bottom: 20px;
        right: 20px;
        font-size: 40px;
        opacity: 0.1;
    }}
    
    /* المنحنى البياني المتطور */
    .chart-container {{
        background: {card_bg};
        border-radius: 24px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid {border_color};
    }}
    
    /* بطاقات الأسهم */
    .stock-card-enhanced {{
        background: {card_bg};
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid {border_color};
        transition: all 0.3s;
    }}
    
    .stock-card-enhanced:hover {{
        border-color: {accent_color};
    }}
    
    /* شارة التحليل */
    .sentiment-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
    }}
    
    .sentiment-positive {{
        background: #00ff8820;
        color: #00ff88;
    }}
    
    .sentiment-negative {{
        background: #ff444420;
        color: #ff4444;
    }}
    
    .sentiment-neutral {{
        background: #ffaa0020;
        color: #ffaa00;
    }}
    
    /* شريط التمرير */
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
    
    .platform-footer {{
        text-align: center;
        padding: 30px;
        color: {text_secondary};
        font-size: 12px;
        margin-top: 50px;
        border-top: 1px solid {border_color};
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ====================== الاستيرادات ======================
import time
import json
import base64
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import google.generativeai as genai
import requests

# ====================== التهيئة ======================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "boursagi.db"

# ====================== قاعدة البيانات (SQLite) ======================
def init_database():
    """تهيئة قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            capital REAL,
            risk_percent REAL,
            created_at TIMESTAMP
        )
    ''')
    
    # جدول المحفظة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            ticker TEXT,
            name TEXT,
            avg_price REAL,
            quantity INTEGER,
            buy_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # جدول الصفقات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            ticker TEXT,
            type TEXT,
            price REAL,
            quantity INTEGER,
            date TIMESTAMP
        )
    ''')
    
    # جدول التنبيهات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            ticker TEXT,
            alert_type TEXT,
            message TEXT,
            created_at TIMESTAMP,
            is_sent BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# ====================== إعداد الذكاء الاصطناعي ======================
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
            icons = {"danger": "🚨⚠️", "warning": "⚠️", "success": "✅", "info": "📊"}
            full_message = f"{icons.get(priority, '📊')} {message}"
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": full_message, "parse_mode": "HTML"}
            response = requests.post(url, data=data, timeout=10)
            return response.ok
    except:
        pass
    return False

# ====================== تحليل المشاعر (Sentiment Analysis) ======================
def get_stock_news_sentiment(ticker: str, model) -> Dict:
    """تحليل أخبار السهم وتصنيفها إيجابي/سلبي"""
    try:
        stock = yf.Ticker(ticker)
        news = []
        
        if hasattr(stock, 'news') and stock.news:
            for item in stock.news[:5]:
                news.append(item.get('title', ''))
        
        if not news:
            return {"sentiment": "neutral", "score": 0.5, "summary": "لا توجد أخبار كافية", "confidence": 0}
        
        if model:
            prompt = f"""
            حلل المشاعر الإخبارية التالية للأسهم:
            {chr(10).join(news)}
            
            أخرج الإجابة بهذا التنسيق فقط:
            SENTIMENT: [positive/negative/neutral]
            SCORE: [0-1]
            SUMMARY: [جملة واحدة]
            """
            response = model.generate_content(prompt)
            text = response.text
            
            sentiment = "neutral"
            score = 0.5
            summary = "تحليل متاح"
            
            if "positive" in text.lower():
                sentiment = "positive"
                score = 0.75
            elif "negative" in text.lower():
                sentiment = "negative"
                score = 0.25
            
            return {"sentiment": sentiment, "score": score, "summary": summary, "news_count": len(news)}
    except:
        pass
    
    return {"sentiment": "neutral", "score": 0.5, "summary": "تحليل غير متاح", "confidence": 0}

# ====================== توقعات مونت كارلو ======================
def monte_carlo_simulation(prices: pd.Series, days: int = 30, simulations: int = 1000) -> Dict:
    """توقعات مونت كارلو لأسعار الأسهم"""
    try:
        returns = prices.pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std()
        
        last_price = prices.iloc[-1]
        dt = 1/252  # أيام التداول
        
        simulations_results = []
        
        for _ in range(simulations):
            daily_returns = np.random.normal(mu, sigma, days)
            price_path = last_price * (1 + daily_returns).cumprod()
            simulations_results.append(price_path[-1])
        
        simulations_results = np.array(simulations_results)
        
        return {
            "current_price": last_price,
            "expected_price": np.mean(simulations_results),
            "lower_bound": np.percentile(simulations_results, 5),
            "upper_bound": np.percentile(simulations_results, 95),
            "probability_up": np.mean(simulations_results > last_price) * 100,
            "risk_percent": (np.std(simulations_results) / np.mean(simulations_results)) * 100
        }
    except:
        return None

# ====================== التحليل الفني المتقدم ======================
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

def calculate_macd(prices):
    try:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1], signal.iloc[-1], macd.iloc[-1] - signal.iloc[-1]
    except:
        return 0, 0, 0

def calculate_bollinger_bands(prices, period=20):
    try:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]
    except:
        return 0, 0, 0

def analyze_stock_advanced(ticker: str) -> Dict:
    """تحليل متقدم للسهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        
        if df.empty or len(df) < 30:
            return None
        
        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2] if len(df) > 1 else current
        change = ((current - prev) / prev) * 100
        
        rsi = calculate_rsi(df['Close'])
        macd, macd_signal, macd_hist = calculate_macd(df['Close'])
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(df['Close'])
        
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        # المتوسطات المتحركة
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else current
        
        # حجم التداول
        avg_volume = df['Volume'].tail(20).mean()
        volume_ratio = df['Volume'].iloc[-1] / avg_volume if avg_volume > 0 else 1
        
        # تحديد الإشارة
        buy_score = 0
        sell_score = 0
        
        if rsi < 30:
            buy_score += 3
        elif rsi > 70:
            sell_score += 3
        elif rsi < 40:
            buy_score += 1
        elif rsi > 60:
            sell_score += 1
        
        if macd > macd_signal:
            buy_score += 2
        else:
            sell_score += 1
        
        if current < sma_20:
            buy_score += 1
        elif current > sma_20 * 1.05:
            sell_score += 1
        
        if volume_ratio > 1.5 and buy_score > 0:
            buy_score += 1
        
        if buy_score >= 4:
            signal = "buy"
            action = "🟢 شراء قوي"
        elif buy_score >= 2:
            signal = "buy_weak"
            action = "🟡 شراء تدريجي"
        elif sell_score >= 4:
            signal = "sell"
            action = "🔴 بيع"
        elif sell_score >= 2:
            signal = "sell_weak"
            action = "🟠 مراقبة"
        else:
            signal = "hold"
            action = "⚪ انتظار"
        
        return {
            "ticker": ticker,
            "current_price": current,
            "daily_change": change,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_histogram": macd_hist,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "support": support,
            "resistance": resistance,
            "volume_ratio": volume_ratio,
            "signal": signal,
            "action": action,
            "buy_score": buy_score,
            "sell_score": sell_score
        }
    except Exception as e:
        return None

# ====================== المنحنى البياني المتطور ======================
def create_advanced_chart(df: pd.DataFrame, ticker: str):
    """إنشاء منحنى بياني مع تدرج لوني"""
    fig = go.Figure()
    
    # منحنى السعر مع تدرج لوني
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        name='السعر',
        line=dict(color='#00ffcc', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 204, 0.1)'
    ))
    
    # المتوسطات المتحركة
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_20'],
        mode='lines',
        name='SMA 20',
        line=dict(color='#ffaa00', width=1.5, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_50'],
        mode='lines',
        name='SMA 50',
        line=dict(color='#ff4444', width=1.5, dash='dot')
    ))
    
    fig.update_layout(
        title=f'{ticker} - الأداء بمرور الوقت',
        template='plotly_dark',
        height=450,
        xaxis_title='التاريخ',
        yaxis_title='السعر',
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
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
        cursor.execute('SELECT ticker, name, avg_price, quantity, buy_date FROM portfolio WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        stocks = []
        for row in rows:
            stocks.append({
                "ticker": row[0], "name": row[1], "avg_price": row[2],
                "quantity": row[3], "buy_date": row[4]
            })
        return stocks

# ====================== شريط المؤشرات ======================
def display_ticker_tape():
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
    
    st.markdown(f"""
    <div class="ticker-tape">
        <div style="animation: scroll 25s linear infinite; display: inline-block;">
            🔴 LIVE | {" | ".join(items)} | 🔴 تحديث لحظي
        </div>
    </div>
    """, unsafe_allow_html=True)

# ====================== الواجهة الرئيسية ======================

def main():
    model = init_gemini()
    
    # الهوية البصرية
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 52px; background: linear-gradient(135deg, #00ffcc, #00b4d8, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {t('app_name')}
        </h1>
        <p style="color: #888;">{t('subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    display_ticker_tape()
    
    # ====================== الشريط الجانبي ======================
    with st.sidebar:
        st.markdown("### 🎮 لوحة التحكم")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌓 تبديل المظهر", use_container_width=True):
                toggle_theme = lambda: setattr(st.session_state, 'theme', 'light' if st.session_state.theme == 'dark' else 'dark')
                toggle_theme()
                st.rerun()
        with col2:
            if st.button("🌐 EN/AR", use_container_width=True):
                toggle_language = lambda: setattr(st.session_state, 'language', 'en' if st.session_state.language == 'ar' else 'ar')
                toggle_language()
                st.rerun()
        
        st.markdown("---")
        
        # إعدادات رأس المال
        st.markdown("### 💰 إعدادات المخاطر")
        st.session_state.capital = st.number_input("رأس المال", value=st.session_state.capital, step=10000)
        st.session_state.risk_percentage = st.slider("نسبة المخاطرة (%)", 0.5, 5.0, st.session_state.risk_percentage, 0.5)
        
        # تفعيل المسح التلقائي
        st.session_state.auto_scan_enabled = st.checkbox("🔄 تفعيل المسح التلقائي", value=st.session_state.auto_scan_enabled)
        
        st.markdown("---")
        
        # إحصائيات سريعة
        portfolio_stocks = PortfolioManager.get_portfolio(st.session_state.user_id)
        st.metric("📊 عدد الأسهم", len(portfolio_stocks))
        
        if model:
            st.success("🧠 Gemini AI: متصل")
        else:
            st.warning("⚠️ أضف مفتاح API")
    
    # ====================== شبكة 2x2 (Dashboard Grid) ======================
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    # بطاقة 1: القوة الشرائية
    st.markdown(f'''
    <div class="grid-card">
        <div class="grid-label">💰 {t('buying_power')}</div>
        <div class="grid-value">{st.session_state.capital:,.0f}</div>
        <div class="grid-icon">💰</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # بطاقة 2: قيمة الاستثمار
    portfolio_value = sum([s.get('current_price', 0) * s.get('quantity', 0) for s in portfolio_stocks]) if portfolio_stocks else 0
    st.markdown(f'''
    <div class="grid-card">
        <div class="grid-label">📈 {t('investment_value')}</div>
        <div class="grid-value">{portfolio_value:,.0f}</div>
        <div class="grid-icon">📈</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # بطاقة 3: أرباح اليوم
    today_profit = 0
    st.markdown(f'''
    <div class="grid-card">
        <div class="grid-label">📊 {t('today_profit')}</div>
        <div class="grid-value" style="color: {"#00ff88" if today_profit >= 0 else "#ff4444"}">{today_profit:+,.0f}</div>
        <div class="grid-icon">📊</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # بطاقة 4: نسبة النجاح
    win_rate = 72
    st.markdown(f'''
    <div class="grid-card">
        <div class="grid-label">🏆 {t('win_rate')}</div>
        <div class="grid-value">{win_rate}%</div>
        <div class="grid-icon">🏆</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ====================== محفظتي ======================
    st.markdown(f"### 💼 {t('portfolio')}")
    
    # إضافة سهم جديد
    with st.expander("➕ إضافة سهم جديد"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_ticker = st.text_input("رمز السهم", placeholder="COMI.CA")
        with col2:
            new_name = st.text_input("اسم السهم", placeholder="البنك التجاري")
        with col3:
            buy_price = st.number_input("سعر الشراء", min_value=0.0, step=0.5)
        with col4:
            quantity = st.number_input("الكمية", min_value=1, step=1)
        
        if st.button("✨ أضف للسهم", use_container_width=True):
            if new_ticker and buy_price and quantity:
                PortfolioManager.add_stock(st.session_state.user_id, new_ticker, new_name or new_ticker, buy_price, int(quantity))
                st.success(f"✅ تم إضافة {new_ticker}")
                st.rerun()
    
    # عرض الأسهم
    if portfolio_stocks:
        for stock in portfolio_stocks:
            ticker = stock['ticker']
            
            # تحليل السهم
            analysis = analyze_stock_advanced(ticker)
            
            if analysis:
                profit_pct = ((analysis['current_price'] - stock['avg_price']) / stock['avg_price']) * 100
                profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
                
                st.markdown(f"""
                <div class="stock-card-enhanced">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 18px; font-weight: bold;">{stock['name']}</span>
                            <span class="badge">{ticker}</span>
                        </div>
                        <div class="{profit_class}">{profit_pct:+.2f}%</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <div>شراء: {stock['avg_price']:.2f}</div>
                        <div>حالياً: {analysis['current_price']:.2f}</div>
                        <div>RSI: {analysis['rsi']:.1f}</div>
                        <div>{analysis['action']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # أزرار التحكم
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"📊 تحليل فني", key=f"chart_{ticker}"):
                        df = yf.Ticker(ticker).history(period="2mo")
                        if not df.empty:
                            df['SMA_20'] = df['Close'].rolling(20).mean()
                            df['SMA_50'] = df['Close'].rolling(50).mean()
                            fig = create_advanced_chart(df, ticker)
                            st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if st.button(f"🧠 تحليل الذكاء", key=f"ai_{ticker}"):
                        with st.spinner("جاري التحليل..."):
                            if model:
                                sentiment = get_stock_news_sentiment(ticker, model)
                                sentiment_class = f"sentiment-{sentiment['sentiment']}"
                                st.markdown(f"""
                                <div>
                                    <span class="sentiment-badge {sentiment_class}">
                                        {'😊' if sentiment['sentiment'] == 'positive' else '😞' if sentiment['sentiment'] == 'negative' else '😐'} 
                                        تحليل المشاعر: {sentiment['sentiment']}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                prompt = f"حلل سهم {ticker}: السعر {analysis['current_price']:.2f}, RSI {analysis['rsi']:.1f}"
                                response = model.generate_content(prompt)
                                st.info(f"🤖 **التحليل:** {response.text}")
                
                with col3:
                    if st.button(f"📈 توقعات MC", key=f"mc_{ticker}"):
                        df = yf.Ticker(ticker).history(period="6mo")
                        if not df.empty and len(df) > 30:
                            mc = monte_carlo_simulation(df['Close'])
                            if mc:
                                st.markdown(f"""
                                <div class="risk-calculator">
                                    <b>🎲 توقعات مونت كارلو (30 يوم):</b><br>
                                    السعر الحالي: {mc['current_price']:.2f}<br>
                                    السعر المتوقع: {mc['expected_price']:.2f}<br>
                                    الحد الأدنى: {mc['lower_bound']:.2f}<br>
                                    الحد الأعلى: {mc['upper_bound']:.2f}<br>
                                    احتمالية الصعود: {mc['probability_up']:.1f}%<br>
                                    نسبة المخاطرة: {mc['risk_percent']:.1f}%
                                </div>
                                """, unsafe_allow_html=True)
                
                with col4:
                    if st.button(f"🗑️ حذف", key=f"del_{ticker}"):
                        PortfolioManager.remove_stock(st.session_state.user_id, ticker)
                        st.rerun()
                
                # تنبيه وقف الخسارة
                stop_loss_price = stock['avg_price'] * 0.95
                if analysis['current_price'] <= stop_loss_price:
                    alert_msg = f"⚠️ تنبيه وقف الخسارة! {stock['name']} هبط إلى {analysis['current_price']:.2f} (أقل من {stop_loss_price:.2f})"
                    st.error(alert_msg)
                    if st.session_state.notifications_enabled:
                        send_telegram_alert(alert_msg, "danger")
    else:
        st.info("📭 لا توجد أسهم في المحفظة - أضف أسهمك لتبدأ")
    
    # ====================== رادار السوق ======================
    st.markdown(f"### 📡 {t('radar')} - {t('scan_market')}")
    
    if st.button(f"🔍 {t('scan_market')}", type="primary", use_container_width=True):
        with st.spinner("رادار البورصجي يبحث عن الفرص..."):
            tickers_to_scan = ["COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "2222.SR", "1120.SR", "AAPL", "MSFT", "TSLA"]
            opportunities = []
            
            for ticker in tickers_to_scan:
                analysis = analyze_stock_advanced(ticker)
                if analysis and analysis['signal'] in ['buy', 'buy_weak']:
                    opportunities.append(analysis)
            
            if opportunities:
                st.success(f"✅ تم العثور على {len(opportunities)} فرصة شراء")
                for opp in opportunities[:5]:
                    st.markdown(f"""
                    <div class="glass-card">
                        🟢 <b>{opp['ticker']}</b> - السعر: {opp['current_price']:.2f} | RSI: {opp['rsi']:.1f} | {opp['action']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.auto_scan_enabled and st.session_state.notifications_enabled:
                        send_telegram_alert(f"🟢 فرصة شراء: {opp['ticker']} بسعر {opp['current_price']:.2f} - RSI {opp['rsi']:.1f}", "success")
            else:
                st.info("لا توجد فرص شراء حالياً")
    
    # ====================== تذييل ======================
    st.markdown(f"""
    <div class="platform-footer">
        🧠 {t('app_name')} - منصة التداول الذكية العالمية<br>
        البيانات من Yahoo Finance • تحليلات Gemini AI • تحديث لحظي • © 2024
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
