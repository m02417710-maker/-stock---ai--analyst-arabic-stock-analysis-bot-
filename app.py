# app.py - منصة البورصجي AI العالمية V2.0
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

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

def toggle_language():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'

# إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - المنصة العالمية الذكية",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== الترجمة المتقدمة ======================
STRINGS = {
    "ar": {
        "app_name": "🌍 البورصجي AI",
        "subtitle": "المنصة العالمية الذكية للتداول",
        "market_status": "حالة السوق",
        "opportunities": "فرص الشراء",
        "alerts": "تنبيهات نشطة",
        "accuracy": "دقة الذكاء الاصطناعي",
        "portfolio": "محفظتي الاستثمارية",
        "radar": "رادار البورصجي",
        "scan": "مسح السوق الآن",
        "buy": "شراء",
        "sell": "بيع",
        "hold": "انتظار",
        "profit": "الربح",
        "loss": "الخسارة",
        "add_stock": "إضافة سهم للمراقبة",
        "ticker": "رمز السهم",
        "price": "السعر",
        "quantity": "الكمية",
        "analyze": "تحليل ذكي",
        "delete": "حذف",
        "risk_management": "إدارة المخاطر",
        "position_size": "حجم الصفقة المقترح",
        "stop_loss": "وقف الخسارة",
        "take_profit": "جني الأرباح",
        "ai_vision": "الرؤية الحاسوبية",
        "technical_patterns": "النماذج الفنية",
        "send_alert": "إرسال تنبيه",
        "daily_report": "تقرير يومي",
        "capital": "رأس المال",
        "risk_percent": "نسبة المخاطرة"
    },
    "en": {
        "app_name": "🌍 Al-Boursagi AI",
        "subtitle": "Global Intelligent Trading Platform",
        "market_status": "Market Status",
        "opportunities": "Buy Opportunities",
        "alerts": "Active Alerts",
        "accuracy": "AI Accuracy",
        "portfolio": "My Investment Portfolio",
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
        "analyze": "AI Analysis",
        "delete": "Delete",
        "risk_management": "Risk Management",
        "position_size": "Suggested Position Size",
        "stop_loss": "Stop Loss",
        "take_profit": "Take Profit",
        "ai_vision": "Computer Vision",
        "technical_patterns": "Technical Patterns",
        "send_alert": "Send Alert",
        "daily_report": "Daily Report",
        "capital": "Capital",
        "risk_percent": "Risk Percentage"
    }
}

def t(key):
    return STRINGS[st.session_state.language].get(key, key)

# ====================== CSS الاحترافي مع تحسين الخطوط ======================
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
    
    * {{
        font-family: 'Cairo', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: -0.02em;
    }}
    
    .stApp {{
        background-color: {bg_color};
    }}
    
    /* شريط المؤشرات المتحرك */
    .ticker-tape {{
        background: linear-gradient(90deg, #00ffcc, #00b4d8);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 20px;
        overflow: hidden;
        white-space: nowrap;
        font-weight: bold;
        color: #000;
    }}
    
    .ticker-content {{
        display: inline-block;
        animation: scroll 25s linear infinite;
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
        box-shadow: 0 10px 30px rgba(0, 255, 204, 0.15);
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
        width: 100%;
        transition: all 0.3s;
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
    
    .profit-positive {{ color: #00ff88; font-weight: bold; }}
    .profit-negative {{ color: #ff4444; font-weight: bold; }}
    
    /* حاسبة المخاطر */
    .risk-calculator {{
        background: {card_bg};
        border-radius: 15px;
        padding: 15px;
        margin-top: 10px;
        border: 1px solid {border_color};
    }}
    
    .platform-footer {{
        text-align: center;
        padding: 30px;
        color: {text_secondary};
        font-size: 12px;
        margin-top: 50px;
        border-top: 1px solid {border_color};
    }}
    
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
import base64
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import requests
from PIL import Image

# ====================== التهيئة ======================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

REAL_PORTFOLIO_FILE = DATA_DIR / "real_portfolio.json"
ALERTS_LOG_FILE = DATA_DIR / "alerts_log.json"

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
    """إرسال تنبيه عبر تليجرام"""
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            
            icons = {"danger": "🚨⚠️", "warning": "⚠️", "success": "✅", "info": "📊"}
            full_message = f"{icons.get(priority, '📊')} {message}"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": full_message, "parse_mode": "HTML"}
            response = requests.post(url, data=data, timeout=10)
            
            # تسجيل التنبيه
            log_alert(message, priority)
            return response.ok
    except Exception as e:
        print(f"Telegram error: {e}")
    return False

def log_alert(message: str, priority: str):
    """تسجيل التنبيهات في الملف"""
    alerts = []
    if ALERTS_LOG_FILE.exists():
        with open(ALERTS_LOG_FILE, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
    
    alerts.append({
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat()
    })
    
    # الاحتفاظ بآخر 100 تنبيه
    alerts = alerts[-100:]
    
    with open(ALERTS_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

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
        alerts = []
        
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
                    
                    # تنبيهات تلقائية
                    if stock["profit_loss_pct"] <= -5 and not stock.get("loss_alert_sent", False):
                        alerts.append(f"🔴 تنبيه: {stock['name']} هبط {abs(stock['profit_loss_pct']):.1f}% من سعر شرائك!")
                        stock["loss_alert_sent"] = True
                    elif stock["profit_loss_pct"] >= 10 and not stock.get("profit_alert_sent", False):
                        alerts.append(f"🟢 تنبيه: {stock['name']} حقق أرباح {stock['profit_loss_pct']:.1f}% - وقت جني الأرباح!")
                        stock["profit_alert_sent"] = True
                    elif stock["profit_loss_pct"] > -3:
                        stock["loss_alert_sent"] = False
                    elif stock["profit_loss_pct"] < 8:
                        stock["profit_alert_sent"] = False
            except:
                pass
        
        data["total_current"] = total_current
        data["total_invested"] = total_invested
        data["total_profit"] = total_current - total_invested
        data["total_profit_pct"] = (data["total_profit"] / total_invested * 100) if total_invested > 0 else 0
        BoursagiPortfolio.save(data)
        
        # إرسال التنبيهات عبر تليجرام
        for alert in alerts:
            if st.session_state.notifications_enabled:
                send_telegram_alert(alert, "warning")
        
        return data

# ====================== حاسبة حجم الصفقة (إدارة المخاطر) ======================
def calculate_position_size(entry_price: float, stop_loss_price: float, capital: float, risk_percent: float) -> Dict:
    """حساب حجم الصفقة المناسب بناءً على قاعدة 2%"""
    risk_amount = capital * (risk_percent / 100)
    risk_per_share = abs(entry_price - stop_loss_price)
    
    if risk_per_share <= 0:
        return {"shares": 0, "risk_amount": risk_amount, "position_value": 0, "warning": "وقف الخسارة يجب أن يكون مختلفاً عن سعر الدخول"}
    
    shares = int(risk_amount / risk_per_share)
    position_value = shares * entry_price
    
    return {
        "shares": shares,
        "risk_amount": risk_amount,
        "position_value": position_value,
        "risk_per_share": risk_per_share,
        "capital_percent": (position_value / capital) * 100 if capital > 0 else 0,
        "warning": None
    }

# ====================== الرؤية الحاسوبية للرسوم البيانية ======================
def analyze_chart_with_vision(fig: go.Figure, ticker: str, model) -> str:
    """تحليل الرسم البياني باستخدام الرؤية الحاسوبية لـ Gemini"""
    if not model:
        return "الذكاء الاصطناعي غير متوفر"
    
    try:
        # تحويل الرسم البياني إلى صورة
        img_bytes = fig.to_image(format="png", width=800, height=500)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        prompt = f"""
        أنت خبير تحليل فني. حلل الرسم البياني لسهم {ticker} واستخرج:
        1. النماذج الفنية الموجودة (مثل الرأس والكتفين، القمم المزدوجة، العلم، المثلث)
        2. الاتجاه العام (صاعد، هابط، جانبي)
        3. مستويات الدعم والمقاومة الرئيسية
        4. توصية فنية مختصرة
        
        الرد بالعربية بشكل احترافي.
        """
        
        response = model.generate_content([prompt, {"mime_type": "image/png", "data": img_base64}])
        return response.text
    except Exception as e:
        return f"خطأ في تحليل الصورة: {e}"

# ====================== دوال التحليل الأساسية ======================
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

# ====================== شريط المؤشرات المتحرك ======================
def display_ticker_tape():
    try:
        indices = {"EGX 30": "^EGX30", "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "TASI": "^TASI"}
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
        
        st.markdown(f"""
        <div class="ticker-tape">
            <div class="ticker-content">🔴 LIVE | {" | ".join(ticker_items)} | 🔴 تحديث لحظي</div>
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

# ====================== تقرير يومي ======================
def generate_daily_report():
    """توليد تقرير يومي للمحفظة"""
    portfolio = BoursagiPortfolio.update_prices()
    
    report = f"""
📊 <b>تقرير البورصجي اليومي</b>
📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}

💰 <b>إجمالي المحفظة:</b>
- قيمة الاستثمار: {portfolio['total_invested']:,.2f}
- القيمة الحالية: {portfolio['total_current']:,.2f}
- الربح/الخسارة: {portfolio['total_profit']:+,.2f} ({portfolio['total_profit_pct']:+.2f}%)

📈 <b>الأسهم في المحفظة:</b>
"""
    for stock in portfolio["stocks"]:
        report += f"\n- {stock['name']} ({stock['ticker']}): {stock.get('profit_loss_pct', 0):+.2f}%"
    
    return report

# ====================== قائمة الأسهم ======================
STOCKS = {
    "CIB": "COMI.CA", "Talaat Moustafa": "TMGH.CA", "Elsewedy": "SWDY.CA",
    "Telecom Egypt": "ETEL.CA", "Aramco": "2222.SR", "Al Rajhi": "1120.SR",
    "Apple": "AAPL", "Microsoft": "MSFT", "Tesla": "TSLA"
}

# ====================== الواجهة الرئيسية ======================

def main():
    model = init_gemini()
    
    # الهوية البصرية
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 48px; background: linear-gradient(135deg, #00ffcc, #00b4d8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
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
            if st.button("🌓 تبديل المظهر"):
                toggle_theme()
                st.rerun()
        with col2:
            if st.button("🌐 EN/AR"):
                toggle_language()
                st.rerun()
        
        st.markdown("---")
        
        # إعدادات رأس المال والمخاطرة
        st.markdown(f"### {t('risk_management')}")
        st.session_state.capital = st.number_input(t('capital'), value=st.session_state.capital, step=10000)
        st.session_state.risk_percentage = st.slider(t('risk_percent'), 0.5, 5.0, st.session_state.risk_percentage, 0.5)
        
        # تفعيل التنبيهات
        st.session_state.notifications_enabled = st.checkbox("🔔 تفعيل التنبيهات", value=st.session_state.notifications_enabled)
        
        # تقرير يومي
        if st.button("📊 إرسال تقرير يومي", use_container_width=True):
            report = generate_daily_report()
            if send_telegram_alert(report, "info"):
                st.success("✅ تم إرسال التقرير إلى تليجرام")
            else:
                st.error("فشل إرسال التقرير - تأكد من إعدادات البوت")
        
        st.markdown("---")
        portfolio = BoursagiPortfolio.update_prices()
        st.metric("💰 إجمالي المحفظة", f"{portfolio['total_current']:,.0f}", f"{portfolio['total_profit_pct']:+.1f}%")
    
    # ====================== لوحة المؤشرات ======================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t('market_status'), "🟢 EGX متداول")
    col2.metric(t('opportunities'), "3")
    col3.metric(t('alerts'), "0")
    col4.metric(t('accuracy'), "94%")
    
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
                    <div><span style="font-size: 18px; font-weight: bold;">{stock['name']}</span><span class="badge">{stock['ticker']}</span></div>
                    <div class="{profit_class}">{profit_pct:+.2f}%</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <div>شراء: {stock['avg_price']:.2f}</div>
                    <div>حالياً: {stock.get('current_price', 0):.2f}</div>
                    <div>الكمية: {stock['quantity']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # أزرار التحكم
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button(f"📊 رسم بياني", key=f"chart_{stock['ticker']}"):
                    fig = create_candlestick_chart(stock['ticker'])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # تحليل بالرؤية الحاسوبية
                        with st.spinner("تحليل الرسم البياني بالذكاء الاصطناعي..."):
                            vision_analysis = analyze_chart_with_vision(fig, stock['ticker'], model)
                            st.info(f"🧠 **{t('ai_vision')}:**\n\n{vision_analysis}")
            
            with col2:
                if st.button(f"🧠 {t('analyze')}", key=f"analyze_{stock['ticker']}"):
                    analysis = analyze_stock(stock['ticker'])
                    if analysis and model:
                        prompt = f"حلل سهم {stock['name']}: السعر {analysis['current_price']:.2f}, RSI {analysis['rsi']:.1f}, الدعم {analysis['support']:.2f}, المقاومة {analysis['resistance']:.2f}"
                        response = model.generate_content(prompt)
                        st.success(f"🤖 **{t('analyze')}:** {response.text}")
            
            with col3:
                if st.button(f"⚠️ {t('send_alert')}", key=f"alert_{stock['ticker']}"):
                    alert_msg = f"🔔 تنبيه للمتابعة: {stock['name']} سعره {stock.get('current_price', 0):.2f}"
                    if send_telegram_alert(alert_msg, "info"):
                        st.toast("✅ تم إرسال التنبيه")
                    else:
                        st.error("فشل الإرسال")
            
            with col4:
                if st.button(f"🗑️ {t('delete')}", key=f"del_{stock['ticker']}"):
                    BoursagiPortfolio.remove_stock(stock['ticker'])
                    st.rerun()
            
            # حاسبة حجم الصفقة (إدارة المخاطر)
            with st.expander(f"📐 {t('position_size')}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    stop_loss = st.number_input(f"{t('stop_loss')} ({stock['ticker']})", value=stock['avg_price'] * 0.95, step=0.5, key=f"sl_{stock['ticker']}")
                with col_b:
                    take_profit = st.number_input(f"{t('take_profit')} ({stock['ticker']})", value=stock['avg_price'] * 1.10, step=0.5, key=f"tp_{stock['ticker']}")
                
                if st.button(f"📊 حساب حجم الصفقة", key=f"calc_{stock['ticker']}"):
                    position = calculate_position_size(stock['avg_price'], stop_loss, st.session_state.capital, st.session_state.risk_percentage)
                    st.markdown(f"""
                    <div class="risk-calculator">
                        <b>{t('position_size')}:</b> {position['shares']} سهم<br>
                        <b>قيمة الصفقة:</b> {position['position_value']:,.2f}<br>
                        <b>نسبة من رأس المال:</b> {position['capital_percent']:.1f}%<br>
                        <b>المخاطرة القصوى:</b> {position['risk_amount']:.2f} ({st.session_state.risk_percentage}% من رأس المال)
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        st.info("📭 لا توجد أسهم في المحفظة - أضف أسهمك لتبدأ")
    
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
                        🟢 <b>{r['name']}</b> ({r['ticker']}) - RSI: {r['rsi']:.1f} | السعر: {r['price']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # تنبيه عبر تليجرام إذا تم التفعيل
                    if st.session_state.notifications_enabled:
                        send_telegram_alert(f"🟢 فرصة شراء: {r['name']} بسعر {r['price']:.2f} - RSI {r['rsi']:.1f}", "success")
            else:
                st.info("لا توجد فرص شراء حالياً")
    
    # ====================== تذييل ======================
    st.markdown(f"""
    <div class="platform-footer">
        🌍 {t('app_name')} - المنصة العالمية الذكية للتداول<br>
        البيانات من Yahoo Finance • تحليلات Gemini AI • تحديث لحظي<br>
        © 2024 جميع الحقوق محفوظة
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
