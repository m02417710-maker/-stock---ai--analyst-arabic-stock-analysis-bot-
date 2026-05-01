# في app.py، أضف هذا التبويب الجديد

from engines import ComparisonEngine

# ... داخل التبويبات ...

tab6 = st.tabs([...])[5]  # إضافة tab جديد

with tab6:
    st.subheader("🔍 مقارنة سهمين من نفس القطاع")
    
    st.markdown("""
    <div style="background: #1e293b; border-radius: 10px; padding: 15px; margin: 10px 0;">
        <p>⚡ مقارنة سهمين من نفس القطاع لتحديد أيهما يقدم فرصة استثمارية أفضل</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        stock1_options = [name for name in ALL_STOCKS.keys()]
        stock1_name = st.selectbox("السهم الأول", stock1_options, key="compare1")
        stock1_ticker = get_ticker(ALL_STOCKS[stock1_name]) if isinstance(ALL_STOCKS[stock1_name], dict) else ALL_STOCKS[stock1_name]
        sector1 = get_sector(ALL_STOCKS[stock1_name]) if isinstance(ALL_STOCKS[stock1_name], dict) else "غير محدد"
    
    with col2:
        # تصفية الأسهم من نفس القطاع
        similar_sector_stocks = [name for name, data in ALL_STOCKS.items() 
                                 if isinstance(data, dict) and data.get("sector") == sector1 and name != stock1_name]
        
        if not similar_sector_stocks:
            similar_sector_stocks = stock1_options
        
        stock2_name = st.selectbox("السهم الثاني", similar_sector_stocks, key="compare2")
        stock2_ticker = get_ticker(ALL_STOCKS[stock2_name]) if isinstance(ALL_STOCKS[stock2_name], dict) else ALL_STOCKS[stock2_name]
    
    if st.button("📊 مقارنة", use_container_width=True):
        with st.spinner("جاري تحليل السهمين..."):
            df1, _ = get_stock_data(stock1_ticker)
            df2, _ = get_stock_data(stock2_ticker)
            
            if df1 is not None and df2 is not None:
                comparison = ComparisonEngine.compare_stocks(df1, df2, stock1_name, stock2_name)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                            border: 2px solid {COLORS['primary']};
                            border-radius: 20px; padding: 20px;
                            text-align: center; margin: 15px 0;">
                    <h2 style="color: {COLORS['primary']};">🏆 السهم الأفضل: {comparison['winner']}</h2>
                    <p>{comparison['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{stock1_name}**")
                    st.metric("الدرجة الفنية", f"{comparison['score1']}/5")
                    st.metric("أداء 20 يوم", f"{comparison['perf1']:+.1f}%")
                    st.metric("التذبذب السنوي", f"{comparison['vol1']:.1f}%")
                
                with col2:
                    st.markdown(f"**{stock2_name}**")
                    st.metric("الدرجة الفنية", f"{comparison['score2']}/5")
                    st.metric("أداء 20 يوم", f"{comparison['perf2']:+.1f}%")
                    st.metric("التذبذب السنوي", f"{comparison['vol2']:.1f}%")
            else:
                st.error("فشل في جلب بيانات أحد السهمين")
