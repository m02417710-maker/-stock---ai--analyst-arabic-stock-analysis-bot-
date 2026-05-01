# البورصجي AI - النسخة الاحترافية (محاكاة الصورة)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="البورصجي AI - منصة التداول",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS مخصص لمحاكاة التصميم في الصورة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0e1117 100%);
    }
    
    /* الهيدر العلوي */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 25px;
        background: rgba(10, 10, 15, 0.95);
        border-bottom: 1px solid #00ffcc30;
        margin-bottom: 20px;
    }
    
    .logo-title {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #00ffcc, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* بطاقات المؤشرات */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 25px;
        padding: 0 10px;
    }
    
    .stat-card {
        background: rgba(15, 20, 30, 0.9);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(0, 255, 204, 0.15);
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        border-color: #00ffcc;
        transform: translateY(-2px);
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: bold;
        background: linear-gradient(135deg, #fff, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        font-size: 12px;
        color: #888;
        margin-top: 5px;
    }
    
    .stat-change-positive {
        color: #00ff88;
        font-size: 12px;
    }
    
    .stat-change-negative {
        color: #ff4444;
        font-size: 12px;
    }
    
    /* شريط البحث */
    .search-bar {
        background: rgba(20, 25, 35, 0.9);
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
    
    /* الجدول الاحترافي */
    .data-table-container {
        background: rgba(15, 20, 30, 0.8);
        border-radius: 16px;
        padding: 15px;
        border: 1px solid rgba(0, 255, 204, 0.1);
    }
    
    /* تذييل */
    .footer {
        text-align: center;
        padding: 20px;
        color: #555;
        font-size: 11px;
        margin-top: 30px;
        border-top: 1px solid #1a1a1a;
    }
    
    /* تنسيق الأرقام في الجدول */
    .positive {
        color: #00ff88;
        font-weight: bold;
    }
    
    .negative {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* أزرار */
    .stButton > button {
        background: linear-gradient(135deg, #ff4b4b, #ff7676);
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* شريط التمرير */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00ffcc;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. دوال جلب البيانات
@st.cache_data(ttl=30)
def get_live_stock_data():
    """جلب بيانات حية للأسهم"""
    stocks = {
        "AMES_R2": {"name": "أميس", "ticker": None},
        "EALR": {"name": "إيال آر", "ticker": None},
        "AALR": {"name": "إيال آر", "ticker": None},
        "AMES": {"name": "أميس", "ticker": None},
        "DEIN": {"name": "دين", "ticker": None},
        "WKOL": {"name": "وكول", "ticker": None},
        "SNCR": {"name": "سنكر", "ticker": None},
        "NNNN": {"name": "إن إن", "ticker": None},
        "SVCE_R1": {"name": "سيرفيس", "ticker": None},
        "KWIN": {"name": "كوين", "ticker": None},
        "EGSA": {"name": "إيجسا", "ticker": None}
    }
    
    # محاكاة البيانات (لأن الصورة تظهر بيانات حقيقية)
    data = [
        {"الرمز": "AMES_R2", "السيولة": "11%", "طلب/حجم": "48.65", "عرض/حجم": "40.65", "التغيير": "+0.71%", "آخر": 40.65},
        {"الرمز": "EALR", "السيولة": "61%", "طلب/حجم": "396.15", "عرض/حجم": "395.08", "التغيير": "+1.06%", "آخر": 396.15},
        {"الرمز": "AALR", "السيولة": "65%", "طلب/حجم": "214.11", "عرض/حجم": "214.10", "التغيير": "+1.06%", "آخر": 214.11},
        {"الرمز": "AMES", "السيولة": "57%", "طلب/حجم": "55.87", "عرض/حجم": "55.87", "التغيير": "+1.06%", "آخر": 55.87},
        {"الرمز": "DEIN", "السيولة": "--", "طلب/حجم": "13.65", "عرض/حجم": "8.60", "التغيير": "+1.95%", "آخر": 13.65},
        {"الرمز": "WKOL", "السيولة": "70%", "طلب/حجم": "331.08", "عرض/حجم": "333.08", "التغيير": "-1.87%", "آخر": 330.80},
        {"الرمز": "SNCR", "السيولة": "68%", "طلب/حجم": "20.54", "عرض/حجم": "20.54", "التغيير": "+1.73%", "آخر": 20.54},
        {"الرمز": "NNNN", "السيولة": "63%", "طلب/حجم": "20.54", "عرض/حجم": "20.54", "التغيير": "+1.73%", "آخر": 20.54},
        {"الرمز": "SVCE_R1", "السيولة": "63%", "طلب/حجم": "2.71", "عرض/حجم": "2.71", "التغيير": "+1.61%", "آخر": 2.71},
        {"الرمز": "KWIN", "السيولة": "55%", "طلب/حجم": "77.58", "عرض/حجم": "77.58", "التغيير": "+0.92%", "آخر": 77.58},
        {"الرمز": "EGSA", "السيولة": "90%", "طلب/حجم": "8.64", "عرض/حجم": "8.64", "التغيير": "+0.92%", "آخر": 8.65}
    ]
    
    return pd.DataFrame(data)

@st.cache_data(ttl=60)
def get_market_stats():
    """جلب إحصائيات السوق"""
    return {
        "EGX30": {"value": 51760.97, "change": -1.19},
        "EGX70": {"value": 14028.98, "change": +0.04},
        "Volume": {"value": "11.08B", "change": None},
        "S&P500": {"value": 7230.11, "change": +0.32}
    }

# 4. واجهة المستخدم الرئيسية
def main():
    # الهيدر
    st.markdown("""
    <div class="main-header">
        <div>
            <span class="logo-title">📈 البورصجي AI</span>
            <span style="font-size: 12px; color: #888; margin-right: 10px;">PRO TERMINAL</span>
        </div>
        <div style="display: flex; gap: 15px;">
            <span style="font-size: 12px;">📅 """ + datetime.now().strftime("%Y-%m-%d") + """</span>
            <span class="live-badge" style="color: #ff4444;">● LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # بطاقات المؤشرات
    stats = get_market_stats()
    
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    
    # EGX30
    egx30_color = "stat-change-negative" if stats["EGX30"]["change"] < 0 else "stat-change-positive"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats["EGX30"]["value"]:,.2f}</div>
        <div class="stat-label">EGX 30</div>
        <div class="{egx30_color}">{stats["EGX30"]["change"]:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # EGX70
    egx70_color = "stat-change-positive" if stats["EGX70"]["change"] > 0 else "stat-change-negative"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats["EGX70"]["value"]:,.2f}</div>
        <div class="stat-label">EGX 70</div>
        <div class="{egx70_color}">{stats["EGX70"]["change"]:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # حجم التداول
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats["Volume"]["value"]}</div>
        <div class="stat-label">حجم التداول</div>
    </div>
    """, unsafe_allow_html=True)
    
    # S&P 500
    sp_color = "stat-change-positive" if stats["S&P500"]["change"] > 0 else "stat-change-negative"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats["S&P500"]["value"]:,.2f}</div>
        <div class="stat-label">S&P 500</div>
        <div class="{sp_color}">{stats["S&P500"]["change"]:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # شريط البحث
    st.markdown("""
    <div class="search-bar">
        <div style="display: flex; gap: 10px; align-items: center;">
            <span>🔍</span>
            <input type="text" placeholder="بحث..." style="background: transparent; border: none; color: white; width: 100%; outline: none;">
            <span style="color: #00ffcc;">⏎</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # تبويبات التصنيفات
    tab1, tab2, tab3 = st.tabs(["📊 السلوكيات", "🏭 الصناعات", "🛢️ النفطية"])
    
    with tab1:
        st.markdown('<div class="data-table-container">', unsafe_allow_html=True)
        
        # جلب البيانات
        df = get_live_stock_data()
        
        # تنسيق DataFrame للعرض
        display_df = df.copy()
        
        # إضافة ألوان للتغيير
        def color_change(val):
            if '+' in str(val):
                return 'positive'
            elif '-' in str(val):
                return 'negative'
            return ''
        
        # عرض الجدول بتنسيق احترافي
        st.dataframe(
            display_df,
            column_config={
                "الرمز": st.column_config.TextColumn("الرمز", width="small"),
                "السيولة": st.column_config.TextColumn("السيولة", width="small"),
                "طلب/حجم": st.column_config.NumberColumn("طلب/حجم", format="%.2f"),
                "عرض/حجم": st.column_config.NumberColumn("عرض/حجم", format="%.2f"),
                "التغيير": st.column_config.TextColumn("%", width="small"),
                "آخر": st.column_config.NumberColumn("آخر", format="%.2f")
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # إحصائيات إضافية
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background: rgba(0, 255, 204, 0.05); border-radius: 12px; padding: 15px; margin-top: 15px;">
                <div style="color: #00ffcc;">📊 قطاع مطارق</div>
                <div style="font-size: 24px; font-weight: bold;">61%</div>
                <div style="font-size: 12px; color: #888;">نسبة النشاط</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: rgba(255, 68, 68, 0.05); border-radius: 12px; padding: 15px; margin-top: 15px;">
                <div style="color: #ff4444;">⚠️ تنبيهات</div>
                <div style="font-size: 24px; font-weight: bold;">3</div>
                <div style="font-size: 12px; color: #888;">صفقات بحاجة للمراجعة</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.info("🏭 بيانات قطاع الصناعات قيد التحديث")
        
        # مؤشرات القطاعات
        sectors = {
            "البنوك": 2.5,
            "العقارات": -1.2,
            "الاتصالات": 3.1,
            "الصناعة": 0.8,
            "التجارة": -0.5
        }
        
        for sector, change in sectors.items():
            color = "#00ff88" if change > 0 else "#ff4444"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #222;">
                <span>{sector}</span>
                <span style="color: {color};">{change:+.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.info("🛢️ بيانات قطاع النفطية قيد التحديث")
    
    # زر تحديث
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # تذييل
    st.markdown(f"""
    <div class="footer">
        🕶️ البورصجي AI PRO TERMINAL | العين التي لا تنام في الأسواق<br>
        📊 تحديث لحظي • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
