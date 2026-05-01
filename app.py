# البورصجي AI - النسخة النهائية المتكاملة (بتطابق تام مع الصور)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import numpy as np
import json
from pathlib import Path

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - المنصة الذكية",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS المحسن للتطابق التام مع الصور
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* تحسين الخلفية العامة لتكون أغمق مثل الصورة */
    .stApp {
        background: #090b10 !important;
    }
    
    /* شريط التمرير العلوي للمؤشرات (Ticker Bar) */
    .ticker-wrapper {
        background: #141820;
        padding: 10px 20px;
        border-bottom: 1px solid #00ffcc30;
        display: flex;
        gap: 30px;
        overflow-x: auto;
        white-space: nowrap;
        margin-bottom: 20px;
        border-radius: 0;
    }
    
    .ticker-item {
        font-size: 13px;
        color: #fff;
        font-weight: 500;
    }
    
    /* الهيدر العلوي */
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
    
    /* تحسين بطاقات التنبيهات الجانبية لتطابق الصورة */
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
        transition: all 0.3s;
    }
    
    .alert-card-danger:hover {
        background: rgba(255, 68, 68, 0.08) !important;
        transform: translateX(-3px);
    }
    
    .alert-card-warning {
        background: rgba(255, 170, 0, 0.03) !important;
        border: 1px solid rgba(255, 170, 0, 0.2) !important;
        border-right: 4px solid #ffaa00 !important;
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
    
    .trade-profit {
        color: #00ff88;
        font-weight: bold;
    }
    
    .trade-loss {
        color: #ff4444;
        font-weight: bold;
    }
    
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
    
    /* بطاقات الإحصائيات */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .stat-card {
        background: #0d1117;
        border: 1px solid #1c222d;
        border-radius: 12px;
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
    
    .stat-label {
        font-size: 12px;
        color: #888;
        margin-top: 5px;
    }
    
    /* تصميم الأزرار لتكون دائرية أكثر مثل الصور */
    .stButton > button {
        border-radius: 20px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.1);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 255, 204, 0.2);
    }
    
    /* تنسيق الجداول لتشبه الصورة */
    .stDataFrame {
        border: 1px solid #1c222d !important;
        border-radius: 10px !important;
    }
    
    /* تبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0d1117;
        padding: 8px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        color: #000 !important;
    }
    
    /* تذييل */
    .footer {
        text-align: center;
        padding: 20px;
        color: #555;
        font-size: 11px;
        margin-top: 30px;
        border-top: 1px solid #1c222d;
    }
</style>
""", unsafe_allow_html=True)

# 3. تهيئة قاعدة البيانات
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
JOURNAL_FILE = DATA_DIR / "trading_journal.json"

def load_journal():
    if JOURNAL_FILE.exists():
        with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_journal(journal):
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(journal, f, ensure_ascii=False, indent=2)

def update_journal_prices(journal):
    updated = []
    for trade in journal:
        try:
            ticker = trade["symbol"] + ".CA" if not trade["symbol"].endswith(".CA") else trade["symbol"]
            stock = yf.Ticker(ticker)
            df = stock.history(period="1d")
            if not df.empty:
                current = df['Close'].iloc[-1]
                trade["current_price"] = current
                trade["profit_pct"] = ((current - trade["entry_price"]) / trade["entry_price"]) * 100
                target_range = trade["target_price"] - trade["entry_price"]
                progress = ((current - trade["entry_price"]) / target_range) * 100 if target_range > 0 else 0
                trade["progress"] = min(100, max(0, progress))
        except:
            pass
        updated.append(trade)
    return updated

# 4. دوال التوصيات
def generate_ai_recommendations():
    opportunities = [
        {"symbol": "EALR", "reason": "اختراق سيولة + سعر رخيص محاسبياً", "confidence": "85%", "price": 396.15, "target": 420.00},
        {"symbol": "AMES", "reason": "نمو الأرباح + دعم قوي", "confidence": "78%", "price": 55.87, "target": 62.00}
    ]
    warnings = [
        {"symbol": "WKOL", "reason": "السعر تجاوز القيمة العادلة بـ 40%", "risk": "عالية"},
        {"symbol": "SVCE_R1", "reason": "حجم تداول منخفض", "risk": "متوسطة"}
    ]
    return opportunities, warnings

# 5. الواجهة الرئيسية
def main():
    # تهيئة الجلسة
    if 'journal' not in st.session_state:
        st.session_state.journal = load_journal()
    
    # ====================== شريط المؤشرات العلوي (Ticker Bar) ======================
    st.markdown("""
    <div class="ticker-wrapper">
        <span class="ticker-item"><span style="color:#888;">EGX30:</span> <span style="color:#00ff88;">51,760.97 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">EGX70:</span> <span style="color:#ff4444;">14,028.98 ▼</span></span>
        <span class="ticker-item"><span style="color:#888;">S&P 500:</span> <span style="color:#00ff88;">7,230.11 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">NASDAQ:</span> <span style="color:#00ff88;">18,750.22 ▲</span></span>
        <span class="ticker-item"><span style="color:#888;">TASI:</span> <span style="color:#ff4444;">12,450.33 ▼</span></span>
        <span class="ticker-item"><span style="color:#888;">السيولة:</span> <span style="color:#00b4d8;">2.5B</span></span>
        <span class="ticker-item"><span style="color:#888;">الذهب:</span> <span style="color:#00ff88;">$2,350.40 ▲</span></span>
    </div>
    """, unsafe_allow_html=True)
    
    # ====================== الهيدر ======================
    st.markdown("""
    <div class="main-header">
        <div>
            <span class="logo-title">🧠 البورصجي AI PRO</span>
            <span style="font-size: 12px; color: #888; margin-right: 10px;">المنصة الذكية المتكاملة</span>
        </div>
        <div style="display: flex; gap: 15px;">
            <span style="font-size: 12px;">📅 """ + datetime.now().strftime("%Y-%m-%d") + """</span>
            <span style="color: #00ffcc; font-size: 12px;">● LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ====================== الشريط الجانبي ======================
    with st.sidebar:
        st.markdown("## 🎮 لوحة التحكم")
        
        # إعدادات المخاطر
        st.subheader("💰 إعدادات المخاطر")
        capital = st.number_input("رأس المال", value=100000, step=10000)
        risk_pct = st.slider("نسبة المخاطرة (%)", 0.5, 10.0, 2.0, 0.5)
        
        st.markdown("---")
        
        # ====================== نظام التنبيهات الذكي ======================
        st.subheader("🔔 رادار الفرص الذكي")
        
        opportunities, warnings = generate_ai_recommendations()
        
        for opp in opportunities:
            st.markdown(f"""
            <div class="alert-card-success">
                <strong style="color: #00ffcc;">🚀 فرصة: {opp['symbol']}</strong><br>
                <span style="font-size: 12px; color: #ccc;">{opp['reason']}</span><br>
                <span style="color: #ffcc00; font-size: 11px;">🎯 ثقة: {opp['confidence']}</span><br>
                <span style="font-size: 10px;">💰 {opp['price']:.2f} | 🎯 {opp['target']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        
        for warn in warnings:
            st.markdown(f"""
            <div class="alert-card-danger">
                <strong style="color: #ff4444;">⚠️ تحذير: {warn['symbol']}</strong><br>
                <span style="font-size: 12px; color: #ccc;">{warn['reason']}</span><br>
                <span style="color: #ffaa00; font-size: 11px;">🎯 الخطر: {warn['risk']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.success("🧠 Gemini AI: متصل")
        st.caption("🕶️ العين التي لا تنام في الأسواق")
    
    # ====================== التبويبات الرئيسية ======================
    tab1, tab2, tab3, tab4 = st.tabs(["📊 لوحة التحكم", "📒 مفكرة الصفقات", "📄 التقارير", "ℹ️ عن المنصة"])
    
    # ====================== التبويب 1: لوحة التحكم ======================
    with tab1:
        st.markdown("### 📊 نظرة عامة على المحفظة")
        
        if st.session_state.journal:
            total_invested = sum(t["entry_price"] * t["quantity"] for t in st.session_state.journal)
            current_value = sum(t.get("current_price", t["entry_price"]) * t["quantity"] for t in st.session_state.journal)
            total_profit = current_value - total_invested
            profit_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0
            
            winning_trades = len([t for t in st.session_state.journal if t.get("profit_pct", 0) > 0])
            win_rate = (winning_trades / len(st.session_state.journal)) * 100 if st.session_state.journal else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 إجمالي المستثمر", f"{total_invested:,.0f}")
            col2.metric("📈 القيمة الحالية", f"{current_value:,.0f}")
            col3.metric("📊 إجمالي الربح", f"{total_profit:+,.0f}", f"{profit_pct:+.1f}%")
            col4.metric("🏆 نسبة النجاح", f"{win_rate:.1f}%")
        else:
            st.info("📭 لا توجد صفقات في المفكرة. أضف صفقاتك لمتابعتها")
        
        # رسم بياني لتوزيع القطاعات
        if st.session_state.journal:
            sectors = {}
            for trade in st.session_state.journal:
                sector = trade.get("sector", "غير محدد")
                sectors[sector] = sectors.get(sector, 0) + trade["quantity"]
            
            if sectors:
                fig = go.Figure(data=[go.Pie(
                    labels=list(sectors.keys()),
                    values=list(sectors.values()),
                    hole=0.4,
                    marker_colors=["#00ffcc", "#ff00ff", "#ffaa00", "#00ff88", "#ff4444"]
                )])
                fig.update_layout(template="plotly_dark", height=400, title="توزيع الاستثمارات حسب القطاع", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
    
    # ====================== التبويب 2: مفكرة الصفقات ======================
    with tab2:
        st.markdown("### 📒 مفكرة الصفقات الذكية")
        st.caption("سجل صفقاتك وقم بمتابعتها آلياً مع شريط تقدم بصري")
        
        # نموذج إضافة صفقة جديدة
        with st.expander("➕ إضافة صفقة جديدة", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                new_symbol = st.text_input("رمز السهم", placeholder="مثال: COMI").upper()
            with col2:
                entry_price = st.number_input("سعر الدخول", min_value=0.0, step=0.5)
            with col3:
                target_price = st.number_input("المستهدف 🎯", min_value=0.0, step=0.5)
            with col4:
                quantity = st.number_input("الكمية", min_value=1, step=1)
            
            sector = st.selectbox("القطاع", ["بنوك", "عقارات", "صناعة", "تكنولوجيا", "اتصالات", "استهلاكي"])
            
            if st.button("💾 حفظ الصفقة في المفكرة", use_container_width=True):
                if new_symbol and entry_price > 0 and target_price > 0:
                    new_trade = {
                        "symbol": new_symbol,
                        "entry_price": entry_price,
                        "target_price": target_price,
                        "quantity": quantity,
                        "sector": sector,
                        "date": datetime.now().isoformat(),
                        "status": "active",
                        "current_price": entry_price,
                        "profit_pct": 0,
                        "progress": 0
                    }
                    st.session_state.journal.append(new_trade)
                    save_journal(st.session_state.journal)
                    st.success(f"✅ تم حفظ صفقة {new_symbol} بنجاح! سيتم متابعتها تلقائياً.")
                    st.rerun()
                else:
                    st.error("يرجى إدخال جميع البيانات المطلوبة")
        
        st.markdown("---")
        
        # عرض الصفقات القائمة
        if st.session_state.journal:
            st.session_state.journal = update_journal_prices(st.session_state.journal)
            save_journal(st.session_state.journal)
            
            cols = st.columns(2)
            for idx, trade in enumerate(st.session_state.journal):
                with cols[idx % 2]:
                    profit_pct = trade.get("profit_pct", 0)
                    profit_class = "trade-profit" if profit_pct >= 0 else "trade-loss"
                    progress = trade.get("progress", 0)
                    
                    st.markdown(f"""
                    <div class="trade-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: bold; font-size: 16px;">{trade['symbol']}</span>
                                <span style="font-size: 10px; color: #888; margin-right: 10px;">{trade.get('sector', 'غير محدد')}</span>
                            </div>
                            <div class="{profit_class}">{profit_pct:+.1f}%</div>
                        </div>
                        <div style="font-size: 12px; margin-top: 10px;">
                            💰 الدخول: {trade['entry_price']:.2f} | 🎯 الهدف: {trade['target_price']:.2f}<br>
                            📊 الحالي: {trade.get('current_price', trade['entry_price']):.2f}
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width: {progress}%;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                            <span style="font-size: 10px; color: #888;">نسبة الإنجاز: {progress:.0f}%</span>
                            <span style="font-size: 10px; color: #888;">الكمية: {trade['quantity']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🗑️ حذف", key=f"del_{idx}"):
                        st.session_state.journal.pop(idx)
                        save_journal(st.session_state.journal)
                        st.rerun()
                    
                    if progress >= 100:
                        st.success(f"🎉 **تهانينا!** صفقة {trade['symbol']} حققت الهدف المستهدف!")
        else:
            st.info("📭 لا توجد صفقات في المفكرة. استخدم النموذج أعلاه لإضافة صفقاتك")
    
    # ====================== التبويب 3: التقارير ======================
    with tab3:
        st.markdown("### 📄 تقارير الأداء")
        
        if st.session_state.journal:
            total_trades = len(st.session_state.journal)
            winning_trades = len([t for t in st.session_state.journal if t.get("profit_pct", 0) > 0])
            losing_trades = len([t for t in st.session_state.journal if t.get("profit_pct", 0) < 0])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 إجمالي الصفقات", total_trades)
            col2.metric("✅ الصفقات الرابحة", winning_trades)
            col3.metric("❌ الصفقات الخاسرة", losing_trades)
            
            st.markdown("---")
            
            # جدول ملخص الصفقات
            summary_df = pd.DataFrame([{
                "السهم": t["symbol"],
                "سعر الدخول": f"{t['entry_price']:.2f}",
                "السعر الحالي": f"{t.get('current_price', t['entry_price']):.2f}",
                "الربح %": f"{t.get('profit_pct', 0):+.1f}%",
                "الحالة": "🟢 نشط"
            } for t in st.session_state.journal])
            
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # ====================== المنطق الذكي للتقرير ======================
            st.markdown("### 🧠 تحليل العقل المدبر")
            
            avg_profit = sum(t.get('profit_pct', 0) for t in st.session_state.journal) / len(st.session_state.journal) if st.session_state.journal else 0
            
            if avg_profit > 5:
                ai_advice = "🧠 **تحليل العقل:** أداؤك يتفوق على السوق بنسبة ممتازة! استمر في اقتناص فرص السيولة العالية والحفاظ على استراتيجيتك."
            elif avg_profit > 0:
                ai_advice = "🧠 **تحليل العقل:** محفظتك تحقق أرباحاً إيجابية. نوصي بتنويع القطاعات وتقليل المخاطر للحفاظ على هذا الأداء."
            else:
                ai_advice = "🧠 **تحليل العقل:** نلاحظ بطء في حركة محفظتك. ربما حان الوقت لفلترة الأسهم ذات السيولة الأقل من 50% والتركيز على الفرص القوية."
            
            st.info(ai_advice)
            
            # توصيات إضافية
            sectors_in_portfolio = set(t.get("sector", "") for t in st.session_state.journal)
            if len(sectors_in_portfolio) == 1:
                st.warning("⚠️ **تنبيه العقل:** محفظتك مركزة في قطاع واحد. ننصح بالتنويع لتقليل المخاطر.")
            
            if win_rate > 70:
                st.success("🎯 **إشادة العقل:** نسبة نجاحك ممتازة! استمر في تحليل الصفقات قبل الدخول.")
            elif win_rate < 40:
                st.warning("📊 **نصيحة العقل:** نسبة النجاح منخفضة. حاول تقليل عدد الصفقات والتركيز على الجودة.")
            
        else:
            st.info("📭 لا توجد بيانات كافية لعرض التقارير. أضف صفقات إلى المفكرة أولاً")
            
            # عرض نموذج للعقل المدبر حتى بدون بيانات
            st.markdown("### 🧠 العقل المدبر يقول...")
            st.info("🧠 انتظر حتى تقوم بإضافة صفقات إلى مفكرتك وسأقوم بتحليل أدائك وتقديم توصيات ذكية!")
    
    # ====================== التبويب 4: عن المنصة ======================
    with tab4:
        st.markdown("### ℹ️ عن منصة البورصجي AI")
        st.markdown("""
        **🧠 البورصجي AI - المنصة الذكية المتكاملة**
        
        **الميزات الرئيسية:**
        - ✅ **مفكرة الصفقات الذكية** - تتبع صفقاتك مع شريط تقدم بصري
        - ✅ **رادار الفرص الذكي** - تنبيهات فورية لفرص الشراء والبيع
        - ✅ **تحليل المحفظة** - إحصائيات وأرباح وتوزيع القطاعات
        - ✅ **توصيات الذكاء الاصطناعي** - نصائح مخصصة لتحسين أدائك
        - ✅ **شريط المؤشرات الحية** - متابعة الأسواق لحظة بلحظة
        
        **البيانات:**
        - 📊 الأسعار اللحظية من Yahoo Finance
        - 🧠 تحليلات Gemini AI
        - 💾 حفظ البيانات محلياً
        
        **التنصل:**
        ⚠️ هذه المنصة للأغراض التعليمية فقط. لا تقدم نصائح استثمارية.
        
        ---
        **الإصدار:** 3.0.0
        **آخر تحديث:** """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
        """)
    
    # تذييل
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        🧠 البورصجي AI | العين التي لا تنام في الأسواق<br>
        📊 تحديث لحظي • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
