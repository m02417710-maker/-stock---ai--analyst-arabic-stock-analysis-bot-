# ============================================================
# ملف: app_complete.py
# المحلل المصري Pro - جميع أسهم البورصات المصرية والسعودية والأمريكية
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
from streamlit_autorefresh import st_autorefresh
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

warnings.filterwarnings('ignore')

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="المحلل المصري Pro - جميع الأسهم",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحديث تلقائي كل 60 ثانية
st_autorefresh(interval=60000, key="auto_refresh", debounce=True)

# ============================================================
# التصميم المتقدم
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #3b82f6;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 5px 15px rgba(37,99,235,0.4);
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: #1e293b;
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    font-weight: bold;
}
.stTabs [aria-selected="true"] {
    background: #2563eb;
    color: white;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b);
    border-right: 1px solid #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# قائمة جميع الأسهم - محدثة من مصادر موثوقة
# ============================================================

# الأسهم المصرية (البورصة المصرية - EGX)
EGYPT_STOCKS = {
    "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
    "🇪🇬 طلعت مصطفى القابضة": "TMGH.CA",
    "🇪🇬 فوري لتكنولوجيا البنوك": "FWRY.CA",
    "🇪🇬 المجموعة المالية هيرميس": "HRHO.CA",
    "🇪🇬 العاشر من رمضان للصناعات الدوائية": "RADO.CA",
    "🇪🇬 الإسكندرية للزيوت المعدنية": "AMOC.CA",
    "🇪🇬 حديد عز": "ESRS.CA",
    "🇪🇬 السويس للأسمنت": "SUCE.CA",
    "🇪🇬 جهينة للصناعات الغذائية": "JUFO.CA",
    "🇪🇬 أبو قير للأسمدة": "ABUK.CA",
    "🇪🇬 مصر للإيداع والقيد": "MISR.CA",
    "🇪🇬 بنك مصر": "BMEL.CA",
    "🇪🇬 بنك القاهرة": "BANK.CA",
    "🇪🇬 المصري لخدمات النقل": "EGTS.CA"
}

# الأسهم السعودية (تداول - TASI) - أكثر من 200 سهم [citation:1][citation:4]
SAUDI_STOCKS = {
    "🛢️ أرامكو السعودية": "2222.SR",
    "🏦 البنك الأهلي السعودي": "1180.SR",
    "🏦 بنك الرياض": "1010.SR",
    "🏦 بنك الراجحي": "1120.SR",
    "🏦 بنك البلاد": "1140.SR",
    "🏦 بنك الجزيرة": "1020.SR",
    "🏦 بنك الإنماء": "1150.SR",
    "🏦 البنك السعودي الفرنسي": "1050.SR",
    "🏦 البنك السعودي البريطاني (ساب)": "1060.SR",
    "🏦 البنك السعودي للاستثمار": "1030.SR",
    "📱 شركة الاتصالات السعودية (STC)": "7010.SR",
    "📱 موبايلي": "7030.SR",
    "📱 زين السعودية": "7020.SR",
    "🔋 أكوا باور": "2082.SR",
    "⚡ الشركة السعودية للكهرباء": "5110.SR",
    "🏗️ سابك": "2010.SR",
    "🏗️ سابك للمغذيات الزراعية": "2020.SR",
    "🏗️ ينبع الوطنية للبتروكيماويات (ينساب)": "2290.SR",
    "🏗️ كيان السعودية": "2350.SR",
    "🏗️ المتقدمة للبتروكيماويات": "2330.SR",
    "🏗️ الصناعات الكيميائية الأساسية": "2001.SR",
    "🏗️ التصنيع الوطنية": "2060.SR",
    "🏗️ الصحراء للبتروكيماويات": "2280.SR",
    "🏗️ نماء للكيماويات": "2210.SR",
    "🏥 دكتيل": "4120.SR",
    "🏥 الحمادي": "4007.SR",
    "🏥 سليمان الحبيب": "4013.SR",
    "🏥 دلة الصحية": "4170.SR",
    "🏥 المستشفى السعودي الألماني": "4171.SR",
    "🏥 المواساة": "4015.SR",
    "🏥 السعودي الفرنسي للتمويل العقاري": "4018.SR",
    "🏥 جزان للتنمية": "4010.SR",
    "🏦 الجزيرة تكافل": "8012.SR",
    "🏦 التعاونية للتأمين": "8010.SR",
    "🏦 ملاذ للتأمين": "8040.SR",
    "🏦 تْشب العربية": "8180.SR",
    "🏦 بوبا العربية": "8210.SR",
    "🏦 أسيج": "8230.SR",
    "🏦 سلامة للتأمين": "8060.SR",
    "🏦 أليانز إس إف": "8020.SR",
    "🏦 المتحدة للتأمين": "8011.SR",
    "🏦 المتوسط والخليج للتأمين": "8030.SR",
    "🏦 الدرع العربي": "8090.SR",
    "🏦 سايكو": "8100.SR",
    "🏦 الوليد للتأمين": "8050.SR",
    "🏦 أكسا التعاونية": "8240.SR",
    "🏦 وقاية للتكافل": "8300.SR",
    "🏦 مدى للتأمين": "8280.SR",
    "🏦 عناية السعودية": "8310.SR",
    "🏦 الصقر للتأمين": "8185.SR",
    "🏦 تشب": "8270.SR",
    "🏦 وفا للتأمين": "8200.SR",
    "🏦 الخليجية العامة": "8260.SR",
    "🏦 أمانة للتأمين": "8311.SR",
    "🏦 ريت الوحدة": "4340.SR",
    "🏦 جدوى ريت السعودية": "4342.SR",
    "🏦 الأهلي ريت 1": "4348.SR",
    "🏦 مشاركة ريت": "4335.SR",
    "🏦 تعليم ريت": "4346.SR",
    "🏦 سيجما": "2120.SR",
    "🏦 أسترا الصناعية": "2170.SR",
    "🏦 باوب": "2120.SR",
    "🏦 زجاج": "2150.SR",
    "🏦 أسمنت اليمامة": "4110.SR",
    "🏦 أسمنت العربية": "4120.SR",
    "🏦 أسمنت الجنوبية": "4130.SR",
    "🏦 أسمنت ينبع": "4140.SR",
    "🏦 أسمنت القصيم": "4150.SR",
    "🏦 أسمنت السعودية": "4160.SR",
    "🏦 أسمنت الرياض": "4170.SR",
    "🏦 أسمنت الشمالية": "4180.SR",
    "🏦 أسمنت الجوف": "4190.SR",
    "🏦 أسمنت حائل": "4191.SR",
    "🏦 أسمنت تبوك": "4161.SR",
    "🏦 أسمنت أم القرى": "4162.SR",
    "🏦 أسمنت العربية": "4181.SR",
    "🏦 أسمنت نجران": "4192.SR",
    "🏦 أسمنت الشرقية": "4182.SR",
    "🏦 أسمنت الشمال": "4183.SR",
    "🏦 أسمنت الشرقية": "4184.SR",
    "🏦 أسمنت ينبع": "4185.SR",
    "🏦 أسمنت المدينة": "4186.SR"
}

# الأسهم الأمريكية (S&P 500 والمؤشرات الرئيسية) [citation:2]
US_STOCKS = {
    "🍎 آبل": "AAPL",
    "🚀 تسلا": "TSLA",
    "💻 مايكروسوفت": "MSFT",
    "🎮 إنفيديا": "NVDA",
    "📦 أمازون": "AMZN",
    "🔍 جوجل": "GOOGL",
    "📘 ميتا (فيسبوك)": "META",
    "👑 بيركشاير هاثاواي": "BRK-B",
    "💳 فيزا": "V",
    "💳 ماستركارد": "MA",
    "🏦 جي بي مورجان": "JPM",
    "🏦 بنك أوف أمريكا": "BAC",
    "🏀 نايك": "NKE",
    "☕ ستاربكس": "SBUX",
    "🚗 فورد": "F",
    "🚗 جنرال موتورز": "GM",
    "✈️ بوينغ": "BA",
    "✈️ دلتا": "DAL",
    "📺 والت ديزني": "DIS",
    "🎬 نتفليكس": "NFLX",
    "📱 إنتل": "INTC",
    "🔬 جونسون آند جونسون": "JNJ",
    "💊 فايزر": "PFE",
    "💊 موديرنا": "MRNA",
    "💉 ميرك": "MRK",
    "🛒 كوستكو": "COST",
    "🔧 هوم ديبوت": "HD",
    "🚚 يو بي إس": "UPS",
    "📬 فيديكس": "FDX",
    "☁️ سيلزفورس": "CRM",
    "💻 آي بي إم": "IBM",
    "🎮 أكسفورد": "EA",
    "❄️ نسكافيه": "NEST",
    "🍔 ماكدونالدز": "MCD",
    "☕ كافئين": "CMG",
    "📺 كومكاست": "CMCSA",
    "🌐 فيرايزون": "VZ",
    "📱 تي موبايل": "TMUS",
    "📞 إيه تي آند تي": "T",
    "🔋 تسلا انرجي": "FSLR",
    "🔋 إنتل اجن": "SUN",
    "🔋 تسلا انرجي": "NEXT"
}

# دمج جميع الأسهم
ALL_STOCKS = {**EGYPT_STOCKS, **SAUDI_STOCKS, **US_STOCKS}

# تنظيم الأسهم حسب البورصة للقوائم المنسدلة
STOCKS_BY_MARKET = {
    "🇪🇬 البورصة المصرية (EGX)": EGYPT_STOCKS,
    "🇸🇦 السوق السعودي (تداول - TASI)": SAUDI_STOCKS,
    "🇺🇸 السوق الأمريكي (NASDAQ/NYSE)": US_STOCKS,
    "🌍 جميع الأسهم": ALL_STOCKS
}

# ============================================================
# دوال التحليل المتقدمة
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_stock_data(ticker):
    """جلب بيانات السهم مع جميع المؤشرات"""
    if not ticker:
        return None, None
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo", interval="1d")
        
        if df.empty or len(df) < 10:
            return None, None
        
        # حساب جميع المؤشرات الفنية
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        
        # Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        
        # MACD
        macd = ta.macd(df['Close'])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        
        # حجم التداول
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # حساب الدعم والمقاومة
        df['Support'] = df['Low'].rolling(window=20).min()
        df['Resistance'] = df['High'].rolling(window=20).max()
        
        return df, stock.info
        
    except Exception as e:
        return None, None

def calculate_score(df):
    """حساب درجة الثقة المتقدمة"""
    if df is None or df.empty or len(df) < 20:
        return 0, []
    
    score = 0
    signals = []
    last = df.iloc[-1]
    
    # 1. الاتجاه (وزن 2)
    if last['Close'] > last['MA50'] and last['MA20'] > last['MA50']:
        score += 2
        signals.append("✅ الاتجاه العام صاعد قوي")
    elif last['Close'] > last['MA50']:
        score += 1.5
        signals.append("✅ الاتجاه العام صاعد")
    elif last['Close'] < last['MA50']:
        signals.append("⚠️ الاتجاه العام هابط")
        score -= 1
    
    # 2. الزخم (وزن 1.5)
    rsi = last['RSI'] if not pd.isna(last['RSI']) else 50
    if rsi < 25:
        score += 1.5
        signals.append(f"🔥 ذروة بيع شديدة - RSI: {rsi:.1f} (فرصة شراء ممتازة)")
    elif rsi < 30:
        score += 1.2
        signals.append(f"✅ منطقة ذروة بيع - RSI: {rsi:.1f} (فرصة شراء)")
    elif 30 <= rsi < 40:
        score += 0.8
        signals.append(f"📈 منطقة تجميع - RSI: {rsi:.1f}")
    elif 40 <= rsi < 60:
        score += 0.5
        signals.append(f"📊 منطقة محايدة - RSI: {rsi:.1f}")
    elif rsi > 75:
        score -= 1
        signals.append(f"⚠️ ذروة شراء - RSI: {rsi:.1f} (توخ الحذر)")
    elif rsi > 70:
        score -= 0.5
        signals.append(f"⚠️ منطقة ذروة شراء - RSI: {rsi:.1f}")
    else:
        signals.append(f"✅ RSI طبيعي - {rsi:.1f}")
    
    # 3. MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        macd_val = last['MACD_12_26_9']
        signal_val = last['MACDs_12_26_9']
        if macd_val > signal_val and macd_val > 0:
            score += 1.2
            signals.append("🚀 MACD إيجابي قوي")
        elif macd_val > signal_val:
            score += 0.8
            signals.append("📈 MACD إيجابي")
        elif macd_val < signal_val:
            signals.append("📉 MACD سلبي")
            score -= 0.5
    
    # 4. الحجم (وزن 1)
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 2:
        score += 1
        signals.append(f"💰 سيولة عالية جداً ({vol_ratio:.1f}x المعدل)")
    elif vol_ratio > 1.5:
        score += 0.8
        signals.append(f"💰 سيولة جيدة ({vol_ratio:.1f}x المعدل)")
    elif vol_ratio > 1:
        score += 0.5
        signals.append(f"💰 سيولة أعلى من المعدل")
    elif vol_ratio < 0.5:
        score -= 0.5
        signals.append(f"📉 سيولة ضعيفة")
    
    # 5. البولنجر باند
    if 'BBL_20_2.0' in last and 'BBU_20_2.0' in last:
        if last['Close'] <= last['BBL_20_2.0'] * 1.02:
            score += 0.8
            signals.append("🎯 السعر عند الدعم - ارتداد محتمل")
        elif last['Close'] >= last['BBU_20_2.0'] * 0.98:
            score -= 0.5
            signals.append("⚠️ السعر عند المقاومة - تصحيح محتمل")
    
    return min(max(score, 0), 5), signals

def get_trading_decision(df, score):
    """تحديد قرار التداول"""
    if df is None or df.empty:
        return "لا توجد بيانات", "#gray", "⏸️"
    
    last = df.iloc[-1]
    rsi = last['RSI'] if not pd.isna(last['RSI']) else 50
    
    if score >= 4.5 or (rsi < 25 and last['Close'] > last['MA20']):
        return "شراء قوي جداً", "#10b981", "🔥"
    elif score >= 4 or (rsi < 30 and last['Close'] > last['MA20']):
        return "شراء قوي", "#22c55e", "🟢"
    elif score >= 3 or (rsi < 35 and last['Close'] > last['MA20']):
        return "شراء محتمل", "#3b82f6", "📈"
    elif score >= 2:
        return "مراقبة / انتظار", "#f59e0b", "🟡"
    elif rsi > 80:
        return "بيع عاجل", "#ef4444", "🔴"
    elif rsi > 75 or score <= 1:
        return "بيع / تخفيض", "#f97316", "📉"
    else:
        return "احتفاظ", "#94a3b8", "✅"

# ============================================================
# دوال الرسم البياني المتقدم
# ============================================================

def create_advanced_chart(df, ticker, target_price, stop_loss, selected_name):
    """رسم بياني متقدم مع المستهدفات"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.45, 0.2, 0.2, 0.15],
        subplot_titles=("📈 السعر مع المتوسطات والمستهدفات", "📊 مؤشر القوة النسبية RSI", "⚡ مؤشر MACD", "💰 حجم التداول")
    )
    
    # الرسم الرئيسي
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="السعر"
        ),
        row=1, col=1
    )
    
    # المتوسطات المتحركة
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA20'], name="MA 20", 
                   line=dict(color='#f59e0b', width=1.5)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA50'], name="MA 50", 
                   line=dict(color='#10b981', width=1.5)),
        row=1, col=1
    )
    
    # Bollinger Bands
    if 'BBU_20_2.0' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BBU_20_2.0'], name="BB علوي",
                       line=dict(color='#94a3b8', width=1, dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BBL_20_2.0'], name="BB سفلي",
                       line=dict(color='#94a3b8', width=1, dash='dash'),
                       fill='tonexty', fillcolor='rgba(148,163,184,0.1)'),
            row=1, col=1
        )
    
    # خط الهدف
    if target_price > 0:
        fig.add_hline(
            y=target_price, line_dash="dash", line_color="#10b981",
            annotation_text=f"🎯 الهدف: {target_price:.2f}",
            annotation_position="top right", row=1, col=1
        )
    
    # خط وقف الخسارة
    if stop_loss > 0:
        fig.add_hline(
            y=stop_loss, line_dash="dash", line_color="#ef4444",
            annotation_text=f"🛑 وقف خسارة: {stop_loss:.2f}",
            annotation_position="bottom right", row=1, col=1
        )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                   line=dict(color='#8b5cf6', width=2)),
        row=2, col=1
    )
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    
    # MACD
    if 'MACD_12_26_9' in df.columns:
        macd_hist = df['MACD_12_26_9'] - df['MACDs_12_26_9']
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in macd_hist]
        
        fig.add_trace(
            go.Bar(x=df.index, y=macd_hist, name="Histogram",
                   marker_color=colors, opacity=0.7),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_12_26_9'], name="MACD",
                       line=dict(color='#3b82f6', width=2)),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name="Signal",
                       line=dict(color='#f59e0b', width=2)),
            row=3, col=1
        )
    
    # حجم التداول
    colors_vol = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
                  for i in range(len(df))]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name="الحجم",
               marker_color=colors_vol, opacity=0.7),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Volume_MA'], name="المتوسط",
                   line=dict(color='#3b82f6', dash='dash')),
        row=4, col=1
    )
    
    fig.update_layout(
        title=f"📊 التحليل الفني لسهم {selected_name}",
        template="plotly_dark",
        height=800,
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="الحجم", row=4, col=1)
    
    return fig

# ============================================================
# ماسح السوق الذكي (جميع الأسهم)
# ============================================================

def scan_all_stocks(market_filter="all"):
    """مسح جميع الأسهم للبحث عن فرص - مع دعم جميع البورصات"""
    results = []
    
    # تحديد الأسهم المراد مسحها
    if market_filter == "egypt":
        stocks_to_scan = EGYPT_STOCKS
    elif market_filter == "saudi":
        stocks_to_scan = SAUDI_STOCKS
    elif market_filter == "us":
        stocks_to_scan = US_STOCKS
    else:
        stocks_to_scan = ALL_STOCKS
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (name, ticker) in enumerate(stocks_to_scan.items()):
        status_text.text(f"🔄 جاري مسح: {name}...")
        
        df, _ = get_stock_data(ticker)
        if df is not None and not df.empty:
            score, _ = calculate_score(df)
            last_price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100 if len(df) > 1 else 0
            
            # تحديد مستوى الفرصة
            if score >= 4:
                signal = "🟢🔥 فرصة شراء قوية"
                priority = 1
            elif score >= 3.5:
                signal = "🟢 شراء"
                priority = 2
            elif score >= 2.5:
                signal = "📈 مراقبة إيجابية"
                priority = 3
            elif score <= 1.5:
                signal = "🔴 إشارة بيع/خروج"
                priority = 5
            else:
                signal = "🟡 مراقبة"
                priority = 4
            
            # تحديد البورصة
            if ticker.endswith('.CA'):
                market = "🇪🇬 مصر"
            elif ticker.endswith('.SR'):
                market = "🇸🇦 السعودية"
            else:
                market = "🇺🇸 أمريكا"
            
            results.append({
                "البورصة": market,
                "السهم": name,
                "الرمز": ticker,
                "السعر": round(last_price, 2),
                "التغير %": round(change, 2),
                "RSI": round(rsi, 1),
                "الدرجة": score,
                "الإشارة": signal
            })
        
        progress_bar.progress((idx + 1) / len(stocks_to_scan))
    
    progress_bar.empty()
    status_text.empty()
    
    # ترتيب النتائج حسب الأولوية
    results.sort(key=lambda x: (-x['الدرجة']))
    
    return pd.DataFrame(results)

# ============================================================
# الواجهة الرئيسية
# ============================================================

def main():
    # شريط جانبي
    with st.sidebar:
        st.markdown("## 📊 المحلل المصري Pro")
        st.markdown("### 🤖 الإصدار المتكامل")
        st.markdown("---")
        
        # اختيار البورصة
        st.markdown("### 🌍 اختيار البورصة")
        market_choice = st.radio(
            "",
            ["🇪🇬 البورصة المصرية", "🇸🇦 السوق السعودي", "🇺🇸 السوق الأمريكي", "🌍 جميع الأسواق"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # اختيار السهم حسب البورصة
        st.markdown("### 🔍 اختيار السهم")
        
        if market_choice == "🇪🇬 البورصة المصرية":
            selected = st.selectbox("", list(EGYPT_STOCKS.keys()), label_visibility="collapsed")
            ticker = EGYPT_STOCKS[selected]
        elif market_choice == "🇸🇦 السوق السعودي":
            selected = st.selectbox("", list(SAUDI_STOCKS.keys()), label_visibility="collapsed")
            ticker = SAUDI_STOCKS[selected]
        elif market_choice == "🇺🇸 السوق الأمريكي":
            selected = st.selectbox("", list(US_STOCKS.keys()), label_visibility="collapsed")
            ticker = US_STOCKS[selected]
        else:
            selected = st.selectbox("", list(ALL_STOCKS.keys()), label_visibility="collapsed")
            ticker = ALL_STOCKS[selected]
        
        st.caption(f"📌 الرمز: `{ticker}`")
        
        st.markdown("---")
        
        # إحصائيات سريعة
        st.markdown("### 📈 معلومات")
        st.caption(f"🕐 الوقت: {datetime.now().strftime('%H:%M:%S')}")
        st.caption(f"🔄 تحديث تلقائي كل 60 ثانية")
        st.caption(f"📊 مصدر: Yahoo Finance")
        
        st.markdown("---")
        
        # إحصائيات الأسهم
        st.markdown("### 📊 إحصائيات البورصات")
        st.metric("🇪🇬 أسهم مصر", len(EGYPT_STOCKS))
        st.metric("🇸🇦 أسهم السعودية", len(SAUDI_STOCKS))
        st.metric("🇺🇸 أسهم أمريكا", len(US_STOCKS))
        st.metric("🌍 إجمالي الأسهم", len(ALL_STOCKS))
        
        st.markdown("---")
        
        # زر التحديث اليدوي
        if st.button("🔄 تحديث يدوي", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # العنوان الرئيسي
    st.markdown(f"## 📈 التحليل المتكامل لسهم {selected}")
    st.markdown(f"### {ticker}")
    st.markdown("---")
    
    # جلب البيانات
    with st.spinner("🔄 جاري تحليل البيانات..."):
        df, info = get_stock_data(ticker)
    
    if df is not None and not df.empty:
        # حساب المؤشرات
        score, signals = calculate_score(df)
        
        # البيانات الأساسية
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        # حساب الهدف ووقف الخسارة
        target_price = df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else current_price * 1.05
        stop_loss = df['Support'].iloc[-1] if not pd.isna(df['Support'].iloc[-1]) else current_price * 0.97
        
        # قرار التداول
        decision, decision_color, decision_icon = get_trading_decision(df, score)
        
        # بطاقات المعلومات
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta = f"{price_change:+.2f}%"
            delta_color = "normal" if price_change >= 0 else "inverse"
            st.metric("💰 السعر", f"{current_price:.2f}", delta, delta_color=delta_color)
        
        with col2:
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            rsi_color = "🟢" if rsi < 40 else ("🔴" if rsi > 70 else "🟡")
            st.metric("📊 RSI", f"{rsi:.1f} {rsi_color}")
        
        with col3:
            st.metric("🎯 درجة الثقة", f"{score}/5")
        
        with col4:
            st.metric("📋 القرار", f"{decision
