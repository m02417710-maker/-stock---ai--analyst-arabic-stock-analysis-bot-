# ============================================================
# ملف: stock_analyzer_enhanced.py
# الوصف: محلل أسهم متكامل مع pandas_ta و Streamlit
# الإصدار: 4.0.0
# ============================================================

# ============================================================
# 1. المكتبات المطلوبة (قم بتثبيتها أولاً)
# ============================================================
# pip install streamlit yfinance pandas numpy plotly pandas-ta streamlit-autorefresh

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 2. إعدادات الصفحة والتصميم
# ============================================================

st.set_page_config(
    page_title="المحلل المصري المتكامل Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم CSS مخصص
st.markdown("""
<style>
/* تنسيق الخلفية الرئيسية */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* تنسيق بطاقات المؤشرات */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(59, 130, 246, 0.3);
    padding: 20px 15px;
    border-radius: 20px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #3b82f6;
}

/* تنسيق التبويبات */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 16px 16px 0 0;
    padding: 12px 28px;
    color: #cbd5e1;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white !important;
}

/* تنسيق الأزرار */
.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4);
}

/* تنسيق الشريط الجانبي */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(59, 130, 246, 0.2);
}

/* تنسيق مربعات الإدخال */
.stTextInput > div > div > input {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    color: white;
}

/* تنسيق القوائم المنسدلة */
.stSelectbox > div > div {
    background: #1e293b;
    border-radius: 12px;
    border: 1px solid #334155;
}

/* تنسيق أشرطة التوسيع */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 12px;
    color: #e2e8f0;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. قائمة الأسهم
# ============================================================

STOCKS_DATABASE = {
    "🇪🇬 البنك التجاري الدولي (مصر)": "COMI.CA",
    "🇪🇬 طلعت مصطفى (مصر)": "TMGH.CA",
    "🇪🇬 فوري (مصر)": "FWRY.CA",
    "🇸🇦 أرامكو (السعودية)": "2222.SR",
    "🇸🇦 الراجحي (السعودية)": "1120.SR",
    "🇸🇦 STC (السعودية)": "7010.SR",
    "🇺🇸 آبل (أمريكا)": "AAPL",
    "🇺🇸 تسلا (أمريكا)": "TSLA",
    "🇺🇸 مايكروسوفت (أمريكا)": "MSFT",
    "🇺🇸 إنفيديا (أمريكا)": "NVDA",
    "🇺🇸 أمازون (أمريكا)": "AMZN",
    "🇺🇸 جوجل (أمريكا)": "GOOGL"
}

# ============================================================
# 4. دوال جلب البيانات وحساب المؤشرات
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def fetch_stock_data(ticker):
    """جلب بيانات السهم من Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo", interval="1d")
        
        if df.empty or len(df) < 20:
            return None, None, None
        
        # حساب المؤشرات الفنية باستخدام pandas_ta
        # RSI
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # المتوسطات المتحركة
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['MA200'] = ta.sma(df['Close'], length=200)
        
        # Bollinger Bands
        bbands = ta.bbands(df['Close'], length=20, std=2)
        df = pd.concat([df, bbands], axis=1)
        
        # MACD
        macd = ta.macd(df['Close'])
        df = pd.concat([df, macd], axis=1)
        
        # حجم التداول المتوسط
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        # معلومات إضافية
        try:
            info = stock.info
        except:
            info = {}
        
        try:
            dividends = stock.dividends
        except:
            dividends = pd.Series()
        
        return df, dividends, info
        
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return None, None, None

def calculate_trading_score(df):
    """حساب درجة التداول بناءً على الشروط"""
    
    if df.empty or len(df) < 20:
        return 0, ["لا توجد بيانات كافية"]
    
    score = 0
    reasons = []
    last = df.iloc[-1]
    
    # الشرط 1: السعر فوق المتوسط المتحرك (اتجاه صاعد)
    if last['Close'] > last['MA20']:
        score += 1
        reasons.append("✅ السعر فوق المتوسط 20 (اتجاه صاعد)")
    else:
        reasons.append("⚠️ السعر تحت المتوسط 20 (اتجاه هابط)")
    
    # الشرط 2: RSI في منطقة شراء (ليس متضخماً)
    rsi = last['RSI']
    if not pd.isna(rsi):
        if 30 < rsi < 60:
            score += 1
            reasons.append(f"✅ RSI في منطقة تجميع ({rsi:.1f})")
        elif rsi <= 30:
            reasons.append(f"🔴 RSI في منطقة ذروة بيع ({rsi:.1f}) - فرصة شراء")
            score += 1  # فرصة شراء جيدة
        elif rsi >= 70:
            reasons.append(f"🟡 RSI في منطقة ذروة شراء ({rsi:.1f}) - توخ الحذر")
            score -= 1
        else:
            reasons.append(f"📊 RSI محايد ({rsi:.1f})")
    
    # الشرط 3: حجم التداول أعلى من المتوسط
    if last['Volume'] > last['Volume_MA20']:
        score += 1
        reasons.append("✅ حجم تداول مرتفع (سيولة جيدة)")
    else:
        reasons.append("📉 حجم تداول أقل من المتوسط")
    
    # الشرط 4: البولنجر باند (ارتداد من الحد السفلي)
    if 'BBL_20_2.0' in last and 'BBU_20_2.0' in last:
        if last['Close'] <= last['BBL_20_2.0']:
            score += 1
            reasons.append("✅ السعر عند الحد السفلي لبولنجر - ارتداد محتمل")
        elif last['Close'] >= last['BBU_20_2.0']:
            reasons.append("⚠️ السعر عند الحد العلوي لبولنجر - تصحيح محتمل")
            score -= 0.5
    
    # الشرط 5: MACD إيجابي
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1
            reasons.append("✅ MACD إيجابي (إشارة شراء)")
        else:
            reasons.append("📉 MACD سلبي (إشارة بيع)")
            score -= 0.5
    
    return score, reasons

# ============================================================
# 5. دوال الرسم البياني
# ============================================================

def create_advanced_chart(df, ticker):
    """إنشاء رسم بياني متقدم مع الشموع والمؤشرات"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.15, 0.2, 0.15],
        subplot_titles=("السعر والمؤشرات", "RSI", "MACD", "حجم التداول")
    )
    
    # الرسم البياني الرئيسي - الشموع اليابانية
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="السعر",
            showlegend=True
        ),
        row=1, col=1
    )
    
    # خطوط المتوسطات المتحركة
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['MA20'],
            name="MA 20",
            line=dict(color='#f59e0b', width=1.5),
            opacity=0.8
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['MA50'],
            name="MA 50",
            line=dict(color='#10b981', width=1.5),
            opacity=0.8
        ),
        row=1, col=1
    )
    
    # Bollinger Bands - المنطقة المظللة
    if 'BBU_20_2.0' in df.columns and 'BBL_20_2.0' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BBU_20_2.0'],
                name="الحد العلوي",
                line=dict(color='#94a3b8', width=1, dash='dash'),
                opacity=0.5
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BBL_20_2.0'],
                name="الحد السفلي",
                line=dict(color='#94a3b8', width=1, dash='dash'),
                opacity=0.5,
                fill='tonexty',
                fillcolor='rgba(148, 163, 184, 0.1)'
            ),
            row=1, col=1
        )
    
    # RSI
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['RSI'],
            name="RSI",
            line=dict(color='#8b5cf6', width=2),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.1)'
        ),
        row=2, col=1
    )
    
    # مناطق RSI
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    
    # MACD
    if 'MACD_12_26_9' in df.columns:
        # هيستوجرام MACD
        macd_hist = df['MACD_12_26_9'] - df['MACDs_12_26_9']
        colors = ['#10b981' if val >= 0 else '#ef4444' for val in macd_hist]
        
        fig.add_trace(
            go.Bar(
                x=df.index, y=macd_hist,
                name="MACD Histogram",
                marker_color=colors,
                opacity=0.7
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACD_12_26_9'],
                name="MACD",
                line=dict(color='#3b82f6', width=2)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACDs_12_26_9'],
                name="Signal",
                line=dict(color='#f59e0b', width=2)
            ),
            row=3, col=1
        )
    
    # حجم التداول
    volume_colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
                     for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index, y=df['Volume'],
            name="حجم التداول",
            marker_color=volume_colors,
            opacity=0.7
        ),
        row=4, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['Volume_MA20'],
            name="متوسط الحجم",
            line=dict(color='#3b82f6', width=2, dash='dash')
        ),
        row=4, col=1
    )
    
    # تحديث التصميم العام
    fig.update_layout(
        title=dict(
            text=f"📈 التحليل الفني المتقدم لسهم {ticker}",
            x=0.5,
            font=dict(size=20, color='#f1f5f9')
        ),
        template="plotly_dark",
        height=800,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor='rgba(15, 23, 42, 0.9)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(15, 23, 42, 0.8)'
        )
    )
    
    # تحديث محاور Y
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="الحجم", row=4, col=1)
    
    return fig

# ============================================================
# 6. واجهة المستخدم
# ============================================================

def render_sidebar():
    """عرض الشريط الجانبي"""
    
    with st.sidebar:
        # الشعار
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 26px; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                📊 المحلل المصري Pro
            </h1>
            <p style="color: #94a3b8; font-size: 12px;">النسخة المتطورة مع pandas_ta</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # اختيار السهم
        st.markdown("#### 🔍 اختيار السهم")
        
        selected_stock = st.selectbox(
            "من القائمة:",
            options=list(STOCKS_DATABASE.keys()),
            label_visibility="collapsed"
        )
        
        custom_ticker = st.text_input(
            "أو أدخل الرمز يدوياً:",
            placeholder="مثال: AAPL, TSLA, 2222.SR",
            key="ticker_input"
        )
        
        ticker = custom_ticker.strip().upper() if custom_ticker else STOCKS_DATABASE[selected_stock]
        
        st.info(f"📌 الرمز الحالي: `{ticker}`")
        
        st.markdown("---")
        
        # التحديث التلقائي
        st.markdown("#### 🔄 التحديث التلقائي")
        st.caption("يتم تحديث البيانات كل 15 دقيقة")
        
        if st.button("🔄 تحديث البيانات الآن", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # نصائح سريعة
        with st.sidebar.expander("💡 نصائح سريعة"):
            st.markdown("""
            ### 📊 مؤشر RSI
            - **RSI < 30:** منطقة ذروة بيع (فرصة شراء)
            - **RSI > 70:** منطقة ذروة شراء (توخ الحذر)
            - **RSI 40-60:** منطقة محايدة
            
            ### 📈 المتوسطات المتحركة
            - **السعر > MA20:** اتجاه صاعد قصير
            - **السعر < MA20:** اتجاه هابط قصير
            - **MA20 > MA50:** تأكيد صعودي
            
            ### 🎯 Bollinger Bands
            - **السعر عند الحد السفلي:** ارتداد محتمل
            - **السعر عند الحد العلوي:** تصحيح محتمل
            - **انكماش البولنجر:** هدوء قبل حركة قوية
            
            ### ⚡ MACD
            - **MACD > Signal:** إشارة شراء
            - **MACD < Signal:** إشارة بيع
            - **تقاطع عند خط الصفر:** إشارة قوية
            """)
    
    return ticker

def render_metrics(df, score, reasons):
    """عرض بطاقات المؤشرات"""
    
    if df.empty:
        return
    
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume_MA20'].iloc[-1] if not pd.isna(df['Volume_MA20'].iloc[-1]) else current_volume
    volume_ratio = (current_volume / avg_volume) * 100 if avg_volume > 0 else 100
    
    rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if price_change >= 0 else "inverse"
        st.metric(
            label="💰 السعر الحالي",
            value=f"{current_price:.2f}",
            delta=f"{price_change:+.2f}%",
            delta_color=delta_color
        )
    
    with col2:
        if rsi < 30:
            rsi_status = "🟢 ذروة بيع"
        elif rsi > 70:
            rsi_status = "🔴 ذروة شراء"
        else:
            rsi_status = "🟡 محايد"
        st.metric(
            label=f"📊 RSI ({rsi_status})",
            value=f"{rsi:.1f}"
        )
    
    with col3:
        st.metric(
            label="📈 حجم التداول",
            value=f"{current_volume/1000000:.1f}M",
            delta=f"{volume_ratio:.0f}% من المتوسط"
        )
    
    with col4:
        st.metric(
            label="📊 درجة الإشارة",
            value=f"{score}/5",
            help="كلما زادت النقاط، زادت قوة الإشارة"
        )

def render_signal_section(score, reasons):
    """عرض قسم الإشارات والتحليل"""
    
    # تحديد التوصية
    if score >= 4:
        recommendation = "🟢 إشارة شراء قوية جداً"
        color = "#10b981"
        icon = "🔥"
    elif score >= 3:
        recommendation = "🟢 إشارة شراء إيجابية"
        color = "#22c55e"
        icon = "📈"
    elif score >= 2:
        recommendation = "🟡 ميل للشراء"
        color = "#f59e0b"
        icon = "⚡"
    elif score <= 1:
        recommendation = "🔴 إشارة بيع أو انتظار"
        color = "#ef4444"
        icon = "⚠️"
    else:
        recommendation = "⚪ وضع محايد"
        color = "#94a3b8"
        icon = "➖"
    
    # عرض التوصية
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 20px; padding: 20px; margin: 15px 0;
                border: 1px solid {color}40;">
        <div style="text-align: center;">
            <h2 style="color: {color}; margin: 0;">
                {icon} {recommendation} {icon}
            </h2>
            <p style="color: #94a3b8; margin: 10px 0 0 0;">
                درجة الإشارة: {score}/5
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض تفاصيل الإشارات
    with st.expander("📋 تفاصيل الإشارات الفنية", expanded=True):
        for reason in reasons:
            st.markdown(reason)

# ============================================================
# 7. التشغيل الرئيسي
# ============================================================

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    
    # التحديث التلقائي كل 15 دقيقة
    st_autorefresh(interval=900000, key="auto_refresh")
    
    # عرض الشريط الجانبي
    ticker = render_sidebar()
    
    # العنوان الرئيسي
    st.markdown(f'<h2 style="text-align: center; color: #f1f5f9;">📊 تحليل ومراقبة: {ticker}</h2>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # جلب البيانات
    with st.spinner("🔄 جاري تحليل البيانات وحساب المؤشرات..."):
        df, dividends, info = fetch_stock_data(ticker)
    
    if df is None or df.empty:
        st.error("❌ لا يمكن جلب البيانات")
        st.markdown("""
        <div style="text-align: center; color: #f59e0b; padding: 20px;">
            ⚠️ تأكد من صحة رمز السهم<br>
            💡 أمثلة: AAPL, TSLA, 2222.SR, COMI.CA
        </div>
        """, unsafe_allow_html=True)
        return
    
    # حساب درجة التداول
    score, reasons = calculate_trading_score(df)
    
    # عرض بطاقات المؤشرات
    render_metrics(df, score, reasons)
    
    # عرض الإشارات
    render_signal_section(score, reasons)
    
    st.markdown("---")
    
    # التبويبات الرئيسية
    tab1, tab2, tab3 = st.tabs(["📈 الرسوم البيانية", "💰 التوزيعات", "ℹ️ معلومات الشركة"])
    
    with tab1:
        # الرسم البياني المتقدم
        fig = create_advanced_chart(df, ticker)
        st.plotly_chart(fig, use_container_width=True, key="main_chart")
    
    with tab2:
        st.subheader("💰 تاريخ توزيعات الأرباح")
        
        if not dividends.empty:
            div_df = pd.DataFrame({
                'التاريخ': dividends.index.strftime('%Y-%m-%d'),
                'القيمة': dividends.values
            })
            st.dataframe(div_df, use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي التوزيعات", f"{dividends.sum():.3f}")
            with col2:
                st.metric("متوسط التوزيع", f"{dividends.mean():.3f}")
            with col3:
                st.metric("آخر توزيع", f"{dividends.iloc[-1]:.3f}" if len(dividends) > 0 else "لا يوجد")
        else:
            st.info("📭 لا توجد بيانات توزيعات أرباح متاحة لهذا السهم")
    
    with tab3:
        st.subheader("ℹ️ معلومات الشركة")
        
        if info:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🏢 الاسم:** {info.get('longName', 'غير متوفر')}")
                st.markdown(f"**🏭 القطاع:** {info.get('sector', 'غير متوفر')}")
                st.markdown(f"**📋 الصناعة:** {info.get('industry', 'غير متوفر')}")
                st.markdown(f"**🌍 الدولة:** {info.get('country', 'غير متوفر')}")
                st.markdown(f"**🌐 الموقع:** {info.get('website', 'غير متوفر')}")
            
            with col2:
                if info.get('marketCap'):
                    st.markdown(f"**💰 القيمة السوقية:** ${info.get('marketCap', 0):,}")
                if info.get('trailingPE'):
                    st.markdown(f"**📊 مكرر الأرباح:** {info.get('trailingPE', 'غير متوفر')}")
                if info.get('dividendYield'):
                    st.markdown(f"**💵 عائد التوزيعات:** {info.get('dividendYield', 0)*100:.2f}%")
                if info.get('beta'):
                    st.markdown(f"**📈 معامل بيتا:** {info.get('beta', 'غير متوفر')}")
                if info.get('52WeekHigh'):
                    st.markdown(f"**🎯 أعلى 52 أسبوع:** ${info.get('52WeekHigh', 'غير متوفر')}")
        else:
            st.info("📭 معلومات الشركة غير متوفرة حالياً")
    
    # تذييل الصفحة
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 12px;">
        <p>📊 تم التحليل بواسطة <strong>المحلل المصري Pro</strong> | pandas_ta | Yahoo Finance</p>
        <p>🕐 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>⚠️ <strong>تنويه:</strong> هذا التحليل لأغراض تعليمية فقط، وليس توصية استثمارية</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# تشغيل التطبيق
# ============================================================
if __name__ == "__main__":
    main()
