"""
📈 محلل الأسهم المصري المتكامل مع قاعدة بيانات
Egyptian Stock Analyst - Complete System
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy.orm import Session

# إعداد الصفحة
st.set_page_config(
    page_title="محلل الأسهم المصري - نظام متكامل 📈",
    page_icon="🇪🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استيراد الملفات المحلية
from database.connection import init_db, get_db, backup_database
from database.crud import *
#from utils.indicators import calculate_indicators
from utils.telegram_bot import TelegramNotifier
from utils.notifications import NotificationManager

# ============= التهيئة =============
def init_session():
    """تهيئة جلسة المستخدم"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1  # مستخدم افتراضي
    if 'db_initialized' not in st.session_state:
        init_db()
        st.session_state.db_initialized = True
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

# ============= الواجهة الجانبية =============
def render_sidebar():
    """عرض الشريط الجانبي"""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Egyptian_Exchange_logo.png/200px-Egyptian_Exchange_logo.png", 
                 use_container_width=True)
        
        st.markdown("# 🏦 بورصة مصر")
        st.markdown("---")
        
        # معلومات المستخدم
        db = next(get_db())
        user = get_user(db, st.session_state.user_id)
        if user:
            st.markdown(f"### 👤 مرحباً {user.username}")
        
        st.markdown("---")
        
        # إحصائيات سريعة
        st.markdown("### 📊 إحصائيات")
        
        # عدد الأسهم المفضلة
        favorites = get_favorite_stocks(db, st.session_state.user_id)
        st.metric("⭐ الأسهم المفضلة", len(favorites))
        
        # قيمة المحفظة
        portfolio_summary = get_portfolio_summary(db, st.session_state.user_id)
        st.metric("💰 قيمة المحفظة", f"{portfolio_summary['total_value']:,.2f} ج.م")
        
        # عدد التنبيهات
        alerts = get_active_alerts(db, st.session_state.user_id)
        st.metric("🔔 التنبيهات النشطة", len(alerts))
        
        st.markdown("---")
        
        # أزرار سريعة
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("💾 نسخ احتياطي", use_container_width=True):
            backup_path = backup_database()
            if backup_path:
                st.success(f"تم إنشاء نسخة احتياطية")
        
        st.markdown("---")
        st.caption("📊 نظام متكامل لتحليل الأسهم")
        st.caption("⚠️ للأغراض التعليمية فقط")

# ============= الصفحة الرئيسية =============
def main():
    """تشغيل التطبيق الرئيسي"""
    
    # تهيئة الجلسة
    init_session()
    
    # قائمة الأسهم المصرية
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
    }
    
    # عرض الشريط الجانبي
    render_sidebar()
    
    # المحتوى الرئيسي
    st.title("📈 محلل الأسهم المصري المتكامل")
    st.markdown(f"🕒 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")
    
    # تبويبات التطبيق
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 تحليل الأسهم",
        "⭐ الأسهم المفضلة",
        "💰 المحفظة",
        "🔔 التنبيهات",
        "📊 التقارير"
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
        
        # زر إضافة للمفضلة
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⭐ إضافة للمفضلة", use_container_width=True):
                db = next(get_db())
                add_favorite_stock(db, st.session_state.user_id, selected_ticker)
                st.success(f"تم إضافة {selected_ticker} إلى المفضلة")
                st.rerun()
        
        # عرض التحليل
        with st.spinner("جاري تحليل السهم..."):
            # استيراد دوال التحليل
            from utils.indicators import fetch_stock_data, analyze_stock, create_advanced_chart
            
            # جلب البيانات
            df = fetch_stock_data(selected_ticker, period)
            
            if df is not None and not df.empty:
                # تحليل السهم
                analysis = analyze_stock(df, selected_ticker)
                
                # عرض المؤشرات
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💰 السعر", f"{analysis['current_price']:.2f} ج.م")
                with col2:
                    st.metric("📊 RSI", f"{analysis['rsi']:.1f}")
                with col3:
                    st.metric("📈 المتوسط 20", f"{analysis['sma_20']:.2f}")
                with col4:
                    st.metric("🎯 التوصية", analysis['signal'])
                
                # الرسم البياني
                chart = create_advanced_chart(df, selected_ticker)
                st.plotly_chart(chart, use_container_width=True)
                
                # تخزين التحليل في قاعدة البيانات
                db = next(get_db())
                save_analysis(db, {
                    'ticker': selected_ticker,
                    'recommendation': analysis['signal'],
                    'confidence': 0.8 if analysis['signal'] != 'انتظار' else 0.3,
                    'analysis_text': f"RSI: {analysis['rsi']:.1f}, MA Signal: {analysis['ma_signal']}"
                })
                
            else:
                st.error("❌ لا يمكن جلب البيانات")
    
    # ============= التبويب 2: الأسهم المفضلة =============
    with tab2:
        st.header("⭐ الأسهم المفضلة")
        
        db = next(get_db())
        favorites = get_favorite_stocks(db, st.session_state.user_id)
        
        if favorites:
            for fav in favorites:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{fav.ticker}**")
                    with col2:
                        if st.button("📊 تحليل", key=f"analyze_{fav.id}"):
                            st.session_state.selected_ticker = fav.ticker
                    with col3:
                        if st.button("🗑️ حذف", key=f"delete_{fav.id}"):
                            remove_favorite_stock(db, st.session_state.user_id, fav.ticker)
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("لا توجد أسهم مفضلة. أضف من تبويب تحليل الأسهم")
    
    # ============= التبويب 3: المحفظة =============
    with tab3:
        st.header("💰 إدارة المحفظة")
        
        db = next(get_db())
        
        # نموذج إضافة صفقة
        with st.expander("➕ إضافة صفقة جديدة", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                ticker = st.selectbox("السهم", list(EGYPTIAN_STOCKS.keys()), key="portfolio_ticker")
            with col2:
                shares = st.number_input("عدد الأسهم", min_value=1.0, step=1.0)
            with col3:
                price = st.number_input("سعر الشراء", min_value=0.01, step=0.01)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ شراء", use_container_width=True):
                    portfolio = get_or_create_portfolio(db, st.session_state.user_id)
                    add_holding(db, portfolio.id, ticker, shares, price)
                    
                    # تسجيل المعاملة
                    transaction = Transaction(
                        user_id=st.session_state.user_id,
                        ticker=ticker,
                        type="BUY",
                        shares=shares,
                        price=price,
                        total_value=shares * price,
                        transaction_date=datetime.now()
                    )
                    db.add(transaction)
                    db.commit()
                    
                    st.success(f"تم شراء {shares} سهم من {ticker}")
                    st.rerun()
        
        # عرض المحفظة
        portfolio_summary = get_portfolio_summary(db, st.session_state.user_id)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 الرصيد النقدي", f"{portfolio_summary['total_cash']:,.2f} ج.م")
        with col2:
            st.metric("📊 قيمة الأسهم", f"{portfolio_summary['total_value'] - portfolio_summary['total_cash']:,.2f} ج.م")
        with col3:
            st.metric("💎 إجمالي المحفظة", f"{portfolio_summary['total_value']:,.2f} ج.م")
        
        if portfolio_summary['holdings']:
            st.subheader("📋 الحيازات الحالية")
            holdings_data = []
            for holding in portfolio_summary['holdings']:
                holdings_data.append({
                    "السهم": holding['ticker'],
                    "عدد الأسهم": holding['shares'],
                    "متوسط السعر": holding['avg_price'],
                    "إجمالي التكلفة": holding['total_cost']
                })
            
            st.dataframe(pd.DataFrame(holdings_data), use_container_width=True, hide_index=True)
    
    # ============= التبويب 4: التنبيهات =============
    with tab4:
        st.header("🔔 إدارة التنبيهات")
        
        # نموذج إضافة تنبيه
        with st.expander("➕ إضافة تنبيه جديد", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                alert_ticker = st.selectbox("السهم", list(EGYPTIAN_STOCKS.keys()), key="alert_ticker")
            with col2:
                alert_type = st.selectbox("نوع التنبيه", ["price", "rsi", "volume"])
            with col3:
                condition = st.selectbox("الشرط", ["above", "below"])
            
            target_value = st.number_input("القيمة المستهدفة", min_value=0.01, step=0.01)
            
            if st.button("✅ إنشاء تنبيه", use_container_width=True):
                db = next(get_db())
                create_alert(db, st.session_state.user_id, alert_ticker, alert_type, condition, target_value)
                st.success("تم إنشاء التنبيه بنجاح")
                st.rerun()
        
        # عرض التنبيهات الحالية
        db = next(get_db())
        alerts = get_active_alerts(db, st.session_state.user_id)
        
        if alerts:
            st.subheader("📋 التنبيهات النشطة")
            for alert in alerts:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{alert.ticker}**")
                with col2:
                    st.write(f"{alert.alert_type}")
                with col3:
                    st.write(f"{alert.condition} {alert.target_value}")
                with col4:
                    if st.button("🗑️", key=f"del_alert_{alert.id}"):
                        alert.is_active = False
                        db.commit()
                        st.rerun()
                st.markdown("---")
        else:
            st.info("لا توجد تنبيهات نشطة")
    
    # ============= التبويب 5: التقارير =============
    with tab5:
        st.header("📊 التقارير والإحصائيات")
        
        db = next(get_db())
        
        # إحصائيات عامة
        st.subheader("📈 إحصائيات عامة")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # عدد المعاملات
            transactions = db.query(Transaction).filter(Transaction.user_id == st.session_state.user_id).all()
            st.metric("📊 عدد المعاملات", len(transactions))
        
        with col2:
            # قيمة المحفظة
            portfolio_summary = get_portfolio_summary(db, st.session_state.user_id)
            st.metric("💰 إجمالي المحفظة", f"{portfolio_summary['total_value']:,.2f}")
        
        with col3:
            # عدد التنبيهات المفعلة
            alerts = get_active_alerts(db, st.session_state.user_id)
            st.metric("🔔 التنبيهات المفعلة", len(alerts))
        
        # آخر المعاملات
        if transactions:
            st.subheader("📋 آخر المعاملات")
            transactions_data = []
            for trans in transactions[-10:]:
                transactions_data.append({
                    "التاريخ": trans.transaction_date.strftime("%Y-%m-%d %H:%M"),
                    "السهم": trans.ticker,
                    "النوع": trans.type,
                    "الكمية": trans.shares,
                    "السعر": trans.price,
                    "الإجمالي": trans.total_value
                })
            
            st.dataframe(pd.DataFrame(transactions_data), use_container_width=True, hide_index=True)
        
        # زر تصدير التقرير
        if st.button("📥 تصدير التقرير (Excel)", use_container_width=True):
            # إنشاء تقرير Excel
            output = pd.ExcelWriter("report.xlsx", engine="openpyxl")
            
            # تصدير المعاملات
            if transactions:
                pd.DataFrame(transactions_data).to_excel(output, sheet_name="Transactions", index=False)
            
            # تصدير المحفظة
            if portfolio_summary['holdings']:
                pd.DataFrame(holdings_data).to_excel(output, sheet_name="Portfolio", index=False)
            
            output.close()
            
            with open("report.xlsx", "rb") as f:
                st.download_button(
    label="⬇️ تحميل التقرير", 
    data=st.session_state.get('last_analysis', ''), 
    file_name="stock_analysis.txt"
)
