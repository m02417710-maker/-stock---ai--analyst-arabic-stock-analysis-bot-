# ============================================================
# ملف: stock_analyzer_v6.py
# الإصدار المتطور: نظام نقاط ذكي + تقارير + واجهة محسنة + دمج كامل
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# إعدادات الصفحة والتصميم المتقدم
# ============================================================

st.set_page_config(
    page_title="المحلل المصري Pro - V6",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم CSS محسن
st.markdown("""
<style>
/* تنسيق الخلفية */
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
    font-size: 16px;
}

/* تنسيق أشرطة التوسيع */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 12px;
    color: #e2e8f0;
    font-weight: 600;
}

/* تنسيق الـ JSON viewer */
.stJson {
    background: #1e293b;
    border-radius: 12px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# قائمة الأسهم السريعة
# ============================================================

QUICK_STOCKS = {
    "🇪🇬 البنك التجاري الدولي": "COMI.CA",
    "🇪🇬 طلعت مصطفى": "TMGH.CA",
    "🇪🇬 فوري": "FWRY.CA",
    "🇸🇦 أرامكو": "2222.SR",
    "🇸🇦 الراجحي": "1120.SR",
    "🇺🇸 آبل": "AAPL",
    "🇺🇸 تسلا": "TSLA",
    "🇺🇸 مايكروسوفت": "MSFT",
    "🇺🇸 إنفيديا": "NVDA"
}

# ============================================================
# دالة حساب النقاط المتطورة (Smart Weighting)
# ============================================================

def calculate_smart_score(df):
    """حساب درجة ذكية مع أوزان مختلفة لكل مؤشر"""
    if df.empty or len(df) < 20:
        return 0, [], {}
    
    score = 0
    reasons = []
    details = {}
    last = df.iloc[-1]
    
    # 1. الاتجاه العام (الوزن: 1.0)
    if last['Close'] > last['MA20']:
        score += 1.0
        reasons.append("✅ السعر فوق المتوسط 20 (اتجاه صاعد)")
        details['trend'] = 'up'
    else:
        reasons.append("⚠️ السعر تحت المتوسط 20 (اتجاه هابط)")
        details['trend'] = 'down'
        score -= 0.5
    
    # 2. مؤشر القوة النسبية RSI (الوزن: 1.5)
    rsi = last['RSI']
    details['rsi'] = round(rsi, 1)
    
    if rsi <= 30:
        score += 1.5
        reasons.append(f"🔥 فرصة ذهبية: ذروة بيع شديدة ({rsi:.1f})")
    elif 30 < rsi <= 40:
        score += 1.2
        reasons.append(f"✅ منطقة شراء ممتازة ({rsi:.1f})")
    elif 40 < rsi < 55:
        score += 0.8
        reasons.append(f"✅ RSI في منطقة تجميع آمنة ({rsi:.1f})")
    elif 55 <= rsi < 70:
        score += 0.2
        reasons.append(f"📊 RSI في منطقة محايدة ({rsi:.1f})")
    elif rsi >= 70:
        score -= 1.0
        reasons.append(f"⚠️ تحذير: ذروة شراء شديدة ({rsi:.1f})")
    
    # 3. تقاطع MACD (الوزن: 1.5) - مؤشر قوي جداً
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        macd = last['MACD_12_26_9']
        signal = last['MACDs_12_26_9']
        details['macd'] = round(macd, 3)
        details['macd_signal'] = round(signal, 3)
        
        if macd > signal:
            score += 1.5
            reasons.append("🚀 إشارة اختراق MACD إيجابية قوية")
            details['macd_cross'] = 'bullish'
        else:
            score -= 0.5
            reasons.append("📉 تقاطع MACD سلبي")
            details['macd_cross'] = 'bearish'
    
    # 4. السيولة وحجم التداول (الوزن: 1.0)
    vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
    current_vol = last['Volume']
    vol_ratio = (current_vol / vol_ma) * 100 if vol_ma > 0 else 100
    details['volume_ratio'] = round(vol_ratio, 1)
    
    if current_vol > vol_ma:
        score += 1.0
        reasons.append(f"💰 سيولة مؤسسية أعلى من المعدل ({vol_ratio:.0f}%)")
    else:
        reasons.append(f"📉 حجم تداول أقل من المعدل ({vol_ratio:.0f}%)")
        score -= 0.3
    
    # 5. البولنجر باند (الوزن: 0.5)
    if 'BBL_20_2.0' in last and 'BBU_20_2.0' in last:
        if last['Close'] <= last['BBL_20_2.0']:
            score += 0.8
            reasons.append("🎯 السعر عند الحد السفلي لبولنجر - ارتداد محتمل")
            details['bb_position'] = 'lower'
        elif last['Close'] >= last['BBU_20_2.0']:
            score -= 0.5
            reasons.append("⚠️ السعر عند الحد العلوي لبولنجر - تصحيح محتمل")
            details['bb_position'] = 'upper'
        else:
            details['bb_position'] = 'middle'
    
    # تحديد مستوى الثقة
    if score >= 4.5:
        confidence = "🔥 قوي جداً"
    elif score >= 3.5:
        confidence = "✅ قوي"
    elif score >= 2.5:
        confidence = "🟡 متوسط"
    elif score >= 1.5:
        confidence = "⚠️ ضعيف"
    else:
        confidence = "🔴 ضعيف جداً"
    
    details['confidence'] = confidence
    details['final_score'] = round(score, 1)
    
    return round(score, 1), reasons, details

# ============================================================
# دالة جلب البيانات مع دعم المعلومات المالية
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def get_full_data(ticker):
    """جلب البيانات الكاملة للسهم مع المؤشرات الفنية"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        
        if df.empty or len(df) < 20:
            return None, None
        
        # حساب المؤشرات الفنية باستخدام pandas_ta
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['MA200'] = ta.sma(df['Close'], length=200)
        
        # Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        
        # MACD
        macd = ta.macd(df['Close'])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        
        # حجم التداول المتوسط
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        # حساب نطاق اليوم
        df['Day_High'] = df['High']
        df['Day_Low'] = df['Low']
        df['Day_Range'] = ((df['High'] - df['Low']) / df['Low']) * 100
        
        return df, stock.info
        
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return None, None

# ============================================================
# دالة الرسم البياني المتقدم
# ============================================================

def create_advanced_chart(df, ticker):
    """إنشاء رسم بياني متكامل مع جميع المؤشرات"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.15, 0.2, 0.15],
        subplot_titles=("📈 السعر والمؤشرات", "📊 مؤشر القوة النسبية RSI", "⚡ مؤشر MACD", "💰 حجم التداول")
    )
    
    # ===== الرسم البياني الرئيسي =====
    # الشموع اليابانية
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
    
    # المتوسطات المتحركة
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
    
    # ===== مؤشر RSI =====
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
    
    # ===== مؤشر MACD =====
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
    
    # ===== حجم التداول =====
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
            name="متوسط 20 يوم",
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
        height=850,
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
# الواجهة الرئيسية
# ============================================================

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    
    # التحديث التلقائي كل 15 دقيقة
    st_autorefresh(interval=900000, key="auto_refresh_v6")
    
    # ===== الشريط الجانبي =====
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 24px; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                📊 المحلل المصري Pro
            </h1>
            <p style="color: #94a3b8; font-size: 12px;">الإصدار V6 - نظام النقاط الذكي</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # اختيار سريع
        st.markdown("#### 🚀 اختيار سريع")
        quick_select = st.selectbox("أسعار سريعة:", list(QUICK_STOCKS.keys()))
        
        st.markdown("#### 🔍 إدخال يدوي")
        ticker = st.text_input("رمز السهم:", value=QUICK_STOCKS[quick_select]).upper()
        
        st.markdown("---")
        
        # أزرار التحكم
        if st.button("🔄 تحديث شامل", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # معلومات إضافية
        st.markdown("#### ℹ️ معلومات")
        st.caption(f"🕐 تحديث تلقائي كل 15 دقيقة")
        st.caption(f"📊 مصدر البيانات: Yahoo Finance")
        st.caption(f"⚡ الإصدار: V6.0.0")
        
        st.markdown("---")
        
        # نصائح سريعة
        with st.expander("💡 دليل الإشارات", expanded=False):
            st.markdown("""
            ### 🎯 نظام النقاط (من 0 إلى 5+)
            - **4.5+:** 🔥 فرصة شراء قوية جداً
            - **3.5 - 4.5:** ✅ إشارة شراء إيجابية
            - **2.5 - 3.5:** 🟡 وضع محايد مع ميل للإيجابية
            - **1.5 - 2.5:** ⚠️ توخ الحذر
            - **< 1.5:** 🔴 انتظار أو بيع
            
            ### 📊 قراءة المؤشرات
            - **RSI < 30:** منطقة ذروة بيع (فرصة شراء)
            - **RSI > 70:** منطقة ذروة شراء (توخ الحذر)
            - **MACD > Signal:** إشارة صاعدة
            - **السعر > MA20:** اتجاه صاعد قصير
            """)
    
    # ===== العنوان الرئيسي =====
    st.markdown(f'<h2 style="text-align: center; color: #f1f5f9;">📊 تحليل ومراقبة: {ticker}</h2>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # ===== جلب البيانات =====
    with st.spinner("🔄 جاري تحليل البيانات وحساب المؤشرات..."):
        df, info = get_full_data(ticker)
    
    if df is None or df.empty:
        st.error("❌ لا يمكن جلب البيانات")
        st.markdown("""
        <div style="text-align: center; color: #f59e0b; padding: 20px;">
            ⚠️ تأكد من صحة رمز السهم<br>
            💡 أمثلة: AAPL, TSLA, 2222.SR, COMI.CA
        </div>
        """, unsafe_allow_html=True)
        return
    
    # ===== حساب النقاط الذكية =====
    score, reasons, details = calculate_smart_score(df)
    
    # ===== معلومات سريعة =====
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume_MA20'].iloc[-1] if not pd.isna(df['Volume_MA20'].iloc[-1]) else current_volume
    volume_ratio = (current_volume / avg_volume) * 100 if avg_volume > 0 else 100
    
    # عرض البطاقات
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_color = "normal" if price_change >= 0 else "inverse"
        st.metric("💰 السعر", f"{current_price:.2f}", f"{price_change:+.2f}%", delta_color=delta_color)
    
    with col2:
        rsi = details.get('rsi', 50)
        rsi_status = "🟢 ذروة بيع" if rsi < 30 else ("🔴 ذروة شراء" if rsi > 70 else "🟡 محايد")
        st.metric(f"📊 RSI ({rsi_status})", f"{rsi:.1f}")
    
    with col3:
        st.metric("📈 الحجم", f"{current_volume/1000000:.1f}M", f"{volume_ratio:.0f}%")
    
    with col4:
        st.metric("🎯 درجة الثقة", f"{score}/5", details.get('confidence', ''))
    
    with col5:
        # تحديد التوصية
        if score >= 4:
            rec = "🔥 شراء قوي"
            rec_color = "#10b981"
        elif score >= 3:
            rec = "✅ شراء محتمل"
            rec_color = "#22c55e"
        elif score >= 2:
            rec = "🟡 ترقب"
            rec_color = "#f59e0b"
        else:
            rec = "🔴 انتظار/بيع"
            rec_color = "#ef4444"
        st.metric("📋 التوصية", rec)
    
    st.markdown("---")
    
    # ===== بطاقة التوصية الموسعة =====
    if score >= 4:
        rec_title = "🔥 فرصة شراء قوية جداً"
        rec_color = "#10b981"
        rec_icon = "🚀"
    elif score >= 3:
        rec_title = "✅ إشارة شراء إيجابية"
        rec_color = "#22c55e"
        rec_icon = "📈"
    elif score >= 2:
        rec_title = "🟡 وضع محايد مع ميل للإيجابية"
        rec_color = "#f59e0b"
        rec_icon = "⚡"
    elif score >= 1:
        rec_title = "⚠️ توخ الحذر - إشارات متضاربة"
        rec_color = "#fb923c"
        rec_icon = "⚠️"
    else:
        rec_title = "🔴 انتظار أو بيع - إشارات سلبية"
        rec_color = "#ef4444"
        rec_icon = "📉"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 20px; padding: 25px; margin: 15px 0;
                border: 2px solid {rec_color}40;">
        <div style="text-align: center;">
            <h2 style="color: {rec_color}; margin: 0;">
                {rec_icon} {rec_title} {rec_icon}
            </h2>
            <p style="color: #94a3b8; margin: 10px 0 0 0; font-size: 18px;">
                درجة الثقة: {score}/5 | {details.get('confidence', '')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== عرض تفاصيل الإشارات =====
    with st.expander("📋 تفاصيل الإشارات الفنية (نظام النقاط الذكي)", expanded=True):
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("#### 🎯 نقاط القوة")
            for reason in reasons:
                if reason.startswith("✅") or reason.startswith("🔥") or reason.startswith("🚀") or reason.startswith("💰"):
                    st.markdown(reason)
        
        with col_right:
            st.markdown("#### 📊 ملخص المؤشرات")
            st.markdown(f"- **RSI:** {details.get('rsi', 'N/A')}")
            st.markdown(f"- **MACD:** {details.get('macd', 'N/A')}")
            st.markdown(f"- **حجم التداول:** {details.get('volume_ratio', 'N/A')}% من المتوسط")
            st.markdown(f"- **الاتجاه:** {details.get('trend', 'N/A')}")
            if 'macd_cross' in details:
                st.markdown(f"- **MACD تقاطع:** {details.get('macd_cross', 'N/A')}")
    
    st.markdown("---")
    
    # ===== التبويبات الرئيسية =====
    tab_chart, tab_info, tab_reports = st.tabs(["📈 الرسم البياني", "🏢 بيانات الشركة", "📄 تقارير وتصدير"])
    
    with tab_chart:
        # الرسم البياني المتقدم
        fig = create_advanced_chart(df, ticker)
        st.plotly_chart(fig, use_container_width=True, key="advanced_chart_v6")
        
        # جدول آخر 10 أيام
        st.markdown("---")
        st.subheader("📋 آخر 10 أيام تداول")
        recent_df = df.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI']].round(2)
        recent_df.index = recent_df.index.strftime('%Y-%m-%d')
        recent_df.columns = ['الافتتاح', 'الأعلى', 'الأدنى', 'الإغلاق', 'الحجم', 'RSI']
        st.dataframe(recent_df, use_container_width=True)
    
    with tab_info:
        st.subheader("🏢 معلومات الشركة")
        
        if info:
            # معلومات أساسية
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 معلومات عامة")
                st.markdown(f"**🏢 الاسم:** {info.get('longName', 'غير متوفر')}")
                st.markdown(f"**🏭 القطاع:** {info.get('sector', 'غير متوفر')}")
                st.markdown(f"**📋 الصناعة:** {info.get('industry', 'غير متوفر')}")
                st.markdown(f"**🌍 الدولة:** {info.get('country', 'غير متوفر')}")
                st.markdown(f"**🌐 الموقع:** {info.get('website', 'غير متوفر')}")
            
            with col2:
                st.markdown("#### 💰 معلومات مالية")
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
                if info.get('52WeekLow'):
                    st.markdown(f"**🎯 أدنى 52 أسبوع:** ${info.get('52WeekLow', 'غير متوفر')}")
            
            # وصف الشركة
            st.markdown("---")
            st.markdown("#### 📝 وصف الشركة")
            st.markdown(info.get('longBusinessSummary', 'لا يوجد وصف متاح')[:800] + "...")
            
            # بيانات JSON كاملة
            with st.expander("🔍 عرض جميع البيانات (JSON)"):
                st.json(info)
        else:
            st.info("📭 معلومات الشركة غير متوفرة حالياً")
    
    with tab_reports:
        st.subheader("📄 تقارير وتصدير البيانات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 تقرير التحليل")
            st.markdown(f"**السهم:** {ticker}")
            st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**درجة الثقة:** {score}/5 - {details.get('confidence', '')}")
            st.markdown(f"**التوصية:** {rec_title}")
            st.markdown("---")
            st.markdown("**نقاط القوة:**")
            for reason in reasons[:5]:
                st.markdown(f"- {reason}")
        
        with col2:
            st.markdown("#### 📥 تصدير البيانات")
            
            # تحميل CSV
            csv_data = df[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MA20', 'MA50']].round(2).to_csv()
            st.download_button(
                label="📥 تحميل بيانات التحليل (CSV)",
                data=csv_data,
                file_name=f"{ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # تحميل التقرير النصي
            report_text = f"""
            ========================================
            تقرير تحليل سهم {ticker}
            ========================================
            
            التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            -------- المعلومات الأساسية --------
            السعر الحالي: {current_price:.2f}
            التغير: {price_change:+.2f}%
            حجم التداول: {current_volume/1000000:.1f}M
            نسبة الحجم: {volume_ratio:.0f}%
            
            -------- المؤشرات الفنية --------
            RSI: {details.get('rsi', 'N/A')}
            MACD: {details.get('macd', 'N/A')}
            إشارة MACD: {details.get('macd_cross', 'N/A')}
            الاتجاه: {details.get('trend', 'N/A')}
            
            -------- التوصية --------
            درجة الثقة: {score}/5
            مستوى الثقة: {details.get('confidence', '')}
            التوصية النهائية: {rec_title}
            
            -------- نقاط القوة --------
            {chr(10).join(['- ' + r for r in reasons[:5]])}
            
            ========================================
            تنويه: هذا التحليل لأغراض تعليمية فقط
            ========================================
            """
            
            st.download_button(
                label="📄 تحميل تقرير نصي (TXT)",
                data=report_text,
                file_name=f"{ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # رسم بياني إضافي للمؤشرات
        st.subheader("📈 تطور المؤشرات الفنية")
        
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.5, 0.5])
        
        fig2.add_trace(
            go.Scatter(x=df.index, y=df['Close'], name="السعر", line=dict(color='#3b82f6')),
            row=1, col=1
        )
        fig2.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#8b5cf6')),
            row=
        )
