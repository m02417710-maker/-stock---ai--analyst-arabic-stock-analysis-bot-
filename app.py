# البورصجي AI - النسخة النهائية المصححة (Fix Mixed Numeric Types Error)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import sqlite3
import requests
from pathlib import Path

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - العقل المدبر",
    page_icon="🧠",
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
    
    .risk-low {
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
    }
    
    .risk-medium {
        background: rgba(255, 170, 0, 0.1);
        color: #ffaa00;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
    }
    
    .risk-high {
        background: rgba(255, 68, 68, 0.1);
        color: #ff4444;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
    }
    
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
</style>
""", unsafe_allow_html=True)

# 3. دالة مرنة لدعم جميع الأسواق
def get_flexible_ticker(symbol):
    if "." in symbol:
        return symbol
    return f"{symbol}.CA"

def get_market_flag(symbol):
    if ".CA" in symbol:
        return "🇪🇬"
    elif ".SR" in symbol:
        return "🇸🇦"
    else:
        return "🇺🇸"

# 4. قاعدة البيانات
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
            stop_loss REAL,
            trailing_stop REAL,
            quantity INTEGER,
            sector TEXT,
            date TEXT,
            status TEXT,
            current_price REAL,
            profit_pct REAL,
            highest_price REAL
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
            "target_price": row[3], "stop_loss": row[4], "trailing_stop": row[5] if row[5] else 0,
            "quantity": row[6], "sector": row[7], "date": row[8],
            "status": row[9], "current_price": row[10] if row[10] else row[2],
            "profit_pct": row[11] if row[11] else 0,
            "highest_price": row[12] if row[12] else row[2]
        })
    return trades

def save_trade(trade):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (symbol, entry_price, target_price, stop_loss, quantity, sector, date, status, highest_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trade["symbol"], trade["entry_price"], trade["target_price"], 
          trade.get("stop_loss", trade["entry_price"] * 0.95),
          trade["quantity"], trade["sector"], trade["date"], "active", trade["entry_price"]))
    conn.commit()
    conn.close()

def update_trade(trade_id, target_price, stop_loss):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE trades SET target_price = ?, stop_loss = ? WHERE id = ?', 
                   (target_price, stop_loss, trade_id))
    conn.commit()
    conn.close()

def update_trailing_stop(trade_id, trailing_stop):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE trades SET trailing_stop = ? WHERE id = ?', (trailing_stop, trade_id))
    conn.commit()
    conn.close()

def delete_trade(trade_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()

def update_trade_prices():
    trades = load_trades()
    alerts = []
    
    for trade in trades:
        try:
            ticker = get_flexible_ticker(trade["symbol"])
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d")
            if not df.empty:
                current = float(df['Close'].iloc[-1])
                profit_pct = ((current - trade["entry_price"]) / trade["entry_price"]) * 100
                
                highest_price = max(float(trade.get("highest_price", trade["entry_price"])), current)
                
                if trade.get("trailing_stop", 0) > 0:
                    new_stop = highest_price * (1 - trade["trailing_stop"] / 100)
                    if new_stop > trade["stop_loss"]:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute('UPDATE trades SET stop_loss = ? WHERE id = ?', (new_stop, trade["id"]))
                        conn.commit()
                        conn.close()
                        
                        if new_stop > trade["stop_loss"]:
                            alerts.append(f"📈 {trade['symbol']}: تم رفع وقف الخسارة إلى {new_stop:.2f}")
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('UPDATE trades SET current_price = ?, profit_pct = ?, highest_price = ? WHERE id = ?', 
                               (current, profit_pct, highest_price, trade["id"]))
                conn.commit()
                conn.close()
                
                if current >= trade["target_price"] * 0.95:
                    alerts.append(f"🎯 {trade['symbol']}: قرب من تحقيق الهدف! ({current:.2f}/{trade['target_price']:.2f})")
                
                if current <= trade["stop_loss"] * 1.02:
                    alerts.append(f"⚠️ {trade['symbol']}: قرب من وقف الخسارة! ({current:.2f}/{trade['stop_loss']:.2f})")
                    
        except Exception as e:
            pass
    
    return alerts

# 5. دوال التحليل
def calculate_risk_reward(entry, target, stop_loss):
    risk = abs(entry - stop_loss)
    reward = abs(target - entry)
    if risk <= 0:
        return 0
    return reward / risk

def get_risk_level(risk_reward):
    if risk_reward >= 3:
        return "low", "منخفضة 🟢"
    elif risk_reward >= 1.5:
        return "medium", "متوسطة 🟡"
    else:
        return "high", "عالية 🔴"

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

# 6. الواجهة الرئيسية
def main():
    # تحديث الأسعار
    alerts = update_trade_prices()
    
    # شريط المؤشرات
    st.markdown("""
    <div class="ticker-wrapper">
        <span class="ticker-item"><span style="color:#888;">EGX30:</span> <span style="color:#00ff88;">51,760.97 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">S&P 500:</span> <span style="color:#00ff88;">7,230.11 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">TASI:</span> <span style="color:#ff4444;">12,450.33 ▼</span></span>
        <span class="ticker-item"><span style="color:#888;">السيولة:</span> <span style="color:#00b4d8;">2.5B</span></span>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض التنبيهات
    if alerts:
        for alert in alerts[:3]:
            if "🎯" in alert:
                st.success(alert)
            elif "⚠️" in alert:
                st.warning(alert)
            else:
                st.info(alert)
    
    # الهيدر
    st.markdown(f"""
    <div class="main-header">
        <div>
            <span class="logo-title">🧠 البورصجي AI</span>
            <span style="font-size: 12px; color: #888;">العقل المدبر - الإصدار النهائي</span>
        </div>
        <div style="display: flex; gap: 15px;">
            <span style="font-size: 12px;">📅 {datetime.now().strftime("%Y-%m-%d")}</span>
            <span style="color: #00ffcc; font-size: 12px;">● LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة التحكم", "📒 مفكرة الصفقات", "🧠 العقل المدبر", "📄 التقارير"])
    
    # ====================== التبويب 1: لوحة التحكم ======================
    with tab1:
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 إجمالي المستثمر", f"{stats['total_invested']:,.0f}")
        col2.metric("📈 القيمة الحالية", f"{stats['total_current']:,.0f}")
        col3.metric("📊 إجمالي الربح", f"{stats['total_profit']:+,.0f}", f"{stats['profit_pct']:+.1f}%")
        col4.metric("🏆 نسبة النجاح", f"{stats['win_rate']:.1f}%")
        
        if trades:
            profit_data = [{"السهم": t["symbol"], "الربح": t.get("profit_pct", 0)} for t in trades[:10]]
            df_profit = pd.DataFrame(profit_data)
            
            fig = go.Figure(data=[go.Bar(
                x=df_profit["السهم"], y=df_profit["الربح"],
                marker_color=["#00ff88" if x > 0 else "#ff4444" for x in df_profit["الربح"]],
                text=df_profit["الربح"].apply(lambda x: f"{x:+.1f}%"),
                textposition="outside"
            )])
            fig.update_layout(template="plotly_dark", height=400, title="توزيع الأرباح")
            st.plotly_chart(fig, use_container_width=True)
    
    # ====================== التبويب 2: مفكرة الصفقات ======================
    with tab2:
        st.markdown("### 📒 مفكرة الصفقات")
        
        with st.expander("➕ إضافة صفقة جديدة", expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                symbol = st.text_input("الرمز", placeholder="COMI أو AAPL").upper()
            with col2:
                entry = st.number_input("سعر الدخول", min_value=0.01, step=0.5, value=100.0)
            with col3:
                target = st.number_input("الهدف 🎯", min_value=0.01, step=0.5, value=120.0)
            with col4:
                # ✅ إصلاح الخطأ: تحويل القيمة إلى float صريح
                default_stop = float(entry * 0.95) if entry > 0 else 90.0
                stop = st.number_input("وقف الخسارة 🛡️", min_value=0.01, step=0.5, value=default_stop)
            with col5:
                qty = st.number_input("الكمية", min_value=1, step=1, value=10)
            
            sector = st.selectbox("القطاع", ["بنوك", "عقارات", "صناعة", "تكنولوجيا", "اتصالات", "طاقة"])
            
            col_trail1, col_trail2 = st.columns(2)
            with col_trail1:
                use_trailing = st.checkbox("تفعيل Trailing Stop")
            with col_trail2:
                trailing_pct = st.slider("نسبة التراجع (%)", 1.0, 10.0, 5.0, 0.5) if use_trailing else 0.0
            
            if st.button("💾 حفظ الصفقة", use_container_width=True):
                if symbol and entry > 0 and target > 0:
                    trade = {
                        "symbol": symbol,
                        "entry_price": float(entry),
                        "target_price": float(target),
                        "stop_loss": float(stop) if stop > 0 else float(entry * 0.95),
                        "quantity": int(qty),
                        "sector": sector,
                        "date": datetime.now().isoformat(),
                        "trailing_stop": float(trailing_pct) if use_trailing else 0.0
                    }
                    save_trade(trade)
                    st.success(f"✅ تم إضافة {symbol} {get_market_flag(symbol)}")
                    st.rerun()
                else:
                    st.error("يرجى إدخال جميع البيانات المطلوبة")
        
        # عرض الصفقات
        trades = load_trades()
        if trades:
            for trade in trades:
                profit_pct = trade.get("profit_pct", 0)
                profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
                
                st.markdown(f"""
                <div class="trade-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div><b>{trade['symbol']}</b> {get_market_flag(trade['symbol'])} | {trade.get('sector', '')}</div>
                        <div class="{profit_class}">{profit_pct:+.1f}%</div>
                    </div>
                    <div style="font-size: 12px;">
                        🚪 الدخول: {trade['entry_price']:.2f} | 🎯 الهدف: {trade['target_price']:.2f} | 🛡️ وقف: {trade['stop_loss']:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✏️ تعديل", key=f"edit_{trade['id']}"):
                        st.session_state[f'editing_{trade["id"]}'] = True
                
                with col2:
                    with st.expander(f"📊 تفاصيل", key=f"details_{trade['id']}"):
                        st.write(f"الكمية: {trade['quantity']}")
                        st.write(f"تاريخ الدخول: {trade['date'][:10]}")
                        if trade.get("trailing_stop", 0) > 0:
                            st.write(f"Trailing Stop: {trade['trailing_stop']}%")
                
                with col3:
                    if st.button(f"🗑️ حذف", key=f"del_{trade['id']}"):
                        delete_trade(trade['id'])
                        st.rerun()
                
                # نافذة التعديل
                if st.session_state.get(f'editing_{trade["id"]}', False):
                    with st.container():
                        st.markdown(f"**تعديل صفقة {trade['symbol']}**")
                        new_target = st.number_input("الهدف الجديد", value=float(trade["target_price"]), step=0.5, key=f"target_{trade['id']}")
                        new_stop = st.number_input("وقف الخسارة الجديد", value=float(trade["stop_loss"]), step=0.5, key=f"stop_{trade['id']}")
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 حفظ التعديل", key=f"save_edit_{trade['id']}"):
                                update_trade(trade['id'], new_target, new_stop)
                                st.session_state[f'editing_{trade["id"]}'] = False
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ إلغاء", key=f"cancel_edit_{trade['id']}"):
                                st.session_state[f'editing_{trade["id"]}'] = False
                                st.rerun()
        else:
            st.info("📭 لا توجد صفقات. أضف صفقتك الأولى")
    
    # ====================== التبويب 3: العقل المدبر ======================
    with tab3:
        st.markdown("### 🧠 توصيات العقل المدبر لإدارة المخاطر")
        
        trades = load_trades()
        
        if trades:
            risk_data = []
            for trade in trades:
                risk_reward = calculate_risk_reward(trade["entry_price"], trade["target_price"], trade["stop_loss"])
                risk_level, risk_text = get_risk_level(risk_reward)
                risk_data.append({"السهم": trade["symbol"], "نسبة المخاطرة": f"1:{risk_reward:.1f}", "المستوى": risk_text})
            
            high_risk_trades = [t for t in risk_data if "عالية" in t["المستوى"]]
            
            if high_risk_trades:
                st.warning(f"⚠️ لديك {len(high_risk_trades)} صفقات ذات مخاطرة عالية")
                st.info("💡 **نصيحة العقل المدبر:** حاول أن يكون العائد المستهدف ضعف وقف الخسارة على الأقل (1:2)")
            else:
                st.success("✅ جميع صفقاتك تلتزم بمعايير إدارة المخاطر الجيدة")
            
            st.markdown("---")
            
            # حاسبة حجم المركز
            st.markdown("### 🧮 حاسبة حجم المركز")
            
            col_cap, col_risk = st.columns(2)
            with col_cap:
                total_capital = st.number_input("إجمالي رأس المال", value=100000.0, step=10000.0)
            with col_risk:
                risk_percent = st.slider("نسبة المخاطرة في الصفقة (%)", 0.5, 5.0, 2.0, 0.5)
            
            amount_to_risk = total_capital * (risk_percent / 100)
            st.info(f"💰 يجب ألا تخسر أكثر من **{amount_to_risk:,.2f}** في الصفقة الواحدة")
            
            # تحليل الأداء
            st.markdown("---")
            st.markdown("### 📊 تحليل أداء المحفظة")
            
            stats = calculate_portfolio_stats(trades)
            
            if stats['win_rate'] > 70:
                st.success(f"🎯 نسبة نجاح ممتازة ({stats['win_rate']:.0f}%)")
            elif stats['win_rate'] < 40:
                st.warning(f"⚠️ نسبة النجاح ({stats['win_rate']:.0f}%) تحتاج تحسين")
            
            if stats['profit_pct'] > 10:
                st.success(f"📈 أداء استثنائي! أرباح {stats['profit_pct']:.1f}%")
            elif stats['profit_pct'] < 0:
                st.warning(f"📉 محفظتك في تصحيح ({stats['profit_pct']:.1f}%)")
        else:
            st.info("📭 أضف صفقات لبدء تحليل العقل المدبر")
    
    # ====================== التبويب 4: التقارير ======================
    with tab4:
        st.markdown("### 📄 التقارير والتحليلات")
        
        trades = load_trades()
        
        if trades:
            sectors = {}
            for trade in trades:
                sector = trade.get("sector", "غير محدد")
                sectors[sector] = sectors.get(sector, 0) + trade["quantity"]
            
            if sectors:
                fig = go.Figure(data=[go.Pie(
                    labels=list(sectors.keys()),
                    values=list(sectors.values()),
                    hole=0.4,
                    marker_colors=["#00ffcc", "#ff00ff", "#ffaa00", "#00ff88", "#ff4444"]
                )])
                fig.update_layout(template="plotly_dark", height=400, title="توزيع الاستثمارات")
                st.plotly_chart(fig, use_container_width=True)
            
            df_trades = pd.DataFrame([{
                "السهم": t["symbol"],
                "الربح %": f"{t.get('profit_pct', 0):+.1f}%",
                "الحالة": "🟢 نشط"
            } for t in trades])
            st.dataframe(df_trades, use_container_width=True, hide_index=True)
            
            if st.button("📥 تصدير CSV", use_container_width=True):
                df_export = pd.DataFrame(trades)
                csv = df_export.to_csv(index=False)
                st.download_button("تحميل", csv, "boursagi_report.csv", "text/csv")
        else:
            st.info("📭 لا توجد بيانات")
    
    # تذييل
    st.markdown(f"""
    <div class="footer">
        🧠 البورصجي AI | العقل المدبر - إدارة مخاطر احترافية<br>
        📊 تحديث لحظي • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
