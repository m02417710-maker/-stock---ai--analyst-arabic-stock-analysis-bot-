# ============================================================
# app.py - الواجهة الرئيسية
# تم التصحيح: استخدام import core بدلاً من from core import *
# ============================================================

import streamlit as st
import core  # استيراد بسيط ونظيف
from strings import UI_TEXT
from datetime import datetime

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="المحلل المالي المتكامل — Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# التصميم
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #10b981;
    border-radius: 15px;
    padding: 15px;
}
.golden-signal {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 2px solid #10b981;
    border-radius: 20px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# الشريط الجانبي
# ============================================================

with st.sidebar:
    st.markdown(f"# {UI_TEXT['app_title']}")
    st.markdown("---")
    
    st.markdown(f"### {UI_TEXT['sidebar_capital']}")
    capital = st.number_input(UI_TEXT["sidebar_capital_label"], min_value=100, value=10000, step=1000)
    risk_percent = st.slider(UI_TEXT["sidebar_risk_label"], 0.5, 5.0, 2.0, 0.5)
    
    st.markdown("---")
    
    selected_name = st.selectbox("🔍 اختر السهم", list(core.STOCKS.keys()))
    ticker = core.STOCKS[selected_name]
    
    st.caption(f"📌 الرمز: `{ticker}`")
    st.markdown("---")
    
    st.markdown("### 📊 معلومات")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    st.caption(f"🔄 {UI_TEXT['sidebar_refresh']}")
    st.caption(f"📈 {UI_TEXT['sidebar_stocks_count']}: {len(core.STOCKS)}")
    
    if st.button(UI_TEXT["sidebar_update_btn"], use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# جلب البيانات
# ============================================================

st.markdown(f"## {UI_TEXT['page_title'].format(selected=selected_name)}")
st.markdown("---")

with st.spinner("🔄 جاري تحليل البيانات..."):
    df, info = core.get_data(ticker)

if df is not None and not df.empty:
    # التحليل الأساسي
    score, signals, recommendation, rec_color = core.analyze(df)
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
    change = ((current_price - prev_price) / prev_price) * 100
    
    # مونت كارلو
    with st.spinner("🔮 تشغيل محاكاة مونت كارلو..."):
        mc = core.monte_carlo_gbm(df)
    
    # إدارة المخاطر
    shares, position, actual_risk, risk_advice = core.risk_management(capital, current_price, 5, risk_percent)
    
    # الأهداف
    target_price = df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else current_price * 1.07
    stop_price = current_price * 0.95
    
    # بطاقات
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(UI_TEXT["metric_price"], f"{current_price:.2f}", f"{change:+.2f}%")
    col2.metric(UI_TEXT["metric_confidence"], f"{score}/5")
    col3.metric(UI_TEXT["metric_rsi"], f"{df['RSI'].iloc[-1]:.1f}")
    col4.metric(UI_TEXT["metric_position"], f"${position:,.2f}")
    
    if mc:
        col5, col6, col7, col8 = st.columns(4)
        col5.metric(UI_TEXT["metric_profit_prob"], f"{mc['profit_prob']:.0f}%")
        col6.metric(UI_TEXT["metric_target_10"], f"{mc['target_10_prob']:.0f}%")
        col7.metric(UI_TEXT["metric_var_95"], f"{mc['var_95_pct']:.1f}%")
        col8.metric(UI_TEXT["metric_stop_prob"], f"{mc['stop_prob']:.0f}%")
    
    st.markdown("---")
    
    # التوصية
    if score >= 4:
        st.markdown(f"""
        <div class="golden-signal">
            <h1 style="color: #10b981; margin: 0;">✨ إشارة ذهبية ✨</h1>
            <h2 style="color: #10b981;">{recommendation}</h2>
            <p>🎯 هدف: {target_price:.2f} | 🛑 وقف: {stop_price:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 2px solid {rec_color};
                    border-radius: 20px; padding: 20px;
                    text-align: center;">
            <h2 style="color: {rec_color};">{recommendation}</h2>
            <p>🎯 هدف: {target_price:.2f} | 🛑 وقف: {stop_price:.2f}</p>
            <p style="font-size: 12px;">{risk_advice}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["📈 الرسم البياني", "📋 التحليل", "🔍 الماسح"])
    
    with tab1:
        fig = core.create_chart(df, ticker, selected_name, target_price, stop_price)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        for s in signals:
            if "✅" in s or "🔥" in s or "💰" in s:
                st.success(s)
            elif "⚠️" in s:
                st.warning(s)
            else:
                st.info(s)
        
        st.markdown("---")
        st.markdown("**نقاط التداول**")
        st.markdown(f"- نقطة الدخول: {current_price:.2f}")
        st.markdown(f"- الهدف الأول: {target_price:.2f}")
        st.markdown(f"- الهدف الثاني: {current_price * 1.08:.2f}")
        st.markdown(f"- وقف الخسارة: {stop_price:.2f}")
    
    with tab3:
        if st.button("تشغيل الماسح", use_container_width=True):
            with st.spinner("جاري المسح..."):
                results = core.scan_market_parallel()
                if not results.empty:
                    st.dataframe(results, use_container_width=True, hide_index=True)
                else:
                    st.warning("لا توجد بيانات")

else:
    st.error(UI_TEXT["error_fetch"])
    st.info(UI_TEXT["error_solutions"])

# تذييل
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    🚀 {UI_TEXT['footer']}<br>
    🔄 تحديث تلقائي كل 5 دقائق
</div>
""", unsafe_allow_html=True)
