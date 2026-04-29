"""
📈 محلل الأسهم المصري المتكامل مع قاعدة بيانات
Egyptian Stock Analyst - Complete System
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas_ta as ta
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path
import json

# ============================================
# إعداد الصفحة
# ============================================
st.set_page_config(
    page_title="محلل الأسهم المصري - نظام متكامل 📈",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# تهيئة قاعدة البيانات
# ============================================

def init_database():
    """تهيئة قاعدة البيانات SQLite"""
    db_path = Path("data/stock_analyst.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # إنشاء الجداول
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            settings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorite_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT NOT NULL,
            shares REAL NOT NULL,
            avg_price REAL NOT NULL,
            bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT NOT NULL,
            type TEXT NOT NULL,
            shares REAL NOT NULL,
            price REAL NOT NULL,
            total_value REAL NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            condition TEXT NOT NULL,
            target_value REAL NOT NULL,
            is_active INTEGER DEFAULT 1,
            triggered INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            recommendation TEXT,
            confidence REAL,
            analysis_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # إضافة مستخدم افتراضي
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username, email, settings) VALUES (1, 'admin', 'admin@example.com', '{}')")
    conn.commit()
    conn.close()
    
    return str(db_path)

# ============================================
# دوال قاعدة البيانات
# ============================================

def get_db_connection():
    """الحصول على اتصال قاعدة البيانات"""
    db_path = Path("data/stock_analyst.db")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def add_favorite_stock(user_id: int, ticker: str):
    """إضافة سهم للمفضلة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO favorite_stocks (user_id, ticker) VALUES (?, ?)",
        (user_id, ticker)
    )
    conn.commit()
    conn.close()

def remove_favorite_stock(user_id: int, ticker: str):
    """حذف سهم من المفضلة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favorite_stocks WHERE user_id = ? AND ticker = ?",
        (user_id, ticker)
    )
    conn.commit()
    conn.close()

def get_favorite_stocks(user_id: int) -> List[str]:
    """الحصول على قائمة الأسهم المفضلة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker FROM favorite_stocks WHERE user_id = ?",
        (user_id,)
    )
    stocks = [row['ticker'] for row in cursor.fetchall()]
    conn.close()
    return stocks

def add_transaction(user_id: int, ticker: str, trans_type: str, shares: float, price: float):
    """إضافة معاملة جديدة"""
    total_value = shares * price
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transactions (user_id, ticker, type, shares, price, total_value)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, ticker, trans_type, shares, price, total_value))
    
    # تحديث المحفظة
    if trans_type == "BUY":
        cursor.execute('''
            INSERT OR REPLACE INTO portfolio (user_id, ticker, shares, avg_price)
            VALUES (?, ?, COALESCE((SELECT shares FROM portfolio WHERE user_id = ? AND ticker = ?), 0) + ?,
                    (COALESCE((SELECT avg_price FROM portfolio WHERE user_id = ? AND ticker = ?), 0) * 
                     COALESCE((SELECT shares FROM portfolio WHERE user_id = ? AND ticker = ?), 0) + ? * ?) /
                    (COALESCE((SELECT shares FROM portfolio WHERE user_id = ? AND ticker = ?), 0) + ?))
        ''', (user_id, ticker, user_id, ticker, shares,
              user_id, ticker, user_id, ticker, price, shares,
              user_id, ticker, shares))
    else:
        cursor.execute('''
            UPDATE portfolio 
            SET shares = shares - ?
            WHERE user_id = ? AND ticker = ? AND shares >= ?
        ''', (shares, user_id, ticker, shares))
        
        # حذف إذا أصبحت الصفر
        cursor.execute('DELETE FROM portfolio WHERE user_id = ? AND ticker = ? AND shares <= 0', 
                      (user_id, ticker))
    
    conn.commit()
    conn.close()

def get_portfolio(user_id: int) -> List[Dict]:
    """الحصول على محفظة المستخدم"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker, shares, avg_price FROM portfolio WHERE user_id = ?",
        (user_id,)
    )
    portfolio = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return portfolio

def add_alert(user_id: int, ticker: str, alert_type: str, condition: str, target_value: float):
    """إضافة تنبيه جديد"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (user_id, ticker, alert_type, condition, target_value)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, ticker, alert_type, condition, target_value))
    conn.commit()
    conn.close()

def get_active_alerts(user_id: int) -> List[Dict]:
    """الحصول على التنبيهات النشطة"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM alerts 
        WHERE user_id = ? AND is_active = 1 AND triggered = 0
    ''', (user_id,))
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alerts

# ============================================
# قائمة الأسهم المصرية
# ============================================

EGYPTIAN_STOCKS = {
    "COMI.CA": "البنك التجاري الدولي (CIB)",
    "TMGH.CA": "طلعت مصطفى القابضة",
    "SWDY.CA": "السويدي إليكتريك",
    "ETEL.CA": "تليكوم مصر",
    "EGAL.CA": "مصر للألومنيوم",
    "EAST.CA": "الشرقية للدخان",
    "MFPC.CA": "مصر لإنتاج الأسمدة (موبكو)",
    "ORAS.CA": "أوراسكوم للإنشاءات",
    "JUFO.CA": "جي بي أوتو",
    "ABUK.CA": "أبو قير للأسمدة",
    "HRHO.CA": "البنك الهولندي",
    "SUGR.CA": "سكر الحدود",
    "SKPC.CA": "سيدبك",
    "PHDC.CA": "بالم هيلز للتعمير",
}

# ============================================
# دوال التحليل الفني
# ============================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(ticker: str, period: str = "6mo") -> Optional[pd.DataFrame]:
    """جلب بيانات السهم من Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None
        
        # تنظيف البيانات
        df = df.dropna()
        
        # إضافة المؤشرات الفنية
        if len(df) >= 20:
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            df['SMA_50'] = ta.sma(df['Close'], length=50) if len(df) >= 50 else df['SMA_20']
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['Volume_SMA'] = ta.sma(df['Volume'], length=20)
            
            # MACD
            macd = ta.macd(df['Close'])
            if macd is not None:
                df['MACD'] = macd['MACD_12_26_9']
                df['MACD_Signal'] = macd['MACDs_12_26_9']
        
        return df
    except Exception as e:
        st.error(f"خطأ في جلب بيانات {ticker}: {str(e)}")
        return None

def analyze_stock(df: pd.DataFrame, ticker: str) -> Dict:
    """تحليل السهم وإعطاء توصيات"""
    if df is None or df.empty:
        return {'signal': 'error', 'message': 'لا توجد بيانات كافية'}
    
    last_price = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
    sma_20 = df['SMA_20'].iloc[-1] if 'SMA_20' in df.columns else last_price
    
    # تحليل RSI
    if last_rsi > 70:
        rsi_signal = "ذروة شراء - خطر"
        rsi_color = "red"
    elif last_rsi < 30:
        rsi_signal = "ذروة بيع - فرصة"
        rsi_color = "green"
    else:
        rsi_signal = "منطقة محايدة"
        rsi_color = "yellow"
    
    # تحليل المتوسطات
    if last_price > sma_20:
        ma_signal = "اتجاه صاعد"
        ma_color = "green"
    else:
        ma_signal = "اتجاه هابط"
        ma_color = "red"
    
    # التوصية النهائية
    if last_rsi < 30 and last_price > sma_20:
        recommendation = "🟢 شراء"
        confidence = "مرتفعة"
    elif last_rsi > 70 and last_price < sma_20:
        recommendation = "🔴 بيع"
        confidence = "مرتفعة"
    elif last_rsi < 40:
        recommendation = "🟡 تراكم"
        confidence = "متوسطة"
    elif last_rsi > 60:
        recommendation = "🟠 تصريف"
        confidence = "متوسطة"
    else:
        recommendation = "⚪ انتظار"
        confidence = "منخفضة"
    
    return {
        'signal': recommendation,
        'confidence': confidence,
        'rsi': last_rsi,
        'rsi_signal': rsi_signal,
        'rsi_color': rsi_color,
        'ma_signal': ma_signal,
        'ma_color': ma_color,
        'current_price': last_price,
        'sma_20': sma_20
    }

def create_advanced_chart(df: pd.DataFrame, ticker: str):
    """إنشاء رسم بياني متقدم"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=(f"📈 سعر {ticker}", "📊 RSI", "📉 حجم التداول")
    )
    
    # السعر والمتوسطات
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        name="سعر الإغلاق",
        line=dict(color='#00ff87', width=2)
    ), row=1, col=1)
    
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_20'],
            name="SMA 20",
            line=dict(color='orange', width=1.5, dash='dash')
        ), row=1, col=1)
    
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_50'],
            name="SMA 50",
            line=dict(color='purple', width=1.5, dash='dot')
        ), row=1, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'],
            name="RSI",
            line=dict(color='#ff006e', width=2)
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)
    
    # حجم التداول
    colors = ['#00ff87' if close >= open else '#ff006e' 
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        name="حجم التداول",
        marker_color=colors,
        opacity=0.7
    ), row=3, col=1)
    
    fig.update_layout(
        height=700,
        template="plotly_dark",
        showlegend=True,
        title_text=f"تحليل سهم {ticker}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(title_text="التاريخ", row=3, col=1)
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="الكمية", row=3, col=1)
    
    return fig

# ============================================
# تهيئة الجلسة
# ============================================

def init_session():
    """تهيئة جلسة المستخدم"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True

# ============================================
# الواجهة الجانبية
# ============================================

def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Egyptian_Exchange_logo.png/200px-Egyptian_Exchange_logo.png",
                 use_container_width=True)
        
        st.markdown("# 🏦 بورصة مصر")
        st.markdown("---")
        
        # وضع العرض
        st.session_state.dark_mode = st.toggle("🌙 الوضع المظلم", value=st.session_state.dark_mode)
        
        st.markdown("---")
        
        # إحصائيات سريعة
        st.markdown("### 📊 إحصائيات")
        
        favorites = get_favorite_stocks(st.session_state.user_id)
        st.metric("⭐ الأسهم المفضلة", len(favorites))
        
        portfolio = get_portfolio(st.session_state.user_id)
        portfolio_value = sum(h['shares'] * h['avg_price'] for h in portfolio)
        st.metric("💰 قيمة المحفظة", f"{portfolio_value:,.2f} ج.م")
        
        alerts = get_active_alerts(st.session_state.user_id)
        st.metric("🔔 التنبيهات", len(alerts))
        
        st.markdown("---")
        
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.caption("📊 نظام متكامل لتحليل الأسهم")
        st.caption("⚠️ للأغراض التعليمية فقط")

# ============================================
# التطبيق الرئيسي
# ============================================

def main():
    """تشغيل التطبيق الرئيسي"""
    
    # تهيئة الجلسة
    init_session()
    
    # عرض الشريط الجانبي
    render_sidebar()
    
    # المحتوى الرئيسي
    st.title("📈 محلل الأسهم المصري المتكامل")
    st.markdown(f"🕒 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")
    
    # تبويبات التطبيق
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 تحليل الأسهم",
        "⭐ الأسهم المفضلة",
        "💰 المحفظة",
        "🔔 التنبيهات"
    ])
    
    # ============= التبويب 1: تحليل الأسهم =============
    with tab1:
        st.header("🔍 تحليل الأسهم")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_ticker = st.selectbox(
                "اختر السهم",
                options=list(EGYPTIAN_STOCKS.keys()),
                format_func=lambda x: f"{x} - {EGYPTIAN_STOCKS[x]}"
            )
        
        with col2:
            period = st.selectbox(
                "الفترة الزمنية",
                ["1mo", "3mo", "6mo", "1y"],
                index=2
            )
        
        # أزرار الإجراءات
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⭐ إضافة للمفضلة", use_container_width=True):
                add_favorite_stock(st.session_state.user_id, selected_ticker)
                st.success(f"تم إضافة {selected_ticker} إلى المفضلة")
                st.rerun()
        
        # جلب البيانات وتحليلها
        with st.spinner("جاري تحليل السهم..."):
            df = fetch_stock_data(selected_ticker, period)
            
            if df is not None and not df.empty:
                analysis = analyze_stock(df, selected_ticker)
                
                # عرض المؤشرات
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💰 السعر الحالي", f"{analysis['current_price']:.2f} ج.م")
                with col2:
                    st.metric("📊 RSI", f"{analysis['rsi']:.1f}", 
                             delta=analysis['rsi_signal'],
                             delta_color="inverse" if analysis['rsi'] > 70 else "normal")
                with col3:
                    st.metric("📈 المتوسط 20", f"{analysis['sma_20']:.2f}")
                with col4:
                    st.metric("🎯 التوصية", analysis['signal'])
                
                # الرسم البياني
                chart = create_advanced_chart(df, selected_ticker)
                st.plotly_chart(chart, use_container_width=True)
                
                # نقاط الدعم والمقاومة
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📈 نقاط المقاومة")
                    recent_highs = df['High'].tail(50).nlargest(3)
                    for i, price in enumerate(recent_highs, 1):
                        st.write(f"**R{i}:** {price:.2f} ج.م")
                
                with col2:
                    st.subheader("📉 نقاط الدعم")
                    recent_lows = df['Low'].tail(50).nsmallest(3)
                    for i, price in enumerate(recent_lows, 1):
                        st.write(f"**S{i}:** {price:.2f} ج.م")
                
                # تنبيه RSI
                if analysis['rsi'] > 70:
                    st.warning(f"⚠️ تنبيه: السهم في منطقة ذروة شراء (RSI: {analysis['rsi']:.1f})")
                elif analysis['rsi'] < 30:
                    st.success(f"✅ تنبيه: السهم في منطقة ذروة بيع (RSI: {analysis['rsi']:.1f})")
                
            else:
                st.error("❌ لا يمكن جلب البيانات. يرجى المحاولة مرة أخرى")
    
    # ============= التبويب 2: الأسهم المفضلة =============
    with tab2:
        st.header("⭐ الأسهم المفضلة")
        
        favorites = get_favorite_stocks(st.session_state.user_id)
        
        if favorites:
            for ticker in favorites:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{ticker}** - {EGYPTIAN_STOCKS.get(ticker, '')}")
                    with col2:
                        if st.button("📊 تحليل", key=f"analyze_{ticker}"):
                            st.session_state.selected_ticker = ticker
                    with col3:
                        if st.button("🗑️ حذف", key=f"delete_{ticker}"):
                            remove_favorite_stock(st.session_state.user_id, ticker)
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("لا توجد أسهم مفضلة. أضف من تبويب تحليل الأسهم")
    
    # ============= التبويب 3: المحفظة =============
    with tab3:
        st.header("💰 إدارة المحفظة")
        
        # نموذج إضافة صفقة
        with st.expander("➕ إضافة صفقة جديدة", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                ticker = st.selectbox("السهم", list(EGYPTIAN_STOCKS.keys()), key="portfolio_ticker")
            with col2:
                shares = st.number_input("عدد الأسهم", min_value=1.0, step=1.0, key="shares")
            with col3:
                price = st.number_input("سعر الشراء", min_value=0.01, step=0.01, key="price")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ شراء", use_container_width=True):
                    add_transaction(st.session_state.user_id, ticker, "BUY", shares, price)
                    st.success(f"تم شراء {shares} سهم من {ticker}")
                    st.rerun()
        
        # عرض المحفظة
        portfolio = get_portfolio(st.session_state.user_id)
        
        if portfolio:
            st.subheader("📋 الحيازات الحالية")
            
            portfolio_data = []
            total_value = 0
            
            for holding in portfolio:
                current_price = fetch_stock_data(holding['ticker'], "1d")
                current_value = holding['shares'] * (current_price['Close'].iloc[-1] if current_price is not None else holding['avg_price'])
                total_value += current_value
                
                portfolio_data.append({
                    "السهم": holding['ticker'],
                    "عدد الأسهم": holding['shares'],
                    "متوسط السعر": holding['avg_price'],
                    "القيمة الحالية": current_value
                })
            
            st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True, hide_index=True)
            st.metric("💰 إجمالي قيمة المحفظة", f"{total_value:,.2f} ج.م")
        else:
            st.info("لا توجد أسهم في المحفظة")
    
    # ============= التبويب 4: التنبيهات =============
    with tab4:
        st.header("🔔 إدارة التنبيهات")
        
        # نموذج إضافة تنبيه
        with st.expander("➕ إضافة تنبيه جديد", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                alert_ticker = st.selectbox("السهم", list(EGYPTIAN_STOCKS.keys()), key="alert_ticker")
            with col2:
                alert_type = st.selectbox("نوع التنبيه", ["price", "rsi"])
            with col3:
                condition = st.selectbox("الشرط", ["above", "below"])
            
            target_value = st.number_input("القيمة المستهدفة", min_value=0.01, step=0.01, key="target")
            
            if st.button("✅ إنشاء تنبيه", use_container_width=True):
                add_alert(st.session_state.user_id, alert_ticker, alert_type, condition, target_value)
                st.success("تم إنشاء التنبيه بنجاح")
                st.rerun()
        
        # عرض التنبيهات الحالية
        alerts = get_active_alerts(st.session_state.user_id)
        
        if alerts:
            st.subheader("📋 التنبيهات النشطة")
            for alert in alerts:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{alert['ticker']}**")
                with col2:
                    st.write(alert['alert_type'])
                with col3:
                    st.write(f"{alert['condition']} {alert['target_value']}")
                with col4:
                    if st.button("🗑️", key=f"del_alert_{alert['id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE alerts SET is_active = 0 WHERE id = ?", (alert['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
                st.markdown("---")
        else:
            st.info("لا توجد تنبيهات نشطة")

# ============================================
# تشغيل التطبيق
# ============================================

if __name__ == "__main__":
    main()
