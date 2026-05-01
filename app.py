# ============================================================
# app.py - الواجهة الرئيسية (نسخة بسيطة ومضمونة)
# ============================================================

import streamlit as st
import core
from datetime import datetime

st.set_page_config(
    page_title="المحلل المالي المتكامل",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# واجهة جانبية
# ============================================================

with st.sidebar:
    st.markdown("# 📊 المحلل المالي المتكامل")
    st.markdown("---")
    
    capital = st.number_input("💰 رأس المال ($)", min_value=100, value=10000, step=1000)
    risk_pct = st.slider("⚡ نسبة المخاطرة (%)", 0.5, 5.0, 2.0, 0.5)
    
    st.markdown("---")
    
    # استخدام STOCKS من core
    selected = st.selectbox("🔍 اختر السهم", list(core.STOCKS.keys()))
    ticker = core.STOCKS[selected]
    
    st.caption(f"📌 الرمز: `{ticker}`")
    st.markdown("---")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 تحديث", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# العنوان
# ============================================================

st.markdown(f"## تحليل {selected}")
st.markdown("---")

# ============================================================
# جلب البيانات
# ============================================================

with st.spinner("جاري التحليل..."):
    df, info = core.get_data(ticker)

if df is not None and not df.empty:
    score, signals, rec, color = core.analyze(df)
    current = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2] if len(df) > 1 else current
    change = ((current - prev) / prev) * 100
    
    mc = core.monte_carlo_gbm(df)
    shares, position, actual_risk, advice = core.risk_management(capital, current, 5, risk_pct)
    
    # بطاقات
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 السعر", f"{current:.2f}", f"{change:+.2f}%")
    c2.metric("🎯 درجة الثقة", f"{score}/5")
    c3.metric("📊 RSI", f"{df['RSI'].iloc[-1]:.1f}")
    c4.metric("💵 حجم الصفقة", f"${position:,.2f}")
    
    if mc:
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("📈 احتمال الربح", f"{mc['profit_prob']:.0f}%")
        c6.metric("🎯 هدف +10%", f"{mc['target_10_prob']:.0f}%")
        c7.metric("⚠️ VaR 95%", f"{mc['var_95_pct']:.1f}%")
        c8.metric("📉 كسر الوقف", f"{mc['stop_prob']:.0f}%")
    
    st.markdown("---")
    
    # التوصية
    st.markdown(f"""
    <div style="background: #1e293b; border: 2px solid {color}; border-radius: 20px; padding: 20px; text-align: center;">
        <h2 style="color: {color};">{rec}</h2>
        <p>🎯 هدف: {df['Resistance'].iloc[-1]:.2f} | 🛑 وقف: {current * 0.95:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # التبويبات
    tab1, tab2, tab3 = st.tabs(["📈 الرسم البياني", "📋 التحليل", "🔍 الماسح"])
    
    with tab1:
        fig = core.create_chart(df, ticker, selected)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        for s in signals:
            if "✅" in s or "🔥" in s:
                st.success(s)
            elif "⚠️" in s:
                st.warning(s)
            else:
                st.info(s)
        
        st.markdown("---")
        st.markdown("**نقاط التداول**")
        st.markdown(f"- نقطة الدخول: {current:.2f}")
        st.markdown(f"- الهدف الأول: {df['Resistance'].iloc[-1]:.2f}")
        st.markdown(f"- الهدف الثاني: {current * 1.08:.2f}")
        st.markdown(f"- وقف الخسارة: {current * 0.95:.2f}")
    
    with tab3:
        if st.button("🚀 تشغيل الماسح", use_container_width=True):
            with st.spinner("جاري المسح..."):
                results = core.scan_market_parallel()
                if not results.empty:
                    st.dataframe(results, use_container_width=True, hide_index=True)
                else:
                    st.warning("لا توجد بيانات")

else:
    st.error("تعذر جلب البيانات")
    st.info("تأكد من اتصال الإنترنت وأعد المحاولة")

st.markdown("---")
st.caption("تحليل فني | توقعات مونت كارلو | إدارة مخاطر")
