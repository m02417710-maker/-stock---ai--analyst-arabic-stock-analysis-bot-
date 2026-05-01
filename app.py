# البورصجي AI - النسخة المرنة (Flexible Edition)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import json
import sqlite3
import requests
from pathlib import Path

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - المرن",
    page_icon="🔄",
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
    
    /* شريط المؤشرات */
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
    
    /* بطاقات الصفقات */
    .trade-card {
        background: #0d1117;
        border: 1px solid #1c222d;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s;
        position: relative;
    }
    
    .trade-card:hover {
        border-color: #00ffcc;
        transform: translateX(-5px);
    }
    
    /* مؤشرات المخاطر */
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
    
    /* أزرار التعديل */
    .edit-btn {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid #00ffcc;
        color: #00ffcc;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        cursor: pointer;
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
    """دعم مرن لجميع الأسواق (مصر، السعودية، أمريكا)"""
    if "." in symbol:
        return symbol
    # افتراض أن الرمز بدون لاحقة هو سهم مصري
    return f"{symbol}.CA"

def get_market_flag(symbol):
    """تحديد علم السوق تلقائياً"""
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
            quantity INTEGER,
            sector TEXT,
            date TEXT,
            status TEXT,
            current_price REAL,
            profit_pct REAL
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
            "target_price": row[3], "stop_loss": row[4], "quantity": row[5],
            "sector": row[6], "date": row[7], "status": row[8],
            "current_price": row[9] if row[9] else row[2],
            "profit_pct": row[10] if row[10] else 0
        })
    return trades

def save_trade(trade):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (symbol, entry_price, target_price, stop_loss, quantity, sector, date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trade["symbol"], trade["entry_price"], trade["target_price"], 
          trade.get("stop_loss", trade["entry_price"] * 0.95),
          trade["quantity"], trade["sector"], trade["date"], "active"))
    conn.commit()
    conn.close()

def update_trade(trade_id, target_price, stop_loss):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE trades SET target_price = ?, stop_loss = ? WHERE id = ?', 
                   (target_price, stop_loss, trade_id))
    conn.commit()
    conn.close()

def delete_trade(trade_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    conn.commit()
    conn.close()

def update_trade_prices():
    """تحديث أسعار جميع الصفقات"""
    trades = load_trades()
    for trade in trades:
        try:
            ticker = get_flexible_ticker(trade["symbol"])
            stock = yf.Ticker(ticker)
            df = stock.history(period="1d")
            if not df.empty:
                current = df['Close'].iloc[-1]
                profit_pct = ((current - trade["entry_price"]) / trade["entry_price"]) * 100
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('UPDATE trades SET current_price = ?, profit_pct = ? WHERE id = ?', 
                               (current, profit_pct, trade["id"]))
                conn.commit()
                conn.close()
        except:
            pass

# 5. دوال التحليل
def calculate_risk_reward(entry, target, stop_loss):
    """حساب نسبة المخاطرة/العائد"""
    risk = entry - stop_loss if stop_loss < entry else stop_loss - entry
    reward = target - entry
    if risk <= 0:
        return 0
    return reward / risk

def get_risk_level(risk_reward):
    """تحديد مستوى المخاطرة"""
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
    update_trade_prices()
    
    # شريط المؤشرات
    st.markdown("""
    <div class="ticker-wrapper">
        <span class="ticker-item"><span style="color:#888;">EGX30:</span> <span style="color:#00ff88;">51,760.97 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">S&P 500:</span> <span style="color:#00ff88;">7,230.11 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">TASI:</span> <span style="color:#ff4444;">12,450.33 ▼</span></span>
        <span class="ticker-item"><span style="color:#888;">السيولة:</span> <span style="color:#00b4d8;">2.5B</span></span>
    </div>
    """, unsafe_allow_html=True)
    
    # الهيدر
    st.markdown("""
    <div class="main-header">
        <div>
            <span class="logo-title">🔄 البورصجي AI</span>
            <span style="font-size: 12px; color: #888;">النسخة المرنة - Flexible Edition</span>
        </div>
        <div style="display: flex; gap: 15px;">
            <span style="font-size: 12px;">📅 """ + datetime.now().strftime("%Y-%m-%d") + """</span>
            <span style="color: #00ffcc; font-size: 12px;">● LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة التحكم", "📒 مفكرة الصفقات", "🎯 إدارة المخاطر", "📄 التقارير"])
    
    # ====================== التبويب 1: لوحة التحكم ======================
    with tab1:
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 إجمالي المستثمر", f"{stats['total_invested']:,.0f}")
        col2.metric("📈 القيمة الحالية", f"{stats['total_current']:,.0f}")
        col3.metric("📊 إجمالي الربح", f"{stats['total_profit']:+,.0f}", f"{stats['profit_pct']:+.1f}%")
        col4.metric("🏆 نسبة النجاح", f"{stats['win_rate']:.1f}%")
        
        # رسم بياني
        if trades:
            profit_data = [{"السهم": t["symbol"], "الربح": t.get("profit_pct", 0)} for t in trades[:10]]
            df_profit = pd.DataFrame(profit_data)
            
            fig = go.Figure(data=[go.Bar(
                x=df_profit["السهم"], y=df_profit["الربح"],
                marker_color=["#00ff88" if x > 0 else "#ff4444" for x in df_profit["الربح"]],
                text=df_profit["الربح"].apply(lambda x: f"{x:+.1f}%"),
                textposition="outside"
            )])
            fig.update_layout(template="plotly_dark", height=400, title="توزيع الأرباح - آخر 10 صفقات")
            st.plotly_chart(fig, use_container_width=True)
    
    # ====================== التبويب 2: مفكرة الصفقات (مع فلاتر وتعديل) ======================
    with tab2:
        st.markdown("### 📒 مفكرة الصفقات المرنة")
        st.caption("🔍 يمكنك البحث والفلترة وتعديل الأهداف بسهولة")
        
        # نموذج إضافة صفقة جديدة
        with st.expander("➕ إضافة صفقة جديدة", expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                new_symbol = st.text_input("الرمز", placeholder="COMI أو AAPL").upper()
            with col2:
                entry_price = st.number_input("سعر الدخول", min_value=0.0, step=0.5)
            with col3:
                target_price = st.number_input("المستهدف 🎯", min_value=0.0, step=0.5)
            with col4:
                stop_loss = st.number_input("وقف الخسارة 🛡️", min_value=0.0, step=0.5, value=entry_price * 0.95 if entry_price > 0 else 0)
            with col5:
                quantity = st.number_input("الكمية", min_value=1, step=1)
            
            sector = st.selectbox("القطاع", ["بنوك", "عقارات", "صناعة", "تكنولوجيا", "اتصالات", "طاقة", "استهلاكي"])
            
            if st.button("💾 حفظ الصفقة", use_container_width=True):
                if new_symbol and entry_price > 0 and target_price > 0:
                    trade = {
                        "symbol": new_symbol,
                        "entry_price": entry_price,
                        "target_price": target_price,
                        "stop_loss": stop_loss if stop_loss > 0 else entry_price * 0.95,
                        "quantity": quantity,
                        "sector": sector,
                        "date": datetime.now().isoformat()
                    }
                    save_trade(trade)
                    st.success(f"✅ تم إضافة {new_symbol} {get_market_flag(new_symbol)}")
                    st.rerun()
                else:
                    st.error("يرجى إدخال جميع البيانات المطلوبة")
        
        st.markdown("---")
        
        # ====================== نظام الفلاتر والبحث ======================
        trades = load_trades()
        
        if trades:
            col_search, col_filter, col_status = st.columns([2, 1, 1])
            with col_search:
                search_query = st.text_input("🔍 بحث برمز السهم", placeholder="مثال: COMI")
            with col_filter:
                sectors = ["الكل"] + list(set([t.get("sector", "غير محدد") for t in trades]))
                filter_sector = st.selectbox("📁 فلترة بالقطاع", sectors)
            with col_status:
                filter_status = st.selectbox("📊 فلترة بالحالة", ["الكل", "رابح 🟢", "خاسر 🔴", "معلق 🟡"])
            
            # تطبيق الفلاتر
            filtered_trades = trades.copy()
            
            if search_query:
                filtered_trades = [t for t in filtered_trades if search_query.upper() in t["symbol"].upper()]
            
            if filter_sector != "الكل":
                filtered_trades = [t for t in filtered_trades if t.get("sector") == filter_sector]
            
            if filter_status == "رابح 🟢":
                filtered_trades = [t for t in filtered_trades if t.get("profit_pct", 0) >= 0]
            elif filter_status == "خاسر 🔴":
                filtered_trades = [t for t in filtered_trades if t.get("profit_pct", 0) < 0]
            elif filter_status == "معلق 🟡":
                filtered_trades = [t for t in filtered_trades if abs(t.get("profit_pct", 0)) < 1]
            
            st.caption(f"📊 عرض {len(filtered_trades)} من أصل {len(trades)} صفقة")
            st.markdown("---")
            
            # عرض الصفقات
            for trade in filtered_trades:
                current_price = trade.get("current_price", trade["entry_price"])
                profit_pct = trade.get("profit_pct", 0)
                profit_class = "profit-positive" if profit_pct >= 0 else "profit-negative"
                
                # حساب نسبة المخاطرة/العائد
                stop = trade.get("stop_loss", trade["entry_price"] * 0.95)
                risk_reward = calculate_risk_reward(trade["entry_price"], trade["target_price"], stop)
                risk_level, risk_text = get_risk_level(risk_reward)
                
                # حساب المسافة للهدف
                dist_to_target = trade["target_price"] - current_price
                progress = min(100, max(0, ((current_price - trade["entry_price"]) / (trade["target_price"] - trade["entry_price"])) * 100)) if trade["target_price"] != trade["entry_price"] else 0
                
                st.markdown(f"""
                <div class="trade-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: bold; font-size: 16px;">{trade['symbol']} {get_market_flag(trade['symbol'])}</span>
                            <span style="font-size: 10px; color: #888; margin-right: 10px;">{trade.get('sector', 'غير محدد')}</span>
                        </div>
                        <div class="{profit_class}">{profit_pct:+.1f}%</div>
                    </div>
                    <div style="font-size: 12px; margin: 8px 0;">
                        💰 الدخول: {trade['entry_price']:.2f} | 🎯 الهدف: {trade['target_price']:.2f} | 🛡️ وقف: {stop:.2f}<br>
                        📊 الحالي: {current_price:.2f}
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {progress}%;"></div>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 8px;">
                        <span class="risk-{risk_level}">⚖️ المخاطرة: {risk_text}</span>
                        <span class="risk-low">🎯 متبقي: {dist_to_target:+.2f}</span>
                        <span class="risk-medium">📊 العائد/المخاطرة: 1:{risk_reward:.1f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # أزرار التحكم
                col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                with col1:
                    with st.expander(f"✏️ تعديل {trade['symbol']}"):
                        new_target = st.number_input("الهدف الجديد", value=float(trade["target_price"]), step=0.5, key=f"target_{trade['id']}")
                        new_stop = st.number_input("وقف الخسارة الجديد", value=float(stop), step=0.5, key=f"stop_{trade['id']}")
                        if st.button("💾 حفظ التعديل", key=f"save_{trade['id']}"):
                            update_trade(trade['id'], new_target, new_stop)
                            st.success("تم تحديث الصفقة")
                            st.rerun()
                with col2:
                    if st.button(f"📢 تنبيه", key=f"alert_{trade['id']}"):
                        st.toast(f"✅ تم إرسال تنبيه لـ {trade['symbol']}")
                with col3:
                    if st.button(f"🗑️ حذف", key=f"del_{trade['id']}"):
                        delete_trade(trade['id'])
                        st.rerun()
                with col4:
                    if profit_pct >= 5:
                        st.success("🎯 قريب من الهدف - رفع وقف الخسارة!")
                    elif profit_pct <= -3:
                        st.warning("⚠️ قريب من وقف الخسارة - راجع الصفقة!")
        else:
            st.info("📭 لا توجد صفقات. أضف صفقتك الأولى باستخدام النموذج أعلاه")
    
    # ====================== التبويب 3: إدارة المخاطر ======================
    with tab3:
        st.markdown("### 🎯 إدارة المخاطر المرنة")
        st.caption("تحليل نسبة المخاطرة/العائد لكل صفقة")
        
        trades = load_trades()
        
        if trades:
            risk_data = []
            for trade in trades:
                stop = trade.get("stop_loss", trade["entry_price"] * 0.95)
                risk_reward = calculate_risk_reward(trade["entry_price"], trade["target_price"], stop)
                risk_level, _ = get_risk_level(risk_reward)
                
                risk_data.append({
                    "السهم": trade["symbol"],
                    "سعر الدخول": trade["entry_price"],
                    "الهدف": trade["target_price"],
                    "وقف الخسارة": stop,
                    "نسبة المخاطرة/العائد": f"1:{risk_reward:.1f}",
                    "مستوى المخاطرة": "🟢 منخفضة" if risk_level == "low" else "🟡 متوسطة" if risk_level == "medium" else "🔴 عالية"
                })
            
            df_risk = pd.DataFrame(risk_data)
            st.dataframe(df_risk, use_container_width=True, hide_index=True)
            
            # نصائح ذكية
            st.markdown("---")
            st.markdown("### 🧠 توصيات العقل المدبر")
            
            high_risk_trades = [t for t in trades if calculate_risk_reward(t["entry_price"], t["target_price"], t.get("stop_loss", t["entry_price"] * 0.95)) < 1.5]
            if high_risk_trades:
                st.warning(f"⚠️ {len(high_risk_trades)} صفقات ذات مخاطرة عالية. نوصي بمراجعة أهدافها.")
            else:
                st.success("✅ جميع صفقاتك ضمن مستويات المخاطرة المقبولة")
        else:
            st.info("📭 لا توجد صفقات لعرضها")
    
    # ====================== التبويب 4: التقارير ======================
    with tab4:
        st.markdown("### 📄 التقارير والتحليلات")
        
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        col1, col2 = st.columns(2)
        col1.metric("📊 إجمالي الصفقات", len(trades))
        col2.metric("🎯 متوسط العائد", f"{stats['profit_pct']:+.1f}%")
        
        if trades:
            # توزيع القطاعات
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
                fig.update_layout(template="plotly_dark", height=400, title="توزيع الاستثمارات حسب القطاع")
                st.plotly_chart(fig, use_container_width=True)
            
            # زر تصدير
            if st.button("📥 تصدير التقرير", use_container_width=True):
                df = pd.DataFrame(trades)
                csv = df.to_csv(index=False)
                st.download_button("تحميل CSV", csv, "boursagi_report.csv", "text/csv")
    
    # تذييل
    st.markdown(f"""
    <div class="footer">
        🔄 البورصجي AI | النسخة المرنة - دعم جميع الأسواق<br>
        📊 تحديث لحظي • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
