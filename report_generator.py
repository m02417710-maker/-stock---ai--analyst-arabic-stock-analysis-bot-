# report_generator.py - توليد التقارير المتقدمة
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
from config import REPORTS_DIR

def generate_performance_chart(history_df: pd.DataFrame) -> go.Figure:
    """توليد رسم بياني للأداء"""
    fig = make_subplots(rows=2, cols=1, subplot_titles=("الربح التراكمي", "نسبة النجاح"))
    
    # الربح التراكمي
    fig.add_trace(go.Scatter(
        x=history_df['date'], y=history_df['total_profit'],
        mode='lines+markers',
        name='الربح التراكمي',
        line=dict(color='#00ffcc', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 204, 0.1)'
    ), row=1, col=1)
    
    # نسبة النجاح
    fig.add_trace(go.Bar(
        x=history_df['date'], y=history_df['win_rate'],
        name='نسبة النجاح',
        marker_color='#00ff88'
    ), row=2, col=1)
    
    fig.update_layout(
        template="plotly_dark",
        height=500,
        title="تقرير أداء المحفظة",
        showlegend=True
    )
    
    return fig

def generate_risk_report(trades: list) -> pd.DataFrame:
    """توليد تقرير المخاطر"""
    risk_data = []
    for trade in trades:
        risk_reward = abs(trade['target_price'] - trade['entry_price']) / abs(trade['stop_loss'] - trade['entry_price']) if trade['stop_loss'] != trade['entry_price'] else 0
        
        if risk_reward >= 2:
            risk_level = "منخفضة 🟢"
        elif risk_reward >= 1.5:
            risk_level = "متوسطة 🟡"
        else:
            risk_level = "عالية 🔴"
        
        risk_data.append({
            "السهم": trade['symbol'],
            "سعر الدخول": trade['entry_price'],
            "الهدف": trade['target_price'],
            "وقف الخسارة": trade['stop_loss'],
            "نسبة المخاطرة/العائد": f"1:{risk_reward:.1f}",
            "مستوى المخاطرة": risk_level,
            "Trailing Stop": f"{trade.get('trailing_stop', 0)}%" if trade.get('trailing_stop', 0) > 0 else "-"
        })
    
    return pd.DataFrame(risk_data)

def export_report_to_csv(trades: list, filename: str = None):
    """تصدير التقرير إلى CSV"""
    if not filename:
        filename = f"boursagi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    df = pd.DataFrame(trades)
    filepath = REPORTS_DIR / filename
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return filepath

def generate_summary_report(trades: list, stats: dict) -> str:
    """توليد تقرير نصي ملخص"""
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 تقرير البورصجي AI                      ║
║                      {datetime.now().strftime('%Y-%m-%d %H:%M')}                    ║
╠══════════════════════════════════════════════════════════════╣
║  💰 إجمالي المستثمر: {stats['total_invested']:>30,.2f} ║
║  📈 القيمة الحالية: {stats['total_current']:>30,.2f} ║
║  📊 إجمالي الربح: {stats['total_profit']:>32,.2f} ║
║  📈 نسبة الربح: {stats['profit_pct']:>34.1f}% ║
╠══════════════════════════════════════════════════════════════╣
║  🏆 عدد الصفقات: {len(trades):>33} ║
║  ✅ الصفقات الرابحة: {stats.get('winning_trades', 0):>29} ║
║  📊 نسبة النجاح: {stats.get('win_rate', 0):>33.1f}% ║
╚══════════════════════════════════════════════════════════════╝
"""
    return report
