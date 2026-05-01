# app.py - التطبيق الرئيسي (النسخة النهائية المتكاملة)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import time

# استيراد الملفات المحلية
from config import APP_CONFIG, RISK_CONFIG, SUPPORTED_MARKETS, get_market_flag, get_flexible_ticker
from database import (
    load_trades, save_trade, update_trade, delete_trade, close_trade,
    get_setting, update_setting, save_daily_stats, get_performance_history,
    add_alert, get_pending_alerts, mark_alert_sent
)
from market_scanner import get_market_opportunities, scan_stock
from telegram_bot import init_telegram, send_trade_alert, send_daily_report
from report_generator import generate_performance_chart, generate_risk_report, generate_summary_report

# 1. إعدادات الصفحة
st.set_page_config(
    page_title=f"{APP_CONFIG['name']} - {APP_CONFIG['version']}",
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
        background: linear-gradient(135deg, #090b10 0%, #0d1117 100%) !important;
    }
    
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 25px;
        background: rgba(13, 17, 23, 0.95);
        border-bottom: 1px solid #00ffcc30;
        margin-bottom: 20px;
        border-radius: 0;
    }
    
    .logo-title {
        font-size: 26px;
        font-weight: 800;
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .logo-sub {
        font-size: 11px;
        color: #00ffcc80;
        margin-right: 10px;
    }
    
    .live-badge {
        display: inline-block;
        background: #ff0000;
        color: white;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 20px;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .trade-card {
        background: rgba(13, 17, 23, 0.9);
        border: 1px solid #1c222d;
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .trade-card:hover {
        border-color: #00ffcc;
        transform: translateX(-5px);
        box-shadow: 0 5px 20px rgba(0, 255, 204, 0.1);
    }
    
    .profit-positive {
        color: #00ff88;
        font-weight: bold;
    }
    
    .profit-negative {
        color: #ff4444;
        font-weight: bold;
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
        transition: width 0.5s ease;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .stat-card {
        background: rgba(13, 17, 23, 0.9);
        border: 1px solid #1c222d;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        border-color: #00ffcc;
        transform: translateY(-2px);
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: bold;
        background: linear-gradient(135deg, #fff, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 10px;
    }
    
    .risk-high {
        background: rgba(255, 68, 68, 0.2);
        color: #ff4444;
    }
    
    .risk-medium {
        background: rgba(255, 170, 0, 0.2);
        color: #ffaa00;
    }
    
    .risk-low {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
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
        border-radius: 25px !important;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# 3. دوال تحديث الأسعار
def update_all_prices():
    """تحديث أسعار جميع الصفقات"""
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
                
                # تحديث أعلى سعر
                highest = max(float(trade.get("highest_price", trade["entry_price"])), current)
                
                # تطبيق Trailing Stop
                if trade.get("trailing_stop", 0) > 0:
                    new_stop = highest * (1 - trade["trailing_stop"] / 100)
                    if new_stop > trade["stop_loss"]:
                        update_trade(trade["id"], stop_loss=new_stop)
                        add_alert(trade["id"], "trailing_stop", f"تم رفع وقف الخسارة إلى {new_stop:.2f}")
                        alerts.append(f"📈 {trade['symbol']}: تم رفع وقف الخسارة")
                
                # تحديث قاعدة البيانات
                update_trade(trade["id"], current_price=current, profit_pct=profit_pct, highest_price=highest)
                
                # تنبيهات
                if current >= trade["target_price"] * 0.95:
                    add_alert(trade["id"], "target_approaching", f"قرب من تحقيق الهدف ({current:.2f})")
                    alerts.append(f"🎯 {trade['symbol']}: قرب من الهدف")
                
                if current <= trade["stop_loss"] * 1.02:
                    add_alert(trade["id"], "stop_loss_approaching", f"قرب من وقف الخسارة ({current:.2f})")
                    alerts.append(f"⚠️ {trade['symbol']}: قرب من وقف الخسارة")
                    
        except Exception as e:
            continue
    
    return alerts

# 4. دوال إدارة المخاطر
def calculate_risk_reward(entry, target, stop_loss):
    risk = abs(entry - stop_loss)
    reward = abs(target - entry)
    if risk <= 0:
        return 0
    return reward / risk

def get_risk_level(risk_reward):
    if risk_reward >= 2:
        return "low", "منخفضة 🟢"
    elif risk_reward >= 1.5:
        return "medium", "متوسطة 🟡"
    else:
        return "high", "عالية 🔴"

def calculate_portfolio_stats(trades):
    if not trades:
        return {
            "total_invested": 0, "total_current": 0, "total_profit": 0,
            "profit_pct": 0, "win_rate": 0, "winning_trades": 0
        }
    
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
        "win_rate": win_rate,
        "winning_trades": winning_trades,
        "trades_count": len(trades)
    }

# 5. الواجهة الرئيسية
def main():
    # تهيئة التليجرام
    telegram_enabled = init_telegram()
    
    # تحديث الأسعار
    alerts = update_all_prices()
    
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
            <span class="logo-title">🧠 {APP_CONFIG['name']}</span>
            <span class="logo-sub">v{APP_CONFIG['version']}</span>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <span style="font-size: 12px;">📅 {datetime.now().strftime("%Y-%m-%d")}</span>
            <span style="font-size: 12px;">🕐 {datetime.now().strftime("%H:%M:%S")}</span>
            <span class="live-badge">LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 🎮 لوحة التحكم")
        
        # إعدادات رأس المال
        st.subheader("💰 إدارة رأس المال")
        capital = st.number_input("إجمالي رأس المال", value=float(get_setting("capital", "100000")), step=10000.0)
        risk_percent = st.slider("نسبة المخاطرة في الصفقة (%)", 0.5, 5.0, float(get_setting("risk_percent", "2.0")), 0.5)
        
        if capital != float(get_setting("capital", "100000")):
            update_setting("capital", str(capital))
        if risk_percent != float(get_setting("risk_percent", "2.0")):
            update_setting("risk_percent", str(risk_percent))
        
        st.markdown("---")
        
        # إعدادات التنبيهات
        st.subheader("🔔 نظام التنبيهات")
        if telegram_enabled:
            st.success("✅ تليجرام: متصل")
            if st.button("📢 اختبار التنبيه", use_container_width=True):
                from telegram_bot import send_telegram_message
                if send_telegram_message("🧠 هذا تنبيه تجريبي من البورصجي AI", "info"):
                    st.success("تم الإرسال بنجاح!")
                else:
                    st.error("فشل الإرسال")
        else:
            st.warning("⚠️ أضف مفاتيح التليجرام في secrets")
        
        st.markdown("---")
        
        # الماسح الآلي
        st.subheader("🔍 الماسح الآلي")
        if st.button("🔄 مسح السوق الآن", use_container_width=True):
            with st.spinner("جاري مسح الأسواق..."):
                opportunities = get_market_opportunities()
                if opportunities:
                    st.success(f"✅ تم العثور على {len([o for o in opportunities if o['action'] in ['buy', 'buy_weak']])} فرصة")
                    for opp in opportunities[:3]:
                        if opp['action'] in ['buy', 'buy_weak']:
                            st.markdown(f"""
                            <div style="background: rgba(0, 255, 204, 0.1); padding: 10px; border-radius: 10px; margin: 5px 0;">
                                🟢 <b>{opp['ticker']}</b> - {opp['recommendation']}<br>
                                <small>السعر: {opp['price']:.2f} | RSI: {opp['rsi']:.1f}</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد فرص حالياً")
        
        st.markdown("---")
        st.caption("🧠 العقل المدبر لإدارة المخاطر")
    
    # التبويبات الرئيسية
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 لوحة التحكم", "📒 مفكرة الصفقات", "🧠 العقل المدبر", "🔍 الماسح الآلي", "📄 التقارير"])
    
    # ====================== التبويب 1: لوحة التحكم ======================
    with tab1:
        st.markdown("### 📊 نظرة عامة على المحفظة")
        
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 إجمالي المستثمر", f"{stats['total_invested']:,.0f}")
        col2.metric("📈 القيمة الحالية", f"{stats['total_current']:,.0f}")
        col3.metric("📊 إجمالي الربح", f"{stats['total_profit']:+,.0f}", f"{stats['profit_pct']:+.1f}%")
        col4.metric("🏆 نسبة النجاح", f"{stats['win_rate']:.1f}%")
        
        if trades:
            # رسم بياني
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
            
            # توزيع القطاعات
            sectors = {}
            for trade in trades:
                sector = trade.get("sector", "غير محدد")
                sectors[sector] = sectors.get(sector, 0) + trade["quantity"]
            
            if sectors:
                fig2 = go.Figure(data=[go.Pie(
                    labels=list(sectors.keys()),
                    values=list(sectors.values()),
                    hole=0.4,
                    marker_colors=["#00ffcc", "#ff00ff", "#ffaa00", "#00ff88", "#ff4444"]
                )])
                fig2.update_layout(template="plotly_dark", height=400, title="توزيع الاستثمارات حسب القطاع")
                st.plotly_chart(fig2, use_container_width=True)
    
    # ====================== التبويب 2: مفكرة الصفقات ======================
    with tab2:
        st.markdown("### 📒 مفكرة الصفقات")
        
        # نموذج إضافة صفقة جديدة
        with st.expander("➕ إضافة صفقة جديدة", expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                symbol = st.text_input("الرمز", placeholder="COMI أو AAPL").upper()
            with col2:
                entry = st.number_input("سعر الدخول", min_value=0.01, step=0.5, value=100.0)
            with col3:
                target = st.number_input("الهدف 🎯", min_value=0.01, step=0.5, value=120.0)
            with col4:
                default_stop = float(entry * 0.95) if entry > 0 else 95.0
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
                
                risk_reward = calculate_risk_reward(trade["entry_price"], trade["target_price"], trade["stop_loss"])
                risk_level, _ = get_risk_level(risk_reward)
                
                st.markdown(f"""
                <div class="trade-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b style="font-size: 16px;">{trade['symbol']}</b> {get_market_flag(trade['symbol'])}
                            <span class="risk-badge risk-{risk_level}" style="margin-right: 10px;">⚖️ {risk_reward:.1f}</span>
                        </div>
                        <div class="{profit_class}">{profit_pct:+.1f}%</div>
                    </div>
                    <div style="font-size: 12px; margin: 8px 0;">
                        🚪 الدخول: {trade['entry_price']:.2f} | 🎯 الهدف: {trade['target_price']:.2f} | 🛡️ وقف: {trade['stop_loss']:.2f}
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {min(100, max(0, profit_pct * 2))}%;"></div>
                    </div>
                    <div style="font-size: 10px; color: #888; margin-top: 5px;">
                        الكمية: {trade['quantity']} | 
                        {'📈 Trailing Stop: ' + str(trade.get('trailing_stop', 0)) + '%' if trade.get('trailing_stop', 0) > 0 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button(f"✏️ تعديل", key=f"edit_{trade['id']}"):
                        st.session_state[f'editing_{trade["id"]}'] = True
                with col2:
                    if trade.get("trailing_stop", 0) > 0:
                        st.caption("📈 Trailing Stop مفعل")
                with col3:
                    if st.button(f"🔒 إغلاق", key=f"close_{trade['id']}"):
                        close_trade(trade['id'], trade.get('current_price', trade['entry_price']))
                        st.rerun()
                with col4:
                    if st.button(f"🗑️ حذف", key=f"del_{trade['id']}"):
                        delete_trade(trade['id'])
                        st.rerun()
                
                # نافذة التعديل
                if st.session_state.get(f'editing_{trade["id"]}', False):
                    with st.container():
                        st.markdown(f"**✏️ تعديل صفقة {trade['symbol']}**")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            new_target = st.number_input("الهدف الجديد", value=float(trade["target_price"]), step=0.5, key=f"target_{trade['id']}")
                        with col_b:
                            new_stop = st.number_input("وقف الخسارة الجديد", value=float(trade["stop_loss"]), step=0.5, key=f"stop_{trade['id']}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 حفظ", key=f"save_{trade['id']}"):
                                update_trade(trade['id'], target_price=new_target, stop_loss=new_stop)
                                st.session_state[f'editing_{trade["id"]}'] = False
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ إلغاء", key=f"cancel_{trade['id']}"):
                                st.session_state[f'editing_{trade["id"]}'] = False
                                st.rerun()
        else:
            st.info("📭 لا توجد صفقات. أضف صفقتك الأولى باستخدام النموذج أعلاه")
    
    # ====================== التبويب 3: العقل المدبر ======================
    with tab3:
        st.markdown("### 🧠 العقل المدبر - إدارة المخاطر")
        
        trades = load_trades()
        
        if trades:
            # تحليل المخاطر
            st.markdown("#### 📊 تحليل نسبة المخاطرة/العائد")
            
            risk_data = []
            for trade in trades:
                risk_reward = calculate_risk_reward(trade["entry_price"], trade["target_price"], trade["stop_loss"])
                risk_level, risk_text = get_risk_level(risk_reward)
                risk_data.append({
                    "السهم": trade["symbol"],
                    "نسبة المخاطرة/العائد": f"1:{risk_reward:.1f}",
                    "المستوى": risk_text
                })
            
            df_risk = pd.DataFrame(risk_data)
            st.dataframe(df_risk, use_container_width=True, hide_index=True)
            
            high_risk_trades = [t for t in risk_data if "عالية" in t["المستوى"]]
            if high_risk_trades:
                st.warning(f"⚠️ لديك {len(high_risk_trades)} صفقات ذات مخاطرة عالية")
                st.info("💡 **نصيحة العقل المدبر:** حاول أن يكون العائد المستهدف ضعف وقف الخسارة على الأقل (نسبة 1:2)")
            else:
                st.success("✅ جميع صفقاتك تلتزم بمعايير إدارة المخاطر الجيدة")
            
            st.markdown("---")
            
            # حاسبة حجم المركز
            st.markdown("#### 🧮 حاسبة حجم المركز")
            
            col_cap, col_risk = st.columns(2)
            with col_cap:
                total_capital = st.number_input("إجمالي رأس المال", value=float(get_setting("capital", "100000")), step=10000.0)
            with col_risk:
                risk_pct_trade = st.slider("نسبة المخاطرة في الصفقة (%)", 0.5, 5.0, float(get_setting("risk_percent", "2.0")), 0.5)
            
            amount_to_risk = total_capital * (risk_pct_trade / 100)
            st.info(f"💰 يجب ألا تخسر أكثر من **{amount_to_risk:,.2f}** في الصفقة الواحدة")
            
            # تحليل الأداء
            st.markdown("---")
            st.markdown("#### 📈 تحليل أداء المحفظة")
            
            stats = calculate_portfolio_stats(trades)
            
            if stats['win_rate'] > 70:
                st.success(f"🎯 **نسبة نجاح ممتازة!** ({stats['win_rate']:.0f}%) استمر في استراتيجيتك")
            elif stats['win_rate'] < 40:
                st.warning(f"⚠️ **نسبة النجاح تحتاج تحسين** ({stats['win_rate']:.0f}%) راجع استراتيجية الدخول")
            else:
                st.info(f"📊 **نسبة النجاح الحالية:** {stats['win_rate']:.1f}%")
            
            if stats['profit_pct'] > 10:
                st.success(f"📈 **أداء استثنائي!** أرباح {stats['profit_pct']:.1f}% تفوق السوق")
            elif stats['profit_pct'] < 0:
                st.warning(f"📉 **محفظتك في تصحيح** ({stats['profit_pct']:.1f}%) ركز على وقف الخسائر")
            
            # توصيات إضافية
            st.markdown("---")
            st.markdown("#### 💡 توصيات العقل المدبر")
            
            if len(trades) > 0:
                total_profit = stats['total_profit']
                if total_profit > 0:
                    st.success(f"✅ أرباحك الحالية: {total_profit:,.2f} - نوصي بتفعيل Trailing Stop لتأمين الأرباح")
                else:
                    st.warning(f"⚠️ خسائرك الحالية: {total_profit:,.2f} - نوصي بمراجعة استراتيجية وقف الخسارة")
        else:
            st.info("📭 أضف صفقات لبدء تحليل العقل المدبر")
    
    # ====================== التبويب 4: الماسح الآلي ======================
    with tab4:
        st.markdown("### 🔍 الماسح الآلي للأسواق")
        st.caption("البورصجي AI يبحث عن أفضل فرص الاستثمار")
        
        if st.button("🔍 بدء المسح الشامل", type="primary", use_container_width=True):
            with st.spinner("جاري مسح الأسواق العالمية..."):
                opportunities = get_market_opportunities()
                
                if opportunities:
                    st.success(f"✅ تم العثور على {len([o for o in opportunities if o['action'] in ['buy', 'buy_weak']])} فرصة")
                    
                    for opp in opportunities:
                        if opp['action'] in ['buy', 'buy_weak']:
                            st.markdown(f"""
                            <div style="background: rgba(0, 255, 204, 0.05); border: 1px solid #00ffcc30; border-radius: 12px; padding: 12px; margin: 8px 0;">
                                <div style="display: flex; justify-content: space-between;">
                                    <b>🟢 {opp['ticker']}</b>
                                    <span class="risk-badge risk-low">RSI: {opp['rsi']:.1f}</span>
                                </div>
                                <div style="font-size: 12px; margin-top: 5px;">
                                    السعر: {opp['price']:.2f} | الدعم: {opp['support']:.2f} | المقاومة: {opp['resistance']:.2f}
                                </div>
                                <div style="font-size: 11px; color: #00ffcc; margin-top: 5px;">
                                    {opp['recommendation']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if telegram_enabled:
                                from telegram_bot import send_telegram_message
                                msg = f"🔍 فرصة جديدة!\nالسهم: {opp['ticker']}\nالسعر: {opp['price']:.2f}\nRSI: {opp['rsi']:.1f}\nتوصية: {opp['recommendation']}"
                                send_telegram_message(msg, "buy")
                        else:
                            st.markdown(f"""
                            <div style="background: rgba(255, 68, 68, 0.05); border: 1px solid #ff444430; border-radius: 12px; padding: 12px; margin: 8px 0;">
                                <div style="display: flex; justify-content: space-between;">
                                    <b>🔴 {opp['ticker']}</b>
                                    <span class="risk-badge risk-high">RSI: {opp['rsi']:.1f}</span>
                                </div>
                                <div style="font-size: 12px;">
                                    {opp['recommendation']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("📭 لم يتم العثور على فرص استثمارية حالياً")
    
    # ====================== التبويب 5: التقارير ======================
    with tab5:
        st.markdown("### 📄 التقارير والتحليلات")
        
        trades = load_trades()
        stats = calculate_portfolio_stats(trades)
        
        if trades:
            # تقرير المخاطر
            st.markdown("#### 📊 تقرير المخاطر")
            risk_df = generate_risk_report(trades)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
            
            # ملخص الأداء
            st.markdown("#### 📈 ملخص الأداء")
            summary = generate_summary_report(trades, stats)
            st.code(summary, language="text")
            
            # زر تصدير
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 تصدير التقرير (CSV)", use_container_width=True):
                    from report_generator import export_report_to_csv
                    filepath = export_report_to_csv(trades)
                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                        st.download_button("تحميل", f, filepath.name, "text/csv")
            
            with col2:
                if st.button("📊 حفظ إحصائيات اليوم", use_container_width=True):
                    save_daily_stats()
                    st.success("✅ تم حفظ إحصائيات اليوم")
            
            # إرسال التقرير اليومي
            if telegram_enabled:
                st.markdown("---")
                if st.button("📱 إرسال التقرير اليومي إلى تليجرام", use_container_width=True):
                    send_daily_report(stats)
                    st.success("✅ تم إرسال التقرير إلى تليجرام")
        else:
            st.info("📭 لا توجد بيانات كافية لعرض التقارير")
    
    # تذييل
    st.markdown(f"""
    <div class="footer">
        🧠 {APP_CONFIG['name']} v{APP_CONFIG['version']} | العقل المدبر لإدارة المخاطر<br>
        📊 تحديث لحظي • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
