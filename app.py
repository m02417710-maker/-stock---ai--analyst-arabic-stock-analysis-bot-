# ============================================================
# app.py - الواجهة الرئيسية للنظام
# الإصدار: 4.0 - النهائي
# ============================================================

import streamlit as st
from datetime import datetime
from core import (
    get_data, analyze, monte_carlo_gbm, create_chart, 
    risk_management, scan_market_parallel, STOCKS
)
from strings import UI_TEXT

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
# التصميم (CSS)
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
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
    capital = st.number_input(
        UI_TEXT["sidebar_capital_label"], 
        min_value=100, 
        value=10000, 
        step=1000
    )
    risk_percent = st.slider(
        UI_TEXT["sidebar_risk_label"], 
        0.5, 5.0, 2.0, 0.5
    )
    
    st.markdown("---")
    
    selected_name = st.selectbox(
        "🔍 اختر السهم", 
        list(STOCKS.keys())
    )
    ticker = STOCKS[selected_name]
    
    st.caption(f"📌 الرمز: `{ticker}`")
    st.markdown("---")
    
    st.markdown("### 📊 معلومات")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    st.caption(f"🔄 {UI_TEXT['sidebar_refresh']}")
    st.caption(f"📈 {UI_TEXT['sidebar_stocks_count']}: {len(STOCKS)}")
    
    if st.button(UI_TEXT["sidebar_update_btn"], use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# العنوان الرئيسي وجلب البيانات
# ============================================================

st.markdown(f"## {UI_TEXT['page_title'].format(selected=selected_name)}")
st.markdown("---")

with st.spinner("🔄 جاري تحليل البيانات..."):
    df, info = get_data(ticker)

if df is not None and not df.empty:
    # ============================================================
    # التحليل الأساسي
    # ============================================================
    
    score, signals, recommendation, rec_color = analyze(df)
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
    change = ((current_price - prev_price) / prev_price) * 100
    
    # مونت كارلو
    with st.spinner("🔮 تشغيل محاكاة مونت كارلو..."):
        mc = monte_carlo_gbm(df)
    
    # إدارة المخاطر
    shares, position, actual_risk, risk_advice = risk_management(
        capital, current_price, 5, risk_percent
    )
    
    # الأهداف
    target_price = df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else current_price * 1.07
    stop_price = current_price * 0.95
    
    # ============================================================
    # بطاقات المؤشرات
    # ============================================================
    
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
    
    # ============================================================
    # بطاقة التوصية
    # ============================================================
    
    if score >= 4:
        st.markdown(f"""
        <div class="golden-signal">
            <h1 style="color: #10b981; margin: 0;">✨ إشارة ذهبية ✨</h1>
            <h2 style="color: #10b981;">{recommendation}</h2>
            <p style="color: #d1d5db;">
                🎯 هدف: {target_price:.2f} | 🛑 وقف: {stop_price:.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 2px solid {rec_color};
                    border-radius: 20px; padding: 20px;
                    text-align: center; margin: 15px 0;">
            <h2 style="color: {rec_color};">{recommendation}</h2>
            <p>🎯 هدف: {target_price:.2f} | 🛑 وقف: {stop_price:.2f}</p>
            <p style="font-size: 12px;">{risk_advice}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================
    # التبويبات
    # ============================================================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        UI_TEXT["tab_chart"], 
        UI_TEXT["tab_analysis"], 
        UI_TEXT["tab_forecast"],
        UI_TEXT["tab_risk"], 
        UI_TEXT["tab_scanner"]
    ])
    
    with tab1:
        fig = create_chart(df, ticker, selected_name, target_price, stop_price)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown(f"### {UI_TEXT['analysis_signals_title']}")
        for signal in signals:
            if any(kw in signal for kw in ["✅", "🔥", "💰", "🚀"]):
                st.success(signal)
            elif "⚠️" in signal:
                st.warning(signal)
            else:
                st.info(signal)
        
        st.markdown("---")
        st.markdown(f"### {UI_TEXT['analysis_points_title']}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{UI_TEXT['analysis_entry']}:** {current_price:.2f}")
            st.markdown(f"**{UI_TEXT['analysis_target1']}:** {target_price:.2f}")
            st.markdown(f"**{UI_TEXT['analysis_target2']}:** {current_price * 1.08:.2f}")
        with col_b:
            st.markdown(f"**{UI_TEXT['analysis_target3']}:** {current_price * 1.10:.2f}")
            st.markdown(f"**{UI_TEXT['analysis_stop']}:** {stop_price:.2f}")
            if stop_price != current_price:
                ratio = (current_price * 1.07 - current_price) / (current_price - stop_price)
                st.markdown(f"**{UI_TEXT['analysis_risk_reward']}:** 1:{ratio:.1f}")
    
    with tab3:
        if mc:
            st.markdown(f"### {UI_TEXT['forecast_title']}")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.metric(UI_TEXT['forecast_expected'], f"{mc['expected']:.2f}")
                st.metric(UI_TEXT['forecast_median'], f"{mc['median']:.2f}")
                st.metric(UI_TEXT['forecast_best'], f"{mc['best_95']:.2f}")
            with col_f2:
                st.metric(UI_TEXT['forecast_worst'], f"{mc['worst_5']:.2f}")
                st.metric(UI_TEXT['forecast_profit'], f"{mc['profit_prob']:.1f}%")
                st.metric(UI_TEXT['forecast_target'], f"{mc['target_10_prob']:.1f}%")
            
            st.markdown("---")
            if mc['profit_prob'] > 60:
                assessment = UI_TEXT['forecast_good']
                st.success(UI_TEXT['forecast_analysis_profit'].format(
                    prob=mc['profit_prob'], assessment=assessment
                ))
            elif mc['profit_prob'] > 45:
                assessment = UI_TEXT['forecast_average']
                st.warning(UI_TEXT['forecast_analysis_profit'].format(
                    prob=mc['profit_prob'], assessment=assessment
                ))
            else:
                assessment = UI_TEXT['forecast_caution']
                st.error(UI_TEXT['forecast_analysis_profit'].format(
                    prob=mc['profit_prob'], assessment=assessment
                ))
        else:
            st.warning("بيانات غير كافية لتشغيل محاكاة مونت كارلو")
    
    with tab4:
        st.markdown(f"### {UI_TEXT['risk_title']}")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric(UI_TEXT['risk_capital'], f"${capital:,.2f}")
            st.metric(UI_TEXT['risk_allowed'], f"{risk_percent}%")
        with col_r2:
            st.metric(UI_TEXT['risk_shares'], f"{shares:,}")
            st.metric(UI_TEXT['risk_position'], f"${position:,.2f}")
        with col_r3:
            st.metric(UI_TEXT['risk_actual'], f"{actual_risk}%")
            st.metric(UI_TEXT['risk_total'], f"{(position/capital)*100:.1f}%")
        
        st.markdown("---")
        st.markdown(f"### {UI_TEXT['risk_recommendations']}")
        
        if shares == 0:
            st.warning(UI_TEXT['risk_warning_invalid'])
        elif actual_risk > risk_percent:
            st.error(UI_TEXT['risk_warning_exceed'].format(
                actual=actual_risk, allowed=risk_percent
            ))
        else:
            st.success(risk_advice)
        
        st.markdown("---")
        st.markdown(f"### {UI_TEXT['risk_principles_title']}")
        for i in range(1, 5):
            st.markdown(f"- {UI_TEXT[f'risk_principle_{i}']}")
    
    with tab5:
        st.markdown(f"### {UI_TEXT['scanner_title']}")
        
        if st.button(UI_TEXT["scanner_button"], use_container_width=True):
            with st.spinner("🔄 جاري مسح جميع الأسهم بالتوازي..."):
                results = scan_market_parallel()
                if not results.empty:
                    st.success(UI_TEXT['scanner_success'].format(count=len(results)))
                    st.dataframe(results, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.markdown(f"### {UI_TEXT['scanner_top_title']}")
                    top5 = results.head(5)
                    for _, row in top5.iterrows():
                        if "شراء" in row['التوصية']:
                            st.success(f"📈 **{row['السهم']}** - {row['التوصية']} | السعر: {row['السعر']} | RSI: {row['RSI']}")
                        else:
                            st.info(f"📊 **{row['السهم']}** - {row['التوصية']} | السعر: {row['السعر']}")
                else:
                    st.warning(UI_TEXT['scanner_no_data'])

else:
    st.error(UI_TEXT["error_fetch"])
    st.info(UI_TEXT["error_solutions"])

# ============================================================
# تذييل الصفحة
# ============================================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    🚀 {UI_TEXT['footer']}<br>
    🔄 تحديث تلقائي كل 5 دقائق | 📈 جميع البورصات
</div>
""", unsafe_allow_html=True)
