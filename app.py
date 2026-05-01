# app.py - النسخة النهائية المتكاملة (Production Ready V4.0)
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
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

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
    
    .logo-container {{
        text-align: center;
        padding: 20px;
        margin-bottom: 20px;
    }}
    
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
        color: #888;
    }}
    
    .grid-icon {{
        position: absolute;
        bottom: 20px;
        right: 20px;
        font-size: 40px;
        opacity: 0.1;
    }}
    
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
    
    .badge {{
        display: inline-block;
        background: {accent_color}20;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        color: {accent_color};
        margin: 3px;
    }}
    
    .opportunity-card {{
        background: {card_bg};
        border-left: 4px solid #00ff88;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }}
    
    .platform-footer {{
        text-align: center;
        padding: 30px;
        color: #666;
        font-size: 12px;
        margin-top: 50px;
        border-top: 1px solid {border_color};
    }}
    
    .refresh-indicator {{
        text-align: right;
        font-size: 11px;
        color: #666;
        margin-bottom: 10px;
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
        "scan_market": "مسح السوق الآن",
        "add_stock": "إضافة سهم",
        "ticker": "رمز السهم",
        "price": "السعر",
        "quantity": "الكمية",
        "analyze": "تحليل",
        "delete": "حذف",
        "buy_signal": "إشارة شراء",
        "sell_signal": "إشارة بيع",
        "hold_signal": "انتظار"
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
        "scan_market": "Scan Market Now",
        "add_stock": "Add Stock",
        "ticker": "Ticker",
        "price": "Price",
        "quantity": "Quantity",
        "analyze": "Analyze",
        "delete": "Delete",
        "buy_signal": "Buy Signal",
        "sell_signal": "Sell Signal",
        "hold_signal": "Hold"
    }
}

def t(key):
    return STRINGS[st.session_state.language].get(key, key)

# ====================== الاستيرادات ======================
import time
import json
import sqlite3
from datetime import datetime, timedelta
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
    """تهيئة قاعدة البيانات مع التحقق من وجود المجلد"""
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TIMESTAMP,
            results TEXT
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
    """تحليل سهم واحد مع معالجة الأخطاء"""
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
        
        # تحديد الإشارة
        if rsi < 30:
            signal = "buy"
            action = "🟢 شراء قوي"
            signal_text = t('buy_signal')
        elif rsi < 40:
            signal = "buy_weak"
            action = "🟡 شراء تدريجي"
            signal_text = t('buy_signal')
        elif rsi > 70:
            signal = "sell"
            action = "🔴 بيع"
            signal_text = t('sell_signal')
        elif rsi > 60:
            signal = "sell_weak"
            action = "🟠 مراقبة"
            signal_text = t('sell_signal')
        else:
            signal = "hold"
            action = "⚪ انتظار"
            signal_text = t('hold_signal')
        
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
            "action": action,
            "signal_text": signal_text
        }
    except Exception as e:
        print(f"خطأ في تحليل {ticker}: {e}")
        return None

def create_advanced_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """إنشاء رسم بياني متطور"""
    fig = go.Figure()
    
    # منحنى السعر مع تدرج لوني
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        name='السعر',
        line=dict(color='#00ffcc', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 204, 0.1)
    ))
    
    # المتوسطات المتحركة
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    
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
        title=f'{ticker} - التحليل الفني',
        template='plotly_dark',
        height=400,
        xaxis_title='التاريخ',
        yaxis_title='السعر',
        hovermode='x unified'
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
        """حساب قيمة المحفظة الحالية"""
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

# ====================== رادار السوق (Market Scanner) ======================
MARKET_STOCKS = [
    "COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "EAST.CA",
    "2222.SR", "1120.SR", "7010.SR",
    "AAPL", "MSFT", "TSLA", "NVDA", "GOOGL"
]

def run_market_scanner() -> List[Dict]:
    """مسح السوق واكتشاف فرص الشراء"""
    opportunities = []
    
    for ticker in MARKET_STOCKS:
        analysis = analyze_stock(ticker)
        if analysis and analysis['signal'] in ['buy', 'buy_weak']:
            opportunities.append(analysis)
    
    # ترتيب حسب قوة الإشارة
    opportunities.sort(key=lambda x: 0 if x['signal'] == 'buy' else 1)
    
    # حفظ سجل المسح
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scan_history (scan_date, results) VALUES (?, ?)',
                   (datetime.now(), json.dumps(opportunities, default=str)))
    conn.commit()
    conn.close()
    
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
                    items.append(f'{name}: {price:.0f} <span style="color:{color}">{arrow} {change:+.2f}%</span>')
            except:
                pass
        
        if items:
            st.markdown(f'''
            <div class="ticker-tape">
                🔴 LIVE | {" | ".join(items)} | 🔴 تحديث لحظي
            </div>
            ''', unsafe_allow_html=True)
    except:
        pass

# ====================== التحديث التلقائي ======================
def auto_refresh_callback():
    if st.session_state.auto_refresh:
        time.sleep(60)
        st.rerun()

# ====================== الواجهة الرئيسية ======================

def main():
    model = init_gemini()
    
    # تحديثات تلقائية
    if st.session_state.auto_refresh:
        auto_refresh_callback()
    
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
            if st.button("🌓 تبديل المظهر", use_container_width=True):
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
        st.session_state.auto_refresh = st.checkbox("🔄 تحديث تلقائي كل 60 ثانية", value=st.session_state.auto_refresh)
        
        st.markdown("---")
        
        # إحصائيات سريعة
        portfolio_stocks = PortfolioManager.get_portfolio(st.session_state.user_id)
        st.metric("📊 عدد الأسهم", len(portfolio_stocks))
        
        if model:
            st.success("🧠 Gemini AI: متصل")
        else:
            st.warning("⚠️ أضف مفتاح API في secrets")
    
    # حساب قيمة المحفظة
    portfolio_value = PortfolioManager.get_portfolio_value(st.session_state.user_id)
    
    # شبكة المؤشرات (2x2)
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="grid-card">
        <div class="grid-label">💰 {t('buying_power')}</div>
        <div class="grid-value">{st.session_state.capital - portfolio_value['total_invested']:,.0f}</div>
        <div class="grid-icon">💰</div>
    </div>
    <div class="grid-card">
        <div class="grid-label">📈 {t('investment_value')}</div>
        <div class="grid-value">{portfolio_value['total_current']:,.0f}</div>
        <div class="grid-icon">📈</div>
    </div>
    <div class="grid-card">
        <div class="grid-label">📊 {t('today_profit')}</div>
        <div class="grid-value" style="color: {"#00ff88" if portfolio_value['today_profit'] >= 0 else "#ff4444"}">
            {portfolio_value['today_profit']:+,.0f}
        </div>
        <div class="grid-icon">📊</div>
    </div>
    <div class="grid-card">
        <div class="grid-label">🏆 {t('win_rate')}</div>
        <div class="grid-value">72%</div>
        <div class="grid-icon">🏆</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # تحديث آخر
    st.markdown(f'<div class="refresh-indicator">🕐 آخر تحديث: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    
    # ====================== المحفظة ======================
    st.markdown(f"### 💼 {t('portfolio')}")
    
    with st.expander(f"➕ {t('add_stock')}"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_ticker = st.text_input(t('ticker'), placeholder="COMI.CA").upper()
        with col2:
            new_name = st.text_input("الاسم", placeholder="البنك التجاري")
        with col3:
            buy_price = st.number_input(t('price'), min_value=0.0, step=0.5)
        with col4:
            quantity = st.number_input(t('quantity'), min_value=1, step=1)
        
        if st.button("✨ أضف للمحفظة", use_container_width=True):
            if new_ticker and buy_price and quantity:
                PortfolioManager.add_stock(st.session_state.user_id, new_ticker, new_name or new_ticker, buy_price, int(quantity))
                st.success(f"✅ تم إضافة {new_ticker}")
                time.sleep(1)
                st.rerun()
    
    # عرض الأسهم في المحفظة
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
                            <span style="font-size: 18px; font-weight: bold;">{stock['name']}</span>
                            <span class="badge">{stock['ticker']}</span>
                        </div>
                        <div class="{profit_class}">{profit_pct:+.1f}%</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 12px;">
                        <div>💰 شراء: {stock['avg_price']:.2f}</div>
                        <div>📊 حالياً: {analysis['current_price']:.2f}</div>
                        <div>📈 RSI: {analysis['rsi']:.1f}</div>
                        <div>{analysis['action']}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # أزرار التحكم
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"📊 رسم بياني", key=f"chart_{stock['ticker']}"):
                        df = yf.Ticker(stock['ticker']).history(period="2mo")
                        if not df.empty:
                            fig = create_advanced_chart(df, stock['ticker'])
                            st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if st.button(f"🧠 تحليل AI", key=f"ai_{stock['ticker']}"):
                        if model:
                            with st.spinner("جاري التحليل..."):
                                prompt = f"حلل سهم {stock['name']}: السعر {analysis['current_price']:.2f}, RSI {analysis['rsi']:.1f}"
                                response = model.generate_content(prompt)
                                st.info(f"🤖 **تحليل البورصجي:**\n\n{response.text}")
                        else:
                            st.warning("الذكاء الاصطناعي غير متوفر - أضف مفتاح API")
                
                with col3:
                    if st.button(f"📢 تنبيه", key=f"alert_{stock['ticker']}"):
                        msg = f"🔔 تنبيه للمتابعة: {stock['name']} سعره {analysis['current_price']:.2f}"
                        send_telegram_alert(msg, "info")
                        st.toast("✅ تم إرسال التنبيه إلى تليجرام")
                
                with col4:
                    if st.button(f"🗑️ حذف", key=f"del_{stock['ticker']}"):
                        PortfolioManager.remove_stock(st.session_state.user_id, stock['ticker'])
                        st.rerun()
                
                # تنبيه وقف الخسارة
                stop_loss = stock['avg_price'] * 0.95
                if analysis['current_price'] <= stop_loss:
                    st.error(f"⚠️ **تنبيه وقف الخسارة!** {stock['name']} وصل إلى {analysis['current_price']:.2f} (أقل من {stop_loss:.2f})")
                    if st.session_state.notifications_enabled:
                        send_telegram_alert(f"⚠️ تنبيه: {stock['name']} هبط إلى {analysis['current_price']:.2f}", "danger")
    else:
        st.info("📭 لا توجد أسهم في المحفظة - أضف سهمك الأول")
    
    # ====================== رادار السوق ======================
    st.markdown(f"### 📡 {t('radar')}")
    
    col_scan, col_status = st.columns([1, 3])
    with col_scan:
        if st.button(f"🔍 {t('scan_market')}", type="primary", use_container_width=True):
            with st.spinner("رادار البورصجي يبحث عن الفرص..."):
                opportunities = run_market_scanner()
                st.session_state['scan_results'] = opportunities
                st.success(f"✅ تم العثور على {len(opportunities)} فرصة")
    
    with col_status:
        if st.session_state.get('auto_refresh', False):
            st.caption("🔄 التحديث التلقائي مفعل - سيتم تحديث البيانات كل 60 ثانية")
    
    # عرض نتائج المسح
    if 'scan_results' in st.session_state and st.session_state['scan_results']:
        for opp in st.session_state['scan_results'][:5]:
            st.markdown(f'''
            <div class="opportunity-card">
                🟢 <b>{opp['ticker']}</b> - السعر: {opp['current_price']:.2f} | RSI: {opp['rsi']:.1f} | {opp['action']}
                <div style="font-size: 11px; color: #888; margin-top: 5px;">
                    الدعم: {opp['support']:.2f} | المقاومة: {opp['resistance']:.2f}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # إرسال تنبيه تلقائي للفرص القوية
            if opp['signal'] == 'buy' and st.session_state.notifications_enabled:
                msg = f"🚀 فرصة شراء قوية!\n{opp['ticker']} بسعر {opp['current_price']:.2f}\nRSI: {opp['rsi']:.1f}"
                send_telegram_alert(msg, "success")
    else:
        st.info("اضغط على 'مسح السوق الآن' لاكتشاف فرص الشراء")
    
    # ====================== تذييل ======================
    st.markdown(f'''
    <div class="platform-footer">
        🧠 {t('app_name')} - منصة التداول الذكية<br>
        البيانات من Yahoo Finance • تحديث لحظي • تنبيهات تليجرام • © 2024
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
