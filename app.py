# ============================================================
# ملف: app_ultimate.py
# المحلل المصري Pro - الإصدار النهائي المتكامل مع جميع الأسهم
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
from streamlit_autorefresh import st_autorefresh
import requests
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
# جميع أسهم البورصات (محدثة)
# ============================================================

# الأسهم المصرية (EGX)
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
    "🇪🇬 بنك مصر": "BMEL.CA",
    "🇪🇬 المصرية للاتصالات": "ETEL.CA",
    "🇪🇬 الإسكندرية للأدوية": "AXPH.CA",
    "🇪🇬 جنوب الوادي للأسمنت": "SVCE.CA"
}

# الأسهم السعودية (تداول)
SAUDI_STOCKS = {
    "🇸🇦 أرامكو السعودية": "2222.SR",
    "🇸🇦 البنك الأهلي السعودي": "1180.SR",
    "🇸🇦 بنك الرياض": "1010.SR",
    "🇸🇦 بنك الراجحي": "1120.SR",
    "🇸🇦 بنك البلاد": "1140.SR",
    "🇸🇦 بنك الجزيرة": "1020.SR",
    "🇸🇦 بنك الإنماء": "1150.SR",
    "🇸🇦 الاتصالات السعودية (STC)": "7010.SR",
    "🇸🇦 موبايلي": "7030.SR",
    "🇸🇦 زين السعودية": "7020.SR",
    "🇸🇦 سابك": "2010.SR",
    "🇸🇦 الشركة السعودية للكهرباء": "5110.SR",
    "🇸🇦 أكوا باور": "2082.SR",
    "🇸🇦 سليمان الحبيب": "4013.SR",
    "🇸🇦 الحمادي": "4007.SR",
    "🇸🇦 دلة الصحية": "4170.SR",
    "🇸🇦 المواساة": "4015.SR",
    "🇸🇦 التعاونية للتأمين": "8010.SR",
    "🇸🇦 الراجحي للتأمين": "8230.SR",
    "🇸🇦 بوبا العربية": "8210.SR"
}

# الأسهم الأمريكية (NASDAQ & NYSE)
US_STOCKS = {
    "🇺🇸 آبل - Apple": "AAPL",
    "🇺🇸 تسلا - Tesla": "TSLA",
    "🇺🇸 مايكروسوفت - Microsoft": "MSFT",
    "🇺🇸 إنفيديا - NVIDIA": "NVDA",
    "🇺🇸 أمازون - Amazon": "AMZN",
    "🇺🇸 جوجل - Google": "GOOGL",
    "🇺🇸 ميتا - Meta": "META",
    "🇺🇸 بيركشاير هاثاواي": "BRK-B",
    "🇺🇸 فيزا - Visa": "V",
    "🇺🇸 ماستركارد - Mastercard": "MA",
    "🇺🇸 جي بي مورجان": "JPM",
    "🇺🇸 بنك أوف أمريكا": "BAC",
    "🇺🇸 نايك - Nike": "NKE",
    "🇺🇸 ستاربكس - Starbucks": "SBUX",
    "🇺🇸 فورد - Ford": "F",
    "🇺🇸 بوينغ - Boeing": "BA",
    "🇺🇸 ديزني - Disney": "DIS",
    "🇺🇸 نتفليكس - Netflix": "NFLX",
    "🇺🇸 إنتل - Intel": "INTC",
    "🇺🇸 جونسون آند جونسون": "JNJ",
    "🇺🇸 فايزر - Pfizer": "PFE",
    "🇺🇸 موديرنا - Moderna": "MRNA",
    "🇺🇸 كوستكو - Costco": "COST",
    "🇺🇸 هوم ديبوت": "HD",
    "🇺🇸 يو بي إس - UPS": "UPS",
    "🇺🇸 سيلزفورس - Salesforce": "CRM",
    "🇺🇸 آي بي إم - IBM": "IBM",
    "🇺🇸 ماكدونالدز - McDonald's": "MCD"
}

# دمج جميع الأسهم
ALL_STOCKS = {**EGYPT_STOCKS, **SAUDI_STOCKS, **US_STOCKS}

# ============================================================
# دوال التحليل المتقدمة
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_stock_data(ticker):
    """جلب بيانات السهم مع جميع المؤشرات"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo", interval="1d")
        
        if df.empty or len(df) < 10:
            return None, None
        
        # حساب المؤشرات الفنية
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
        
        # حجم التداول
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
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
    
    # 1. الاتجاه العام
    if last['Close'] > last['MA50']:
        score += 2
        signals.append("✅ الاتجاه العام صاعد")
    else:
        score -= 1
        signals.append("⚠️ الاتجاه العام هابط")
    
    # 2. RSI
    rsi = last['RSI'] if not pd.isna(last['RSI']) else 50
    if rsi < 25:
        score += 2
        signals.append(f"🔥 ذروة بيع شديدة - RSI: {rsi:.1f} (فرصة ممتازة)")
    elif rsi < 30:
        score += 1.5
        signals.append(f"✅ منطقة ذروة بيع - RSI: {rsi:.1f}")
    elif 30 <= rsi < 40:
        score += 1
        signals.append(f"📈 منطقة تجميع - RSI: {rsi:.1f}")
    elif 40 <= rsi < 60:
        score += 0.5
        signals.append(f"📊 منطقة محايدة - RSI: {rsi:.1f}")
    elif rsi > 80:
        score -= 1.5
        signals.append(f"⚠️ ذروة شراء شديدة - RSI: {rsi:.1f} (خطر)")
    elif rsi > 70:
        score -= 1
        signals.append(f"⚠️ منطقة ذروة شراء - RSI: {rsi:.1f}")
    else:
        signals.append(f"✅ RSI طبيعي - {rsi:.1f}")
    
    # 3. MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1
            signals.append("🚀 MACD إيجابي - إشارة شراء")
        else:
            score -= 0.5
            signals.append("📉 MACD سلبي - إشارة بيع")
    
    # 4. حجم التداول
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 2:
        score += 1.5
        signals.append(f"💰 سيولة عالية جداً ({vol_ratio:.1f}x)")
    elif vol_ratio > 1.5:
        score += 1
        signals.append(f"💰 سيولة جيدة ({vol_ratio:.1f}x)")
    elif vol_ratio > 1:
        score += 0.5
        signals.append(f"💰 سيولة أعلى من المعدل")
    elif vol_ratio < 0.5:
        score -= 0.5
        signals.append(f"📉 سيولة ضعيفة جداً")
    
    # 5. بولنجر باند
    if 'BBL_20_2.0' in last and 'BBU_20_2.0' in last:
        if last['Close'] <= last['BBL_20_2.0']:
            score += 1
            signals.append("🎯 السعر عند الدعم - ارتداد محتمل")
        elif last['Close'] >= last['BBU_20_2.0']:
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
        return "🔥 شراء قوي جداً", "#10b981", "🟢"
    elif score >= 4 or (rsi < 30 and last['Close'] > last['MA20']):
        return "✅ شراء قوي", "#22c55e", "🟢"
    elif score >= 3 or (rsi < 35 and last['Close'] > last['MA20']):
        return "📈 شراء محتمل", "#3b82f6", "📈"
    elif score >= 2:
        return "🟡 مراقبة / انتظار", "#f59e0b", "🟡"
    elif rsi > 80:
        return "🔴 بيع عاجل", "#ef4444", "🔴"
    elif rsi > 75 or score <= 1:
        return "📉 بيع / تخفيض", "#f97316", "📉"
    else:
        return "⚪ احتفاظ", "#94a3b8", "⚪"

# ============================================================
# دوال الرسم البياني
# ============================================================

def create_advanced_chart(df, ticker, target_price, stop_loss, stock_name):
    """رسم بياني متقدم مع المستهدفات"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.45, 0.2, 0.2, 0.15],
        subplot_titles=("📈 السعر مع المتوسطات والمستهدفات", "📊 مؤشر RSI", "⚡ مؤشر MACD", "💰 حجم التداول")
    )
    
    # الشموع اليابانية
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
                       line=dict(color='#94a3b8', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BBL_20_2.0'], name="BB سفلي",
                       line=dict(color='#94a3b8', dash='dash'),
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
        title=f"📊 التحليل الفني لسهم {stock_name}",
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
# ماسح السوق (Market Scanner) - جميع الأسهم
# ============================================================

def scan_market_by_category(category):
    """مسح الأسهم حسب الفئة المحددة"""
    results = []
    
    if category == "مصر":
        stocks = EGYPT_STOCKS
    elif category == "السعودية":
        stocks = SAUDI_STOCKS
    elif category == "أمريكا":
        stocks = US_STOCKS
    else:
        stocks = ALL_STOCKS
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (name, ticker) in enumerate(stocks.items()):
        status_text.text(f"🔄 جاري مسح: {name}...")
        df, _ = get_stock_data(ticker)
        
        if df is not None and not df.empty:
            score, _ = calculate_score(df)
            price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            
            if score >= 4:
                signal = "🟢🔥 فرصة شراء قوية جداً"
            elif score >= 3:
                signal = "🟢 فرصة شراء"
            elif score >= 2:
                signal = "🟡 مراقبة إيجابية"
            elif score <= 1.5:
                signal = "🔴 إشارة بيع/خروج"
            else:
                signal = "⚪ محايد"
            
            results.append({
                "السهم": name,
                "الرمز": ticker,
                "السعر": round(price, 2),
                "RSI": round(rsi, 1),
                "الدرجة": score,
                "الإشارة": signal
            })
        
        progress_bar.progress((idx + 1) / len(stocks))
        time.sleep(0.05)  # للتحكم في سرعة المسح
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results).sort_values("الدرجة", ascending=False)

# ============================================================
# الواجهة الرئيسية
# ============================================================

def main():
    # شريط جانبي
    with st.sidebar:
        st.markdown("## 📊 المحلل المصري Pro")
        st.markdown("### 🤖 جميع أسهم البورصات")
        st.markdown("---")
        
        # اختيار البورصة
        st.markdown("### 🌍 اختيار البورصة")
        exchange = st.radio(
            "",
            ["🇪🇬 البورصة المصرية", "🇸🇦 السوق السعودي", "🇺🇸 السوق الأمريكي", "🌍 جميع الأسواق"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # اختيار السهم حسب البورصة
        st.markdown("### 🔍 اختيار السهم")
        
        if exchange == "🇪🇬 البورصة المصرية":
            stock_list = EGYPT_STOCKS
        elif exchange == "🇸🇦 السوق السعودي":
            stock_list = SAUDI_STOCKS
        elif exchange == "🇺🇸 السوق الأمريكي":
            stock_list = US_STOCKS
        else:
            stock_list = ALL_STOCKS
        
        selected = st.selectbox("", list(stock_list.keys()), label_visibility="collapsed")
        ticker = stock_list[selected]
        
        st.caption(f"📌 الرمز: `{ticker}`")
        
        st.markdown("---")
        
        # إحصائيات البورصات
        st.markdown("### 📊 إحصائيات الأسهم")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🇪🇬 مصر", len(EGYPT_STOCKS))
        with col2:
            st.metric("🇸🇦 السعودية", len(SAUDI_STOCKS))
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("🇺🇸 أمريكا", len(US_STOCKS))
        with col4:
            st.metric("🌍 الإجمالي", len(ALL_STOCKS))
        
        st.markdown("---")
        
        # معلومات التحديث
        st.markdown("### 📈 معلومات")
        st.caption(f"🕐 الوقت: {datetime.now().strftime('%H:%M:%S')}")
        st.caption(f"🔄 تحديث تلقائي كل 60 ثانية")
        st.caption(f"📊 مصدر: Yahoo Finance")
        
        st.markdown("---")
        
        # زر التحديث
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
        rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
        
        # قرار التداول
        decision, decision_color, decision_icon = get_trading_decision(df, score)
        
        # بطاقات المعلومات
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta = f"{price_change:+.2f}%"
            delta_color = "normal" if price_change >= 0 else "inverse"
            st.metric("💰 السعر", f"{current_price:.2f}", delta, delta_color=delta_color)
        
        with col2:
            rsi_status = "🟢" if rsi < 40 else ("🔴" if rsi > 70 else "🟡")
            st.metric("📊 RSI", f"{rsi:.1f} {rsi_status}")
        
        with col3:
            st.metric("🎯 درجة الثقة", f"{score}/5")
        
        with col4:
            st.metric("📋 القرار", f"{decision_icon} {decision}")
        
        with col5:
            st.metric("🎯 الهدف", f"{target_price:.2f}")
        
        st.markdown("---")
        
        # بطاقة القرار الموسعة
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 2px solid {decision_color};
                    border-radius: 20px; padding: 20px;
                    text-align: center; margin: 15px 0;">
            <h2 style="color: {decision_color}; margin: 0;">
                {decision_icon} {decision} {decision_icon}
            </h2>
            <p style="color: #94a3b8; margin: 10px 0 0 0;">
                🛑 وقف الخسارة: {stop_loss:.2f} | 🎯 الهدف الأول: {target_price:.2f}
            </p>
            <p style="color: #64748b; margin: 5px 0 0 0; font-size: 12px;">
                الهدف البعيد: {(target_price * 1.05):.2f} | المخاطرة: {((target_price - current_price) / (current_price - stop_loss)):.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # التبويبات
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 الرسم البياني", "📋 التحليل الفني", "🔍 ماسح السوق", "🏢 معلومات الشركة"
        ])
        
        with tab1:
            fig = create_advanced_chart(df, ticker, target_price, stop_loss, selected)
            st.plotly_chart(fig, use_container_width=True, key="main_chart")
        
        with tab2:
            st.subheader("📋 تفاصيل التحليل الفني")
            
            # عرض الإشارات
            for signal in signals:
                if "✅" in signal or "🚀" in signal or "🔥" in signal or "💰" in signal:
                    st.success(signal)
                elif "⚠️" in signal or "⚠" in signal or "🔴" in signal:
                    st.warning(signal)
                else:
                    st.info(signal)
            
            st.markdown("---")
            
            # جدول المؤشرات
            st.subheader("📊 المؤشرات الحالية")
            last = df.iloc[-1]
            
            indicators_data = {
                "المؤشر": [
                    "السعر الحالي", "المتوسط المتحرك 20", "المتوسط المتحرك 50",
                    "المتوسط المتحرك 200", "RSI", "الدعم", "المقاومة"
                ],
                "القيمة": [
                    f"{last['Close']:.2f}",
                    f"{last['MA20']:.2f}",
                    f"{last['MA50']:.2f}",
                    f"{last['MA200']:.2f}",
                    f"{last['RSI']:.1f}",
                    f"{last['Support']:.2f}",
                    f"{last['Resistance']:.2f}"
                ],
                "الحالة": [
                    f"{'+' if last['Close'] > last['MA20'] else '-'}",
                    "-", "-", "-",
                    "ذروة بيع" if last['RSI'] < 30 else ("ذروة شراء" if last['RSI'] > 70 else "طبيعي"),
                    "دعم رئيسي",
                    "مقاومة رئيسية"
                ]
            }
            
            st.dataframe(pd.DataFrame(indicators_data), use_container_width=True, hide_index=True)
        
        with tab3:
            st.subheader("🔍 ماسح السوق الذكي")
            
            # خيارات الماسح
            scan_option = st.radio(
                "اختر نطاق المسح:",
                ["مسح البورصة الحالية", "مسح جميع البورصات"],
                horizontal=True
            )
            
            if scan_option == "مسح البورصة الحالية":
                if exchange == "🇪🇬 البورصة المصرية":
                    scan_category = "مصر"
                elif exchange == "🇸🇦 السوق السعودي":
                    scan_category = "السعودية"
                elif exchange == "🇺🇸 السوق الأمريكي":
                    scan_category = "أمريكا"
                else:
                    scan_category = "الكل"
            else:
                scan_category = "الكل"
            
            if st.button("🚀 تشغيل الماسح الضوئي", use_container_width=True):
                results_df = scan_market_by_category(scan_category)
                
                if not results_df.empty:
                    st.success(f"✅ تم مسح {len(results_df)} سهماً")
                    
                    # عرض أفضل الفرص
                    st.subheader("🏆 أفضل فرص الشراء")
                    buy_opportunities = results_df[results_df['الإشارة'].str.contains("شراء")]
                    if not buy_opportunities.empty:
                        st.dataframe(buy_opportunities.head(10), use_container_width=True, hide_index=True)
                    else:
                        st.info("لا توجد فرص شراء قوية حالياً")
                    
                    st.markdown("---")
                    
                    # عرض جميع النتائج
                    with st.expander("📊 عرض جميع النتائج", expanded=False):
                        st.dataframe(results_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ لا توجد بيانات كافية للمسح")
            
            # دليل المستخدم للماسح
            with st.expander("ℹ️ دليل استخدام الماسح", expanded=False):
                st.markdown("""
                ### كيفية استخدام الماسح:
                
                1. **اختر نطاق المسح** (البورصة الحالية أو جميع البورصات)
                2. **اضغط على زر التشغيل**
                3. **انتظر حتى اكتمال المسح** (قد يستغرق 30-60 ثانية)
                4. **شاهد أفضل الفرص** حسب درجة الثقة
                
                ### تفسير الإشارات:
                - 🟢🔥 **فرصة شراء قوية جداً** - درجة الثقة 4-5
                - 🟢 **فرصة شراء** - درجة الثقة 3-4
                - 🟡 **مراقبة إيجابية** - درجة الثقة 2-3
                - 🔴 **إشارة بيع/خروج** - درجة الثقة 0-1.5
                """)
        
        with tab4:
            if info:
                st.subheader("🏢 معلومات الشركة")
                
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
                    if info.get('dividend
