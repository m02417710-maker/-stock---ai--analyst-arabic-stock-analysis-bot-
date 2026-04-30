import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# تكوين الصفحة والإعدادات الأساسية
# ============================================================================

st.set_page_config(
    page_title="المحلل المصري Pro | تحليل الأسهم الذكي",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# التصميم المتقدم (CSS المحسن)
# ============================================================================

def load_advanced_css():
    """تحميل أنماط CSS المتقدمة"""
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
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetric"] value {
        color: #f1f5f9 !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }
    
    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px 16px 0 0;
        padding: 12px 28px;
        color: #cbd5e1;
        font-weight: 600;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #2d3a4e 0%, #1e293b 100%);
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
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
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4);
    }
    
    /* تنسيق مربعات الإدخال */
    .stTextInput > div > div > input {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        color: white;
        padding: 10px 15px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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
    
    /* تنسيق الشريط الجانبي */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* تنسيق الإشعارات والتنبيهات */
    .stAlert {
        border-radius: 12px;
        border-right: 4px solid #3b82f6;
    }
    
    /* تنسيق العنوان الرئيسي */
    .main-header {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* تنسيق بطاقة الإشارة */
    .signal-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    /* تنسيق النص التحذيري */
    .warning-text {
        color: #f59e0b;
        font-size: 14px;
        text-align: center;
        margin-top: 20px;
    }
    
    /* تنسيق زر التحديث في الشريط الجانبي */
    .update-button {
        margin-top: 20px;
    }
    
    /* شريط التمرير المخصص */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3b82f6;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

load_advanced_css()

# ============================================================================
# إعدادات التطبيق
# ============================================================================

@dataclass
class AppConfig:
    """إعدادات التطبيق المركزية"""
    title: str = "المحلل المصري Pro"
    version: str = "3.0.0"
    cache_ttl: int = 300
    update_interval: int = 15
    company: str = "Stock Analyzer"
    
    # الألوان الأساسية
    colors: Dict = None
    
    def __post_init__(self):
        self.colors = {
            'primary': '#3b82f6',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'dark': '#0f172a',
            'light': '#f1f5f9'
        }

config = AppConfig()

# قائمة الأسهم الموسعة
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
    "🇺🇸 إنفيديا (أمريكا)": "NVDA"
}

# ============================================================================
# مكدس استرجاع البيانات المحسن
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_data(ticker: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[Dict]]:
    """جلب بيانات السوق مع معالجة متقدمة للأخطاء"""
    
    if not ticker or ticker.strip() == "":
        return None, None, None
    
    try:
        # تهيئة كائن السهم
        stock = yf.Ticker(ticker)
        
        # جلب بيانات التاريخ
        df = stock.history(period="6mo", interval="1d")
        
        if df.empty or len(df) < 5:
            return None, None, None
        
        # حساب المؤشرات الفنية
        df = calculate_technical_indicators(df)
        
        # جلب التوزيعات
        try:
            dividends = stock.dividends
        except:
            dividends = pd.Series()
        
        # جلب معلومات الشركة
        try:
            info = stock.info
        except:
            info = {}
        
        return df, dividends, info
        
    except Exception as e:
        return None, None, None

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """حساب المؤشرات الفنية المتقدمة"""
    
    # المتوسطات المتحركة
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # مؤشر القوة النسبية RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
    
    # حجم التداول
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    
    return df

def analyze_signal(df: pd.DataFrame) -> Dict:
    """تحليل الإشارات المتقدم"""
    
    if df.empty:
        return {"signal": "لا توجد بيانات", "score": 0, "details": []}
    
    latest = df.iloc[-1]
    details = []
    score = 0
    
    # تحليل RSI
    rsi = latest['RSI']
    if rsi < 30:
        details.append("🔴 RSI منخفض جداً - منطقة ذروة بيع")
        score += 2
    elif rsi > 70:
        details.append("🟡 RSI مرتفع جداً - منطقة ذروة شراء")
        score -= 1
    else:
        details.append(f"✅ RSI في المستوى الطبيعي ({rsi:.1f})")
    
    # تحليل MACD
    if latest['MACD'] > latest['MACD_signal']:
        details.append("📈 إشارة MACD إيجابية (صاعد)")
        score += 1
    else:
        details.append("📉 إشارة MACD سلبية (هابط)")
        score -= 1
    
    # تحليل المتوسطات المتحركة
    if latest['Close'] > latest['MA20']:
        details.append("✅ السعر فوق المتوسط المتحرك 20")
        score += 1
    else:
        details.append("⚠️ السعر تحت المتوسط المتحرك 20")
        score -= 1
    
    # التوصية النهائية
    if score >= 2:
        signal = "🟢 إشارة شراء قوية"
        signal_color = "#10b981"
    elif score >= 1:
        signal = "🟡 ميل للشراء"
        signal_color = "#f59e0b"
    elif score <= -2:
        signal = "🔴 إشارة بيع قوية"
        signal_color = "#ef4444"
    elif score <= -1:
        signal = "🟠 ميل للبيع"
        signal_color = "#f59e0b"
    else:
        signal = "⚪ وضع محايد - انتظار"
        signal_color = "#94a3b8"
    
    return {
        "signal": signal,
        "signal_color": signal_color,
        "score": score,
        "details": details,
        "rsi": latest['RSI']
    }

# ============================================================================
# مكونات التصور المتقدمة
# ============================================================================

def create_price_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """إنشاء رسم بياني متقدم للأسعار"""
    
    fig = go.Figure()
    
    # إضافة الشموع اليابانية
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="السعر",
        showlegend=True
    ))
    
    # إضافة المتوسطات المتحركة
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA20'],
        name="MA 20",
        line=dict(color='#f59e0b', width=1.5, dash='solid'),
        opacity=0.8
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA50'],
        name="MA 50",
        line=dict(color='#10b981', width=1.5, dash='solid'),
        opacity=0.8
    ))
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_upper'],
        name="BB علوي",
        line=dict(color='#94a3b8', width=1, dash='dash'),
        opacity=0.5
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_lower'],
        name="BB سفلي",
        line=dict(color='#94a3b8', width=1, dash='dash'),
        opacity=0.5,
        fill='tonexty',
        fillcolor='rgba(148, 163, 184, 0.1)'
    ))
    
    # تحسين التصميم
    fig.update_layout(
        title=dict(
            text=f"📈 التحليل الفني لسهم {ticker}",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#f1f5f9')
        ),
        template="plotly_dark",
        height=550,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor='rgba(15, 23, 42, 0.9)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        xaxis=dict(
            title="التاريخ",
            gridcolor='rgba(51, 65, 85, 0.5)',
            showgrid=True
        ),
        yaxis=dict(
            title="السعر",
            gridcolor='rgba(51, 65, 85, 0.5)',
            showgrid=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(15, 23, 42, 0.8)'
        )
    )
    
    return fig

def create_volume_chart(df: pd.DataFrame) -> go.Figure:
    """إنشاء رسم بياني لحجم التداول"""
    
    # تلوين الأعمدة حسب ارتفاع/انخفاض السعر
    colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
              for i in range(len(df))]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name="حجم التداول",
        marker_color=colors,
        opacity=0.7
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Volume_MA'],
        name="المتوسط المتحرك",
        line=dict(color='#3b82f6', width=2, dash='solid')
    ))
    
    fig.update_layout(
        title=dict(
            text="📊 حجم التداول اليومي",
            x=0.5,
            font=dict(size=16, color='#f1f5f9')
        ),
        template="plotly_dark",
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(15, 23, 42, 0.9)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        xaxis_title="التاريخ",
        yaxis_title="الحجم",
        showlegend=True
    )
    
    return fig

def create_rsi_chart(df: pd.DataFrame) -> go.Figure:
    """إنشاء رسم بياني لـ RSI"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        name="RSI",
        line=dict(color='#8b5cf6', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.1)'
    ))
    
    # مناطق الذروة
    fig.add_hrect(
        y0=70, y1=100,
        fillcolor="#ef4444", opacity=0.2,
        line_width=0,
        annotation_text="منطقة ذروة شراء",
        annotation_position="top left"
    )
    
    fig.add_hrect(
        y0=0, y1=30,
        fillcolor="#10b981", opacity=0.2,
        line_width=0,
        annotation_text="منطقة ذروة بيع",
        annotation_position="bottom left"
    )
    
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", opacity=0.5)
    
    fig.update_layout(
        title=dict(
            text="📊 مؤشر القوة النسبية (RSI)",
            x=0.5,
            font=dict(size=16, color='#f1f5f9')
        ),
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(15, 23, 42, 0.9)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        yaxis=dict(range=[0, 100], title="RSI"),
        xaxis_title="التاريخ",
        showlegend=False
    )
    
    return fig

def create_macd_chart(df: pd.DataFrame) -> go.Figure:
    """إنشاء رسم بياني لـ MACD"""
    
    fig = go.Figure()
    
    # الهيستوجرام
    colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['MACD_histogram']]
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['MACD_histogram'],
        name="MACD Histogram",
        marker_color=colors,
        opacity=0.7
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD'],
        name="MACD",
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['MACD_signal'],
        name="Signal",
        line=dict(color='#f59e0b', width=2)
    ))
    
    fig.update_layout(
        title=dict(
            text="📊 مؤشر MACD",
            x=0.5,
            font=dict(size=16, color='#f1f5f9')
        ),
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(15, 23, 42, 0.9)',
        paper_bgcolor='rgba(15, 23, 42, 0)',
        xaxis_title="التاريخ",
        yaxis_title="القيمة",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    return fig

# ============================================================================
# الواجهة الرئيسية
# ============================================================================

def render_sidebar() -> str:
    """عرض الشريط الجانبي وإرجاع رمز السهم"""
    
    with st.sidebar:
        # الشعار والترحيب
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 28px; background: linear-gradient(135deg, #2563eb, #7c3aed); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                📊 المحلل المصري
            </h1>
            <p style="color: #94a3b8; font-size: 14px;">النسخة المتطورة 3.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # اختيار السهم
        st.markdown("#### 🔍 اختيار السهم")
        
        selected_stock = st.selectbox(
            "من القائمة المنسدلة:",
            options=list(STOCKS_DATABASE.keys()),
            label_visibility="collapsed"
        )
        
        custom_ticker = st.text_input(
            "أو أدخل الرمز يدوياً:",
            placeholder="مثال: AAPL, TSLA, 2222.SR",
            key="custom_ticker_input"
        )
        
        if custom_ticker and custom_ticker.strip():
            ticker = custom_ticker.strip().upper()
        else:
            ticker = STOCKS_DATABASE[selected_stock]
        
        st.info(f"📌 الرمز الحالي: `{ticker}`")
        
        st.markdown("---")
        
        # معلومات إضافية
        st.markdown("#### ℹ️ معلومات")
        st.caption(f"🕐 تحديث تلقائي كل {config.update_interval} دقيقة")
        st.caption(f"📊 مصدر البيانات: Yahoo Finance")
        st.caption(f"⚡ الإصدار: {config.version}")
        
        st.markdown("---")
        
        # زر التحديث
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # نصائح سريعة
        with st.expander("💡 نصائح سريعة"):
            st.markdown("""
            - **RSI < 30**: منطقة شراء محتملة
            - **RSI > 70**: منطقة بيع محتملة
            - **المتوسطات المتحركة**: تأكيد الاتجاه
            - **MACD**: إشارات الانعكاس
            """)
    
    return ticker

def render_metrics(df: pd.DataFrame, signal_data: Dict):
    """عرض بطاقات المؤشرات"""
    
    if df.empty:
        return
    
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume'].mean()
    volume_ratio = (current_volume / avg_volume) * 100 if avg_volume > 0 else 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 السعر الحالي",
            value=f"{current_price:.2f}",
            delta=f"{price_change:+.2f}%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="📊 مؤشر RSI",
            value=f"{signal_data['rsi']:.1f}",
            help="مؤشر القوة النسبية (0-100)"
        )
    
    with col3:
        st.metric(
            label="📈 حجم التداول",
            value=f"{current_volume/1000000:.1f}M",
            delta=f"{volume_ratio:.0f}% من المتوسط"
        )
    
    with col4:
        change_20 = ((current_price - df['MA20'].iloc[-1]) / df['MA20'].iloc[-1]) * 100
        st.metric(
            label="📉 المتوسط المتحرك 20",
            value=f"{df['MA20'].iloc[-1]:.2f}",
            delta=f"{change_20:+.2f}%"
        )

def render_signal_card(signal_data: Dict):
    """عرض بطاقة الإشارة بشكل جذاب"""
    
    st.markdown(f"""
    <div class="signal-card">
        <h3 style="color: {signal_data['signal_color']}; margin: 0 0 10px 0;">
            {signal_data['signal']}
        </h3>
        <p style="color: #94a3b8; margin: 0;">
            درجة الإشارة: {signal_data['score']}/3
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 تفاصيل الإشارات", expanded=False):
        for detail in signal_data['details']:
            st.markdown(f"- {detail}")

def render_main_interface(ticker: str):
    """عرض الواجهة الرئيسية للتطبيق"""
    
    # عنوان رئيسي متحرك
    st.markdown(f'<h1 class="main-header">📊 تحليل سهم {ticker}</h1>', unsafe_allow_html=True)
    
    # جلب البيانات
    with st.spinner("🔄 جاري تحليل البيانات..."):
        df, dividends, info = fetch_market_data(ticker)
    
    if df is None or df.empty:
        st.error("❌ لا يمكن جلب البيانات")
        st.markdown("""
        <div class="warning-text">
            ⚠️ تأكد من صحة رمز السهم وحاول مرة أخرى<br>
            💡 مثال: AAPL, TSLA, 2222.SR, COMI.CA
        </div>
        """, unsafe_allow_html=True)
        return
    
    # تحليل الإشارات
    signal_data = analyze_signal(df)
    
    # عرض المؤشرات السريعة
    render_metrics(df, signal_data)
    
    # عرض بطاقة الإشارة
    render_signal_card(signal_data)
    
    st.markdown("---")
    
    # التبويبات الرئيسية
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 التحليل الفني",
        "📊 المؤشرات المتقدمة",
        "💰 التوزيعات",
        "ℹ️ معلومات الشركة"
    ])
    
    with tab1:
        # الرسم البياني الرئيسي
        price_chart = create_price_chart(df, ticker)
        st.plotly_chart(price_chart, use_container_width=True, key="price_chart_main")
        
        # رسم حجم التداول
        volume_chart = create_volume_chart(df)
        st.plotly_chart(volume_chart, use_container_width=True, key="volume_chart_main")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            rsi_chart = create_rsi_chart(df)
            st.plotly_chart(rsi_chart, use_container_width=True, key="rsi_chart_main")
        
        with col2:
            macd_chart = create_macd_chart(df)
            st.plotly_chart(macd_chart, use_container_width=True, key="macd_chart_main")
        
        # جدول المؤشرات الحالية
        st.markdown("---")
        st.markdown("#### 📋 المؤشرات الحالية")
        
        latest = df.iloc[-1]
        indicators_data = {
            "المؤشر": ["السعر", "MA20", "MA50", "RSI", "MACD", "MACD Signal"],
            "القيمة": [
                f"{latest['Close']:.2f}",
                f"{latest['MA20']:.2f}",
                f"{latest['MA50']:.2f}",
                f"{latest['RSI']:.1f}",
                f"{latest['MACD']:.3f}",
                f"{latest['MACD_signal']:.3f}"
            ]
        }
        indicators_df = pd.DataFrame(indicators_data)
        st.dataframe(indicators_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("#### 💰 تاريخ توزيعات الأرباح")
        
        if not dividends.empty:
            # عرض جدول التوزيعات
            div_data = []
            for date, amount in dividends.tail(10).items():
                div_data.append({
                    "التاريخ": date.strftime('%Y-%m-%d'),
                    "القيمة": f"{amount:.3f}"
                })
            
            st.table(pd.DataFrame(div_data))
            
            # إحصائيات
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي التوزيعات", f"{dividends.sum():.3f}")
            with col2:
                st.metric("متوسط التوزيع", f"{dividends.mean():.3f}")
            with col3:
                st.metric("عدد التوزيعات", len(dividends))
        else:
            st.info("📭 لا توجد بيانات توزيعات أرباح متاحة لهذا السهم")
    
    with tab4:
        st.markdown("#### ℹ️ معلومات الشركة")
        
        if info:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🏢 الاسم:** {info.get('longName', 'غير متوفر')}")
                st.markdown(f"**🏭 القطاع:** {info.get('sector', 'غير متوفر')}")
                st.markdown(f"**📋 الصناعة:** {info.get('industry', 'غير متوفر')}")
                st.markdown(f"**🌍 الدولة:** {info.get('country', 'غير متوفر')}")
            
            with col2:
                if info.get('marketCap'):
                    st.markdown(f"**💰 القيمة السوقية:** ${info.get('marketCap', 0):,}")
                if info.get('trailingPE'):
                    st.markdown(f"**📊 نسبة السعر للربح:** {info.get('trailingPE', 'غير متوفر')}")
                if info.get('dividendYield'):
                    st.markdown(f"**💵 عائد التوزيعات:** {info.get('dividendYield', 0)*100:.2f}%")
                if info.get('beta'):
                    st.markdown(f"**📈 معامل بيتا:** {info.get('beta', 'غير متوفر')}")
        else:
            st.info("📭 معلومات الشركة غير متوفرة حالياً")

# ============================================================================
# تشغيل التطبيق
# ============================================================================

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    
    # عرض الشريط الجانبي والحصول على رمز السهم
    ticker = render_sidebar()
    
    # عرض الواجهة الرئيسية
    render_main_interface(ticker)
    
    # تذييل الصفحة
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 12px; margin-top: 20px;">
        ⚠️ <strong>تنويه مهم:</strong> هذا التحليل لأغراض تعليمية وتدريبية فقط<br>
        وليس توصية استثمارية. يُنصح بالتشاور مع مستشار مالي معتمد قبل اتخاذ أي قرارات استثمارية.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
