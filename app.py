# البورصجي AI - النسخة المؤسسية الكاملة (Desktop + Mobile + Telegram + Database)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import json
import sqlite3
import requests
import asyncio
from pathlib import Path
import threading
import time

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - المؤسسي",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS المتطور
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #090b10 !important;
    }
    
    /* شريط المؤشرات العلوي */
    .ticker-wrapper {
        background: #141820;
        padding: 10px 20px;
        border-bottom: 1px solid #00ffcc30;
        display: flex;
        gap: 30px;
        overflow-x: auto;
        white-space: nowrap;
        margin-bottom: 20px;
    }
    
    .ticker-item {
        font-size: 13px;
        color: #fff;
        font-weight: 500;
    }
    
    /* الهيدر */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 25px;
        background: #0d1117;
        border-bottom: 1px solid #00ffcc20;
        margin-bottom: 20px;
    }
    
    .logo-title {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* بطاقات الفرص */
    .alert-card-success {
        background: rgba(0, 255, 204, 0.03) !important;
        border: 1px solid rgba(0, 255, 204, 0.2) !important;
        border-right: 4px solid #00ffcc !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-bottom: 15px !important;
        transition: all 0.3s;
    }
    
    .alert-card-success:hover {
        background: rgba(0, 255, 204, 0.08) !important;
        transform: translateX(-3px);
    }
    
    .alert-card-danger {
        background: rgba(255, 68, 68, 0.03) !important;
        border: 1px solid rgba(255, 68, 68, 0.2) !important;
        border-right: 4px solid #ff4444 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-bottom: 15px !important;
    }
    
    /* بطاقات الصفقات */
    .trade-card {
        background: #0d1117;
        border: 1px solid #1c222d;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s;
    }
    
    .trade-card:hover {
        border-color: #00ffcc;
        transform: translateX(-5px);
    }
    
    .profit-positive { color: #00ff88; font-weight: bold; }
    .profit-negative { color: #ff4444; font-weight: bold; }
    
    /* شريط التقدم */
    .progress-bar-container {
        background: #1c222d;
        height: 6px;
        border-radius: 10px;
        margin-top: 10px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #00ffcc, #00ff88);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #555;
        font-size: 11px;
        margin-top: 30px;
        border-top: 1px solid #1c222d;
    }
    
    .stButton > button {
        border-radius: 20px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# 3. قاعدة البيانات (SQLite)
DB_PATH = Path(__file__).parent / "data" / "boursagi.db"
Path(__file__).parent / "data" / "boursagi.db"
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            entry_price REAL,
            target_price REAL,
            quantity INTEGER,
            sector TEXT,
            date TEXT,
            status TEXT,
            current_price REAL,
            profit_pct REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            alert_type TEXT,
            message TEXT,
            timestamp TEXT,
            sent BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_database()

def load_trades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trades ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    trades = []
    for row in rows:
        trades.append({
            "id": row[0], "symbol": row[1], "entry_price": row[2],
            "target_price": row[3], "quantity": row[4], "sector": row[5],
            "date": row[6], "status": row[7], "current_price": row[8] if row[8] else row[2],
            "profit_pct": row[9] if row[9] else 0
        })
    return trades

def save_trade(trade):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (symbol, entry_price, target_price, quantity, sector, date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (trade["symbol"], trade["entry_price"], trade["target_price"], 
          trade["quantity"], trade["sector"], trade["date"], "active"))
    conn.commit()
    conn.close()

def delete_trade(trade_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()

def update_trade_price(trade_id, current_price, profit_pct):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE trades SET current_price = ?, profit_pct = ? WHERE id = ?', 
                   (current_price, profit_pct, trade_id))
    conn.commit()
    conn.close()

def save_alert(alert):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (symbol, alert_type, message, timestamp, sent)
        VALUES (?, ?, ?, ?, ?)
    ''', (alert["symbol"], alert["alert_type"], alert["message"], 
          alert["timestamp"], 0))
    conn.commit()
    conn.close()

# 4. نظام تنبيهات تليجرام
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

def init_telegram():
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    try:
        if "TELEGRAM_BOT_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
            TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
            return True
    except:
        pass
    return False

def send_telegram_alert(message, alert_type="info"):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    icons = {"danger": "🚨", "warning": "⚠️", "success": "✅", "info": "📊"}
    full_message = f"{icons.get(alert_type, '📊')} *البورصجي AI*\n\n{message}"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": full_message, "parse_mode": "Markdown"}
        response = requests.post(url, data=data, timeout=10)
        return response.ok
    except:
        return False

def check_and_send_alerts():
    """فحص الصفقات وإرسال تنبيهات عند تحقيق الأهداف"""
    trades = load_trades()
    alerts_sent = []
    
    for trade in trades:
        try:
            ticker = trade["symbol"] + ".CA" if not trade["symbol"].endswith(".CA") else trade["symbol"]
            stock = yf.Ticker(ticker)
            df = stock.history(period="1d")
            
            if not df.empty:
                current = df['Close'].iloc[-1]
                profit_pct = ((current - trade["entry_price"]) / trade["entry_price"]) * 100
                
                # تحديث السعر في قاعدة البيانات
                update_trade_price(trade["id"], current, profit_pct)
                
                # التحقق من تحقيق الهدف
                if current >= trade["target_price"]:
                    message = f"🎯 *هدف محقق!*\n\nالسهم: {trade['symbol']}\nسعر الدخول: {trade['entry_price']:.2f}\nالسعر الحالي: {current:.2f}\nالربح: {profit_pct:+.1f}%"
                    send_telegram_alert(message, "success")
                    alerts_sent.append(trade["symbol"])
                    
                # تنبيه الخسارة
                elif profit_pct <= -5:
                    message = f"⚠️ *تنبيه خسارة!*\n\nالسهم: {trade['symbol']}\nسعر الدخول: {trade['entry_price']:.2f}\nالسعر الحالي: {current:.2f}\nالخسارة: {profit_pct:.1f}%"
                    send_telegram_alert(message, "warning")
                    alerts_sent.append(trade["symbol"])
                    
        except:
            pass
    
    return alerts_sent

# 5. الماسح الآلي (Auto Scanner)
def auto_scanner():
    """مسح السوق تلقائياً للبحث عن فرص"""
    stocks_to_scan = ["COMI.CA", "TMGH.CA", "SWDY.CA", "ETEL.CA", "FWRY.CA"]
    opportunities = []
    
    for ticker in stocks_to_scan:
        try:
            df = yf.Ticker(ticker).history(period="2mo")
            if not df.empty and len(df) > 20:
                # حساب RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                rsi_value = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
                
                current = df['Close'].iloc[-1]
                
                if rsi_value < 35:
                    opportunities.append({
                        "symbol": ticker.replace(".CA", ""),
                        "price": current,
                        "rsi": rsi_value,
                        "strength": "قوية" if rsi_value < 30 else "متوسطة"
                    })
        except:
            pass
    
    return opportunities

# 6. دوال التحليل
def calculate_portfolio_stats(trades):
    if not trades:
        return {"total_invested": 0, "total_current": 0, "total_profit": 0, "profit_pct": 0, "win_rate": 0}
    
    total_invested = sum(t["entry_price"] * t["quantity"] for t in trades)
    total_current = sum(t.get("current_price", t["entry_price"]) * t["quantity"] for t in trades)
    total_profit = total_current - total_invested
    profit_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    
    winning_trades = len([t for t in trades if t.get("profit_pct", 0) > 0])
    win_rate = (winning_trades / len(trades)) * 100 if trades else 0
    
    return {
        "total_invested": total_invested,
        "total_current": total_current,
        "total_profit": total_profit,
        "profit_pct": profit_pct,
        "win_rate": win_rate
    }

# 7. الواجهة الرئيسية
def main():
    # تهيئة التليجرام
    telegram_enabled = init_telegram()
    
    # شريط المؤشرات
    st.markdown("""
    <div class="ticker-wrapper">
        <span class="ticker-item"><span style="color:#888;">EGX30:</span> <span style="color:#00ff88;">51,760.97 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">EGX70:</span> <span style="color:#ff4444;">14,028.98 ▼</span></span>
        <span class="ticker-item"><span style="color:#888;">S&P 500:</span> <span style="color:#00ff88;">7,230.11 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">السيولة:</span> <span style="color:#00b4d8;">2.5B</span></span>
    </div>
    """, unsafe_allow_html=True)
    
    # الهيدر
    st.markdown("""
    <div class="main-header">
        <div>
            <span class="logo-title">🏢 البورصجي AI</span>
            <span style="font-size: 12px; color: #888;">النسخة المؤسسية</span>
        </div>
        <div style="display: flex; gap: 15px;">
            <span style="font-size: 12px;">📅 """ + datetime.now().strftime("%Y-%m-%d") + """</span>
            <span style="color: #00ffcc; font-size: 12px;">● LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 🎮 لوحة التحكم")
        
        # إعدادات المخاطر
        st.subheader("💰 إعدادات المخاطر")
        capital = st.number_input("رأس المال", value=100000, step=10000)
        
        st.markdown("---")
        
        # حالة التنبيهات
        st.subheader("🔔 نظام التنبيهات")
        if telegram_enabled:
            st.success("✅ تليجرام: متصل")
            if st.button("📢 اختبار التنبيه", use_container_width=True):
                if send_telegram_alert("🧠 هذا تنبيه تجريبي من البورصجي AI", "info"):
                    st.success("تم إرسال التنبيه بنجاح!")
                else:
                    st.error("فشل الإرسال - تحقق من الإعدادات")
        else:
            st.warning("⚠️ أضف مفاتيح التليجرام في secrets")
        
        st.markdown("---")
        
        # الماسح الآلي
        st.subheader("🔄 الماسح الآلي")
        if st.button("🔍 مسح السوق الآن", use_container_width=True):
            with st.spinner("جاري المسح..."):
                opportunities = auto_scanner()
                if opportunities:
                    st.success(f"✅ تم العثور على {len(opportunities)} فرصة")
                    for opp in opportunities[:3]:
                        st.markdown(f"""
                        <div class="alert-card-success">
                            🟢 <b>{opp['symbol']}</b> | RSI: {opp['rsi']:.1f} | القوة: {opp['strength']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد فرص حالياً")
    
    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة التحكم", "📒 مفكرة الصفقات", "🤖 المسح الآلي", "📄 التقارير"])
    
    # ====================== التبويب 1: لوحة التحكم ======================
    with tab1:
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 إجمالي المستثمر", f"{stats['total_invested']:,.0f}")
        col2.metric("📈 القيمة الحالية", f"{stats['total_current']:,.0f}")
        col3.metric("📊 إجمالي الربح", f"{stats['total_profit']:+,.0f}", f"{stats['profit_pct']:+.1f}%")
        
        # رسم بياني للأرباح
        if trades:
            profit_data = [{"السهم": t["symbol"], "الربح": t.get("profit_pct", 0)} for t in trades]
            df_profit = pd.DataFrame(profit_data)
            
            fig = go.Figure(data=[go.Bar(
                x=df_profit["السهم"], y=df_profit["الربح"],
                marker_color=["#00ff88" if x > 0 else "#ff4444" for x in df_profit["الربح"]]
            )])
            fig.update_layout(template="plotly_dark", height=400, title="توزيع الأرباح")
            st.plotly_chart(fig, use_container_width=True)
    
    # ====================== التبويب 2: مفكرة الصفقات ======================
    with tab2:
        st.markdown("### 📒 مفكرة الصفقات")
        
        with st.expander("➕ إضافة صفقة جديدة"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                symbol = st.text_input("الرمز", placeholder="COMI").upper()
            with col2:
                entry = st.number_input("سعر الدخول", min_value=0.0, step=0.5)
            with col3:
                target = st.number_input("المستهدف", min_value=0.0, step=0.5)
            with col4:
                qty = st.number_input("الكمية", min_value=1, step=1)
            
            sector = st.selectbox("القطاع", ["بنوك", "عقارات", "صناعة", "تكنولوجيا", "اتصالات"])
            
            if st.button("💾 حفظ", use_container_width=True):
                if symbol and entry > 0 and target > 0:
                    trade = {
                        "symbol": symbol, "entry_price": entry, "target_price": target,
                        "quantity": qty, "sector": sector, "date": datetime.now().isoformat()
                    }
                    save_trade(trade)
                    st.success(f"✅ تم إضافة {symbol}")
                    st.rerun()
        
        # عرض الصفقات
        trades = load_trades()
        if trades:
            for trade in trades:
                profit_pct = trade.get("profit_pct", 0)
                profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
                
                st.markdown(f"""
                <div class="trade-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div><b>{trade['symbol']}</b> | {trade.get('sector', '')}</div>
                        <div class="{profit_class}">{profit_pct:+.1f}%</div>
                    </div>
                    <div style="font-size: 12px;">
                        الدخول: {trade['entry_price']:.2f} | الهدف: {trade['target_price']:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ حذف", key=f"del_{trade['id']}"):
                    delete_trade(trade['id'])
                    st.rerun()
        else:
            st.info("لا توجد صفقات")
    
    # ====================== التبويب 3: المسح الآلي ======================
    with tab3:
        st.markdown("### 🤖 الماسح الآلي للأسواق")
        st.caption("البورصجي AI يبحث عن أفضل فرص الاستثمار")
        
        if st.button("🔍 بدء المسح الشامل", type="primary", use_container_width=True):
            with st.spinner("جاري مسح الأسواق..."):
                opportunities = auto_scanner()
                
                if opportunities:
                    st.success(f"✅ تم العثور على {len(opportunities)} فرصة")
                    for opp in opportunities:
                        st.markdown(f"""
                        <div class="alert-card-success">
                            🟢 <b>{opp['symbol']}</b><br>
                            السعر: {opp['price']:.2f} | RSI: {opp['rsi']:.1f} | القوة: {opp['strength']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # إرسال تنبيه تليجرام إذا تم التفعيل
                        if telegram_enabled:
                            send_telegram_alert(f"🔍 فرصة جديدة!\nالسهم: {opp['symbol']}\nالسعر: {opp['price']:.2f}\nRSI: {opp['rsi']:.1f}", "success")
                else:
                    st.info("📭 لم يتم العثور على فرص حالياً")
    
    # ====================== التبويب 4: التقارير ======================
    with tab4:
        st.markdown("### 📄 تقارير الأداء")
        
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        col1, col2 = st.columns(2)
        col1.metric("📊 عدد الصفقات", len(trades))
        col2.metric("🏆 نسبة النجاح", f"{stats['win_rate']:.1f}%")
        
        if trades:
            # تحليل العقل المدبر
            avg_profit = stats['profit_pct']
            
            if avg_profit > 5:
                st.success("🧠 **تحليل العقل:** أداء ممتاز! استمر في استراتيجيتك.")
            elif avg_profit > 0:
                st.info("🧠 **تحليل العقل:** أداء جيد. نوصي بتنويع القطاعات.")
            else:
                st.warning("🧠 **تحليل العقل:** الأداء يحتاج تحسين. راجع استراتيجيتك.")
            
            # زر تصدير التقرير
            if st.button("📥 تصدير تقرير CSV", use_container_width=True):
                df = pd.DataFrame(trades)
                csv = df.to_csv(index=False)
                st.download_button("تحميل التقرير", csv, "boursagi_report.csv", "text/csv")
    
    # زر تحديث التنبيهات
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 تحديث التنبيهات", use_container_width=True):
            with st.spinner("جاري فحص الصفقات..."):
                alerts = check_and_send_alerts()
                if alerts:
                    st.success(f"✅ تم إرسال {len(alerts)} تنبيه")
                else:
                    st.info("لا توجد تنبيهات جديدة")
    
    # تذييل
    st.markdown(f"""
    <div class="footer">
        🏢 البورصجي AI | العين التي لا تنام في الأسواق<br>
        📊 تحديث لحظي • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
