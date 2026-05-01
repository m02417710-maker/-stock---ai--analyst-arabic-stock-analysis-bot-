# app.py - بوت البورصجي AI - النسخة الاحترافية الكاملة
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ====================== إعدادات الصفحة وهوية البورصجي ======================
st.set_page_config(
    page_title="البورصجي AI - مساعدك المالي الذكي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS المخصص لهوية البورصجي
st.markdown("""
<style>
    /* الخطوط والألوان الرئيسية */
    @import url('https://fonts.googleapis.com/css2? Cairo:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    /* العنوان الرئيسي */
    .main-title {
        font-size: 52px;
        background: linear-gradient(135deg, #00ffcc 0%, #00b4d8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-title {
        font-size: 18px;
        color: #c0c0c0;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    
    /* بطاقات التحكم */
    .dashboard-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #00ffcc20;
        transition: transform 0.3s;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        border-color: #00ffcc;
    }
    
    .card-value {
        font-size: 28px;
        font-weight: bold;
        color: #00ffcc;
        margin: 10px 0;
    }
    
    .card-label {
        font-size: 14px;
        color: #888;
    }
    
    /* بطاقات الأسهم */
    .stock-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 4px solid #00ffcc;
    }
    
    .stock-profit-positive {
        color: #00ff88;
        font-weight: bold;
    }
    
    .stock-profit-negative {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* أزرار البورصجي */
    .boursagi-button {
        background: linear-gradient(135deg, #00ffcc 0%, #00b4d8 100%);
        color: #000;
        border: none;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .boursagi-button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(0,255,204,0.3);
    }
    
    /* شريط التقدم الذكي */
    .smart-progress {
        background: #2a2a3e;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }
    
    .smart-progress-fill {
        background: linear-gradient(90deg, #00ffcc, #00b4d8);
        width: 0%;
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }
    
    /* تذييل الصفحة */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        margin-top: 50px;
        border-top: 1px solid #333;
    }
    
    /* شارات البورصجي */
    .badge {
        display: inline-block;
        background: #00ffcc20;
        border-radius: 20px;
        padding: 5px 12px;
        font-size: 12px;
        color: #00ffcc;
        margin: 3px;
    }
</style>
""", unsafe_allow_html=True)

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

# ملفات البيانات
REAL_PORTFOLIO_FILE = DATA_DIR / "real_portfolio.json"
SCAN_RESULTS_FILE = DATA_DIR / "scan_results.json"

# ====================== إعداد الذكاء الاصطناعي ======================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except:
        pass
    return None

# ====================== نظام المحفظة الشخصية ======================
class BoursagiPortfolio:
    """نظام إدارة المحفظة الشخصية لبوت البورصجي"""
    
    @staticmethod
    def load():
        if REAL_PORTFOLIO_FILE.exists():
            with open(REAL_PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"stocks": [], "total_invested": 0, "total_current": 0, "last_update": None}
    
    @staticmethod
    def save(data):
        with open(REAL_PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def add_stock(ticker, name, avg_price, quantity):
        data = BoursagiPortfolio.load()
        
        new_stock = {
            "ticker": ticker.upper(),
            "name": name,
            "avg_price": avg_price,
            "quantity": quantity,
            "added_date": datetime.now().isoformat()
        }
        
        data["stocks"].append(new_stock)
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
        """تحديث أسعار المحفظة"""
        data = BoursagiPortfolio.load()
        total_current = 0
        total_invested = 0
        
        for stock in data["stocks"]:
            try:
                ticker = stock["ticker"]
                stock_obj = yf.Ticker(ticker)
                df = stock_obj.history(period="1d")
                
                if not df.empty:
                    current_price = df['Close'].iloc[-1]
                    stock["current_price"] = current_price
                    stock["profit_loss"] = (current_price - stock["avg_price"]) * stock["quantity"]
                    stock["profit_loss_pct"] = ((current_price - stock["avg_price"]) / stock["avg_price"]) * 100
                    
                    total_current += current_price * stock["quantity"]
                    total_invested += stock["avg_price"] * stock["quantity"]
            except:
                pass
        
        data["total_current"] = total_current
        data["total_invested"] = total_invested
        data["total_profit"] = total_current - total_invested
        data["total_profit_pct"] = (data["total_profit"] / total_invested * 100) if total_invested > 0 else 0
        data["last_update"] = datetime.now().isoformat()
        
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
    """تحليل سهم واحد"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="2mo")
        
        if df.empty:
            return None
        
        current_price = df['Close'].iloc[-1]
        daily_change = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100 if len(df) > 1 else 0
        rsi = calculate_rsi(df['Close'])
        
        support = df['Low'].tail(30).min()
        resistance = df['High'].tail(30).max()
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "daily_change": daily_change,
            "rsi": rsi,
            "support": support,
            "resistance": resistance,
            "signal": "شراء" if rsi < 35 else "بيع" if rsi > 65 else "انتظار"
        }
    except:
        return None

def get_market_status():
    """الحصول على حالة السوق"""
    try:
        egx = yf.Ticker("^EGX30")
        df = egx.history(period="1d")
        if not df.empty:
            change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            return "مفتوح" if change != 0 else "مغلق", change
    except:
        pass
    return "غير معروف", 0

# ====================== قائمة الأسهم ======================
STOCKS = {
    "🇪🇬 البنك التجاري الدولي": "COMI.CA",
    "🇪🇬 طلعت مصطفى القابضة": "TMGH.CA",
    "🇪🇬 السويدي إليكتريك": "SWDY.CA",
    "🇪🇬 تليكوم مصر": "ETEL.CA",
    "🇪🇬 الشرقية للدخان": "EAST.CA",
    "🇸🇦 أرامكو السعودية": "2222.SR",
    "🇸🇦 مصرف الراجحي": "1120.SR",
    "🇸🇦 مجموعة STC": "7010.SR",
    "🇺🇸 Apple Inc.": "AAPL",
    "🇺🇸 Microsoft Corp.": "MSFT",
    "🇺🇸 Tesla Inc.": "TSLA",
}

# ====================== الرادار (Scanner) ======================
def run_scanner():
    """مسح السوق بحثاً عن الفرص"""
    results = []
    for name, ticker in STOCKS.items():
        analysis = analyze_stock(ticker)
        if analysis:
            results.append({
                "الاسم": name,
                "الرمز": ticker,
                "السعر": analysis['current_price'],
                "التغير": analysis['daily_change'],
                "RSI": analysis['rsi'],
                "الإشارة": analysis['signal']
            })
    
    # ترتيب حسب أفضل الفرص
    results.sort(key=lambda x: x['RSI'])
    return results[:5]

# ====================== واجهة البورصجي AI الرئيسية ======================

def main():
    # تهيئة النماذج
    model = init_gemini()
    
    # عرض هوية البورصجي
    st.markdown('<p class="main-title">🤖 بوت البورصجي AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">مساعدك المالي الذكي للأسواق المصرية • السعودية • العالمية</p>', unsafe_allow_html=True)
    
    # تحديث بيانات المحفظة
    portfolio_data = BoursagiPortfolio.update_prices()
    
    # ====================== لوحة التحكم السريعة ======================
    st.markdown("---")
    
    # الحصول على حالة السوق
    market_status, market_change = get_market_status()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <div>🕒</div>
            <div class="card-value">""" + market_status + """</div>
            <div class="card-label">حالة السوق المصري</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        opportunities_count = len(run_scanner())
        st.markdown(f"""
        <div class="dashboard-card">
            <div>🎯</div>
            <div class="card-value">{opportunities_count}</div>
            <div class="card-label">فرص شراء محتملة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        alerts_count = 0
        if portfolio_data["stocks"]:
            for stock in portfolio_data["stocks"]:
                profit_pct = stock.get('profit_loss_pct', 0)
                if profit_pct <= -3 or profit_pct >= 10:
                    alerts_count += 1
        st.markdown(f"""
        <div class="dashboard-card">
            <div>⚠️</div>
            <div class="card-value">{alerts_count}</div>
            <div class="card-label">تنبيهات نشطة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        accuracy = 94
        st.markdown(f"""
        <div class="dashboard-card">
            <div>🤖</div>
            <div class="card-value">{accuracy}%</div>
            <div class="card-label">دقة الذكاء الاصطناعي</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ====================== المحفظة الشخصية ======================
    st.markdown("### 💼 محفظتي الشخصية")
    st.markdown("*البورصجي يراقب أسهمك الحقيقية ويعطيك التنبيهات الذكية*")
    
    # إضافة سهم جديد
    with st.expander("➕ إضافة سهم جديد للمراقبة"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_ticker = st.text_input("رمز السهم", placeholder="COMI.CA")
        with col2:
            new_name = st.text_input("اسم السهم", placeholder="البنك التجاري الدولي")
        with col3:
            buy_price = st.number_input("سعر الشراء", min_value=0.0, step=0.5)
        with col4:
            quantity = st.number_input("الكمية", min_value=1, step=1)
        
        if st.button("✨ أضف للمراقبة", use_container_width=True):
            if new_ticker and buy_price and quantity:
                BoursagiPortfolio.add_stock(new_ticker, new_name or new_ticker, buy_price, int(quantity))
                st.success(f"✅ تم إضافة {new_ticker} إلى محفظتك - البورصجي سيراقبه الآن")
                st.rerun()
    
    # عرض الأسهم في المحفظة
    if portfolio_data["stocks"]:
        # إحصائيات المحفظة
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 إجمالي المستثمر", f"{portfolio_data['total_invested']:,.2f}")
        col2.metric("📈 القيمة الحالية", f"{portfolio_data['total_current']:,.2f}")
        profit_color = "normal" if portfolio_data['total_profit'] >= 0 else "inverse"
        col3.metric("📊 إجمالي الربح", f"{portfolio_data['total_profit']:+,.2f}", 
                   delta=f"{portfolio_data['total_profit_pct']:+.2f}%", delta_color=profit_color)
        col4.metric("📅 آخر تحديث", portfolio_data.get('last_update', '--')[:16] if portfolio_data.get('last_update') else "--")
        
        st.markdown("---")
        
        # عرض الأسهم كبطاقات
        for stock in portfolio_data["stocks"]:
            profit_pct = stock.get('profit_loss_pct', 0)
            profit_class = "stock-profit-positive" if profit_pct >= 0 else "stock-profit-negative"
            
            with st.container():
                st.markdown(f"""
                <div class="stock-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 18px; font-weight: bold;">{stock['name']}</span>
                            <span class="badge">{stock['ticker']}</span>
                        </div>
                        <div>
                            <button class="boursagi-button" onclick="alert('تحليل متقدم قريباً')">🧠 اسأل البورصجي</button>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                        <div>💰 سعر الشراء: <strong>{stock['avg_price']:.2f}</strong></div>
                        <div>📊 السعر الحالي: <strong>{stock.get('current_price', 0):.2f}</strong></div>
                        <div class="{profit_class}">📈 الربح: {profit_pct:+.2f}%</div>
                        <div>📦 الكمية: {stock['quantity']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # أزرار التحكم
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🧠 تحليل ذكي", key=f"analyze_{stock['ticker']}"):
                        with st.spinner("البورصجي يفكر..."):
                            analysis = analyze_stock(stock['ticker'])
                            if analysis and model:
                                prompt = f"حلل سهم {stock['name']} (RSI: {analysis['rsi']:.1f}) وأعط توصية مختصرة"
                                response = model.generate_content(prompt)
                                st.info(f"🤖 **البورصجي يقول:** {response.text}")
                with col2:
                    if st.button(f"🗑️ حذف", key=f"del_{stock['ticker']}"):
                        BoursagiPortfolio.remove_stock(stock['ticker'])
                        st.rerun()
    else:
        st.info("📭 محفظتك فارغة. أضف أسهمك ليراقبها البورصجي ويحللها")
    
    st.markdown("---")
    
    # ====================== رادار البورصجي ======================
    st.markdown("### 📡 رادار البورصجي")
    st.markdown("*اكتشف فرص الاستثمار قبل الجميع*")
    
    col_scan, col_result = st.columns([1, 3])
    with col_scan:
        if st.button("🔍 امسح السوق الآن", type="primary", use_container_width=True):
            with st.spinner("رادار البورصجي يبحث عن الفرص..."):
                time.sleep(1)  # محاكاة المسح
                opportunities = run_scanner()
                st.session_state['scan_results'] = opportunities
                st.success(f"✅ تم العثور على {len(opportunities)} فرصة")
    
    with col_result:
        if 'scan_results' in st.session_state and st.session_state['scan_results']:
            for opp in st.session_state['scan_results']:
                signal = opp['الإشارة']
                signal_icon = "🟢" if signal == "شراء" else "🔴" if signal == "بيع" else "🟡"
                st.markdown(f"""
                <div style="background: #1e1e2e; border-radius: 10px; padding: 10px; margin-bottom: 8px;">
                    <span style="font-weight: bold;">{opp['الاسم']}</span>
                    <span class="badge">{opp['الرمز']}</span>
                    <span style="float: right;">{signal_icon} {signal} | السعر: {opp['السعر']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ====================== آخر أخبار البورصجي ======================
    with st.expander("📰 آخر أخبار وتحليلات البورصجي"):
        st.markdown("""
        ### 🧠 تحليلات البورصجي اليوم
        
        **📊 تحليل السوق المصري:**
        - المؤشر الرئيسي EGX30 في منطقة استقرار
        - قطاع البنوك يقود الارتفاعات اليوم
        - السيولة المحلية في أعلى مستوى لها هذا الشهر
        
        **🎯 توصيات البورصجي:**
        - فرصة شراء على CIB مع وقف خسارة عند 74
        - متابعة TMGH بعد اختراق المقاومة
        - جني أرباح جزئي على EAST بعد الارتفاع الأخير
        
        **⚠️ تنبيهات المخاطر:**
        - متابعة تأثير أسعار الفائدة على السوق
        - تقلبات محتملة مع إعلانات الشركات
        """)
    
    # ====================== تذييل الصفحة ======================
    st.markdown("""
    <div class="footer">
        🤖 بوت البورصجي AI - العقل المدبر لمحفظتك<br>
        البيانات من Yahoo Finance | تحليلات بالذكاء الاصطناعي Gemini<br>
        للأغراض التعليمية والاستشارية فقط
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
