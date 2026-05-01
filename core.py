def create_chart(df, ticker, name, target=None, stop=None):
    """إنشاء رسم بياني متكامل"""
    if df is None or df.empty:
        return None
    
    last_price = df['Close'].iloc[-1]
    resistance = df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else last_price * 1.07
    support = df['Support'].iloc[-1] if not pd.isna(df['Support'].iloc[-1]) else last_price * 0.93
    
    target = target or resistance
    stop = stop or support
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=("السعر مع المتوسطات", "RSI", "MACD", "حجم التداول")
    )
    
    # الشموع اليابانية
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="السعر"
    ), row=1, col=1)
    
    # المتوسطات المتحركة
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20",
                             line=dict(color='#f59e0b', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50",
                             line=dict(color='#10b981', width=1.5)), row=1, col=1)
    
    # الهدف ووقف الخسارة
    if target > 0:
        fig.add_hline(y=target, line_dash="dash", line_color="#10b981",
                     annotation_text=f"🎯 الهدف: {target:.2f}", 
                     annotation_position="top right", row=1, col=1)
    if stop > 0:
        fig.add_hline(y=stop, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"🛑 وقف: {stop:.2f}",
                     annotation_position="bottom right", row=1, col=1)
    
    # Bollinger Bands
    if 'BBU_20_2.0' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], name="BB علوي",
                                 line=dict(color='#94a3b8', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], name="BB سفلي",
                                 line=dict(color='#94a3b8', dash='dash'),
                                 fill='tonexty', fillcolor='rgba(148,163,184,0.1)'), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                             line=dict(color='#8b5cf6', width=2)), row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    
    # MACD
    if 'MACD_12_26_9' in df.columns:
        macd_hist = df['MACD_12_26_9'] - df['MACDs_12_26_9']
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in macd_hist]
        
        fig.add_trace(go.Bar(x=df.index, y=macd_hist, name="Histogram",
                             marker_color=colors, opacity=0.7), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name="MACD",
                                 line=dict(color='#3b82f6', width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name="Signal",
                                 line=dict(color='#f59e0b', width=2)), row=3, col=1)
    
    # حجم التداول
    volume_colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
                     for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم",
                         marker_color=volume_colors, opacity=0.7), row=4, col=1)
    
    fig.update_layout(
        title=f"📊 التحليل الفني لسهم {name} ({ticker})",
        template="plotly_dark",
        height=700,
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="الحجم", row=4, col=1)
    
    return fig
