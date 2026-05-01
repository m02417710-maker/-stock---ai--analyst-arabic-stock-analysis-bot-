def create_chart(df, ticker, name, target=None, stop=None):
    """إنشاء رسم بياني متكامل - نسخة مصححة ومستقرة"""
    if df is None or df.empty:
        return None
    
    # تأمين البيانات: حذف أول صفوف قد تحتوي على NaN بسبب حساب المؤشرات
    plot_df = df.tail(100).copy() # رسم آخر 100 يوم فقط لضمان سرعة الواجهة ودقة المؤشرات
    
    last_price = plot_df['Close'].iloc[-1]
    
    # التأكد من وجود أعمدة الدعم والمقاومة أو وضع قيم افتراضية
    resistance = plot_df['Resistance'].iloc[-1] if 'Resistance' in plot_df.columns and not pd.isna(plot_df['Resistance'].iloc[-1]) else last_price * 1.07
    support = plot_df['Support'].iloc[-1] if 'Support' in plot_df.columns and not pd.isna(plot_df['Support'].iloc[-1]) else last_price * 0.93
    
    target = target if target and target > 0 else resistance
    stop = stop if stop and stop > 0 else support
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=("📈 السعر مع المتوسطات", "📊 RSI", "🔍 MACD", "💰 حجم التداول")
    )
    
    # 1. الشموع اليابانية
    fig.add_trace(go.Candlestick(
        x=plot_df.index, open=plot_df['Open'], high=plot_df['High'],
        low=plot_df['Low'], close=plot_df['Close'], name="السعر"
    ), row=1, col=1)
    
    # 2. المتوسطات المتحركة
    if 'MA20' in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df['MA20'], name="MA20",
                                 line=dict(color='#f59e0b', width=1.5)), row=1, col=1)
    if 'MA50' in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df['MA50'], name="MA50",
                                 line=dict(color='#10b981', width=1.5)), row=1, col=1)
    
    # 3. خطوط الهدف ووقف الخسارة
    fig.add_hline(y=target, line_dash="dash", line_color="#10b981",
                 annotation_text=f"🎯 الهدف: {target:.2f}", 
                 annotation_position="top right", row=1, col=1)
    fig.add_hline(y=stop, line_dash="dash", line_color="#ef4444",
                 annotation_text=f"🛑 وقف: {stop:.2f}",
                 annotation_position="bottom right", row=1, col=1)
    
    # 4. RSI (مع تثبيت المدى ليكون منطقياً 0-100)
    if 'RSI' in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df['RSI'], name="RSI",
                                 line=dict(color='#8b5cf6', width=2)), row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.15, row=2, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.15, row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    
    # 5. MACD (مع التأكد من وجود الأعمدة)
    macd_col = 'MACD_12_26_9'
    signal_col = 'MACDs_12_26_9'
    if macd_col in plot_df.columns and signal_col in plot_df.columns:
        macd_hist = plot_df[macd_col] - plot_df[signal_col]
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in macd_hist]
        
        fig.add_trace(go.Bar(x=plot_df.index, y=macd_hist, name="Histogram",
                             marker_color=colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df[macd_col], name="MACD",
                                 line=dict(color='#3b82f6')), row=3, col=1)
        fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df[signal_col], name="Signal",
                                 line=dict(color='#f59e0b')), row=3, col=1)
    
    # 6. حجم التداول
    vol_colors = ['#ef4444' if plot_df['Close'].iloc[i] < plot_df['Open'].iloc[i] else '#10b981' 
                  for i in range(len(plot_df))]
    fig.add_trace(go.Bar(x=plot_df.index, y=plot_df['Volume'], name="الحجم",
                         marker_color=vol_colors), row=4, col=1)
    
    # الإعدادات العامة للشكل
    fig.update_layout(
        title=dict(text=f"📊 التحليل الفني لـ {name} ({ticker})", font=dict(size=20)),
        template="plotly_dark",
        height=800,
        margin=dict(l=10, r=10, t=80, b=10),
        showlegend=False, # إخفاء الـ Legend لجعل الشكل أنظف على الموبايل
        xaxis_rangeslider_visible=False # إخفاء المنزلق لتوفير مساحة
    )
    
    return fig
