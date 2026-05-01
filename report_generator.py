# report_generator.py - نظام توليد التقارير المتقدمة
"""
توليد تقارير PDF و CSV ورسوم بيانية عن أداء المحفظة
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from config import REPORTS_DIR

def generate_risk_report(trades: List[Dict]) -> pd.DataFrame:
    """
    توليد تقرير المخاطر لكل صفقة
    يحتوي على نسبة المخاطرة/العائد ومستوى المخاطرة
    """
    risk_data = []
    for trade in trades:
        entry = trade['entry_price']
        target = trade['target_price']
        stop = trade['stop_loss']
        
        # حساب نسبة المخاطرة/العائد
        if entry > 0 and stop != entry:
            risk_reward = abs(target - entry) / abs(stop - entry)
        else:
            risk_reward = 0
        
        # تحديد مستوى المخاطرة
        if risk_reward >= 2:
            risk_level = "منخفضة 🟢"
            risk_color = "low"
        elif risk_reward >= 1.5:
            risk_level = "متوسطة 🟡"
            risk_color = "medium"
        else:
            risk_level = "عالية 🔴"
            risk_color = "high"
        
        # حساب الربح الحالي
        current_profit = trade.get('profit_pct', 0)
        
        risk_data.append({
            "السهم": trade['symbol'],
            "سعر الدخول": trade['entry_price'],
            "الهدف": trade['target_price'],
            "وقف الخسارة": trade['stop_loss'],
            "نسبة المخاطرة/العائد": f"1:{risk_reward:.1f}",
            "مستوى المخاطرة": risk_level,
            "الربح الحالي": f"{current_profit:+.1f}%",
            "الحالة": "🟢 نشط" if trade.get('status') == 'active' else "🔴 مغلق"
        })
    
    return pd.DataFrame(risk_data)

def generate_performance_chart(trades: List[Dict]) -> go.Figure:
    """
    توليد رسم بياني متقدم لأداء المحفظة
    """
    if not trades:
        return go.Figure()
    
    df = pd.DataFrame(trades)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("الربح لكل صفقة", "توزيع القطاعات", "نسبة النجاح", "أداء المحفظة")
    )
    
    # 1. الربح لكل صفقة (Bar Chart)
    fig.add_trace(go.Bar(
        x=df['symbol'], 
        y=df['profit_pct'],
        marker_color=['#00ff88' if x > 0 else '#ff4444' for x in df['profit_pct']],
        text=df['profit_pct'].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        name="الربح"
    ), row=1, col=1)
    
    # 2. توزيع القطاعات (Pie Chart)
    sector_counts = df.groupby('sector').size().reset_index(name='count')
    if not sector_counts.empty:
        fig.add_trace(go.Pie(
            labels=sector_counts['sector'],
            values=sector_counts['count'],
            hole=0.3,
            marker_colors=["#00ffcc", "#ff00ff", "#ffaa00", "#00ff88"],
            name="القطاعات"
        ), row=1, col=2)
    
    # 3. نسبة النجاح
    winning = len([t for t in trades if t.get('profit_pct', 0) > 0])
    losing = len(trades) - winning
    fig.add_trace(go.Pie(
        labels=["رابحة", "خاسرة"],
        values=[winning, losing],
        marker_colors=["#00ff88", "#ff4444"],
        hole=0.5,
        name="النجاح"
    ), row=2, col=1)
    
    # 4. أداء المحفظة
    if 'current_price' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['symbol'],
            y=df['current_price'],
            mode='lines+markers',
            line=dict(color='#00ffcc', width=2),
            marker=dict(size=8),
            name="السعر الحالي"
        ), row=2, col=2)
    
    fig.update_layout(
        template="plotly_dark",
        height=600,
        showlegend=True,
        title_text="تقرير أداء المحفظة - البورصجي AI"
    )
    
    return fig

def generate_summary_report(trades: List[Dict], stats: Dict) -> str:
    """
    توليد تقرير نصي ملخص للمحفظة
    """
    if not trades:
        return "لا توجد صفقات لعرض التقرير"
    
    winning = len([t for t in trades if t.get('profit_pct', 0) > 0])
    losing = len([t for t in trades if t.get('profit_pct', 0) < 0])
    breakeven = len([t for t in trades if t.get('profit_pct', 0) == 0])
    
    best_trade = max(trades, key=lambda x: x.get('profit_pct', 0)) if trades else None
    worst_trade = min(trades, key=lambda x: x.get('profit_pct', 0)) if trades else None
    
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           📊 تقرير البورصجي AI                               ║
║                        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  💰 إجمالي المستثمر: {stats['total_invested']:>40,.2f} ║
║  📈 القيمة الحالية: {stats['total_current']:>40,.2f} ║
║  📊 إجمالي الربح: {stats['total_profit']:>42,.2f} ║
║  📈 نسبة الربح: {stats['profit_pct']:>44.1f}% ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🏆 إجمالي الصفقات: {len(trades):>41} ║
║  ✅ الصفقات الرابحة: {winning:>39} ║
║  ❌ الصفقات الخاسرة: {losing:>39} ║
║  ⚖️ صفقات التعادل: {breakeven:>40} ║
║  📊 نسبة النجاح: {stats['win_rate']:>44.1f}% ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🏅 أفضل صفقة:                                                               ║
║     السهم: {best_trade['symbol'] if best_trade else 'لا يوجد'}                                                       ║
║     الربح: {best_trade.get('profit_pct', 0):+.1f}% if best_trade else '0'                                              ║
║                                                                              ║
║  📉 أسوأ صفقة:                                                               ║
║     السهم: {worst_trade['symbol'] if worst_trade else 'لا يوجد'}                                                       ║
║     الخسارة: {worst_trade.get('profit_pct', 0):+.1f}% if worst_trade else '0'                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    return report

def export_report_to_csv(trades: List[Dict], filename: str = None) -> str:
    """
    تصدير تقرير الصفقات إلى ملف CSV
    """
    if not filename:
        filename = f"boursagi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    df = pd.DataFrame(trades)
    filepath = REPORTS_DIR / filename
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return str(filepath)

def export_risk_report_to_csv(trades: List[Dict], filename: str = None) -> str:
    """
    تصدير تقرير المخاطر إلى ملف CSV
    """
    if not filename:
        filename = f"boursagi_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    risk_df = generate_risk_report(trades)
    filepath = REPORTS_DIR / filename
    risk_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return str(filepath)
