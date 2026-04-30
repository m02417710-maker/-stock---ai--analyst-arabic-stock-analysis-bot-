# ============================================================
# ملف: app_complete_fixed.py
# المحلل المصري Pro - جميع أسهم البورصات (مصر - السعودية - أمريكا)
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

st_autorefresh(interval=60000, key="auto_refresh", debounce=True)

# ============================================================
# التصميم
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
# جميع أسهم البورصات
# ============================================================

# الأسهم المصرية (EGX)
EGYPT_STOCKS = {
    "البنك التجاري الدولي (CIB)": "COMI.CA",
    "طلعت مصطفى القابضة": "TMGH.CA",
    "فوري لتكنولوجيا البنوك": "FWRY.CA",
    "المجموعة المالية هيرميس": "HRHO.CA",
    "العاشر من رمضان للصناعات الدوائية": "RADO.CA",
    "الإسكندرية للزيوت المعدنية": "AMOC.CA",
    "حديد عز": "ESRS.CA",
    "السويس للأسمنت": "SUCE.CA",
    "جهينة للصناعات الغذائية": "JUFO.CA",
    "أبو قير للأسمدة": "ABUK.CA",
    "مصر للإيداع والقيد": "MISR.CA",
    "بنك مصر": "BMEL.CA",
    "القاهرة للزيوت": "CANA.CA",
    "المصرية للاتصالات": "ETEL.CA"
}

# الأسهم السعودية (تداول)
SAUDI_STOCKS = {
    "أرامكو السعودية": "2222.SR",
    "البنك الأهلي السعودي": "1180.SR",
    "بنك الرياض": "1010.SR",
    "بنك الراجحي": "1120.SR",
    "بنك البلاد": "1140.SR",
    "بنك الجزيرة": "1020.SR",
    "بنك الإنماء": "1150.SR",
    "الاتصالات السعودية (STC)": "7010.SR",
    "موبايلي": "7030.SR",
    "زين السعودية": "7020.SR",
    "سابك": "2010.SR",
    "الشركة السعودية للكهرباء": "5110.SR",
    "أكوا باور": "2082.SR",
    "سليمان الحبيب": "4013.SR",
    "الحمادي": "4007.SR",
    "دلة الصحية": "4170.SR",
    "المواساة": "4015.SR",
    "بابا للتأمين": "8210.SR",
    "أسيج للتأمين": "8230.SR",
    "التعاونية للتأمين": "8010.SR"
}

# الأسهم الأمريكية (NASDAQ & NYSE)
US_STOCKS = {
    "آبل - Apple": "AAPL",
    "تسلا - Tesla": "TSLA",
    "مايكروسوفت - Microsoft": "MSFT",
    "إنفيديا - NVIDIA": "NVDA",
    "أمازون - Amazon": "AMZN",
    "جوجل - Google": "GOOGL",
    "ميتا - Meta": "META",
    "بيركشاير هاثاواي": "BRK-B",
    "فيزا - Visa": "V",
    "ماستركارد - Mastercard": "MA",
    "جي بي مورجان": "JPM",
    "بنك أوف أمريكا": "BAC",
    "نايك - Nike": "NKE",
    "ستاربكس - Starbucks": "SBUX",
    "فورد - Ford": "F",
    "بوينغ - Boeing": "BA",
    "ديزني - Disney": "DIS",
    "نتفليكس - Netflix": "NFLX",
    "إنتل - Intel": "INTC",
    "جونسون آند جونسون": "JNJ",
    "فايزر - Pfizer": "PFE",
    "موديرنا - Moderna": "MRNA",
    "كوستكو - Costco": "COST",
    "هوم ديبوت": "HD",
    "يو بي إس - UPS": "UPS",
    "سيلزفورس - Salesforce": "CRM",
    "آي بي إم - IBM": "IBM",
    "ماكدونالدز - McDonald's": "MCD",
    "كومكاست - Comcast": "CMCSA",
    "فيرايزون - Verizon": "VZ",
    "إيه تي آند تي - AT&T": "T"
}

# دمج جميع الأسهم
ALL_STOCKS = {**EGYPT_STOCKS, **SAUDI_STOCKS, **US_STOCKS}

# ============================================================
# دوال التحليل
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_stock_data(ticker):
    """جلب بيانات السهم"""
    if not ticker:
        return None, None
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo", interval="1d")
        if df.empty or len(df) < 10:
            return None, None
        
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
        
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Support'] = df['Low'].rolling(window=20).min()
        df['Resistance'] = df['High'].rolling(window=20).max()
        
        return df, stock.info
    except Exception as e:
        return None, None

def calculate_score(df):
    """حساب درجة الثقة"""
    if df is None or df.empty or len(df) < 20:
        return 0, []
    
    score = 0
    signals = []
    last = df.iloc[-1]
    
    # الاتجاه
    if last['Close'] > last['MA50']:
        score += 2
        signals.append("✅ الاتجاه العام صاعد")
    else:
        score -= 1
        signals.append("⚠️ الاتجاه العام هابط")
    
    # RSI
    rsi = last['RSI'] if not pd.isna(last['RSI']) else 50
    if rsi < 30:
        score += 1.5
        signals.append(f"🔥 منطقة شراء - RSI: {rsi:.1f}")
    elif rsi > 70:
        score -= 1
        signals.append(f"⚠️ منطقة بيع - RSI: {rsi:.1f}")
    else:
        score += 0.5
        signals.append(f"✅ RSI طبيعي - {rsi:.1f}")
    
    # MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1
            signals.append("✅ MACD إيجابي")
        else:
            score -= 0.5
            signals.append("📉 MACD سلبي")
    
    # حجم التداول
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 1.5:
        score += 1
        signals.append(f"💰 سيولة عالية ({vol_ratio:.1f}x)")
    elif vol_ratio < 0.5:
        score -= 0.5
        signals.append("📉 سيولة ضعيفة")
    
    return min(max(score, 0), 5), signals

def get_decision(score, rsi):
    """تحديد قرار التداول"""
    if score >= 4:
        return "شراء قوي", "#10b981", "🟢"
    elif score >= 3:
        return "شراء محتمل", "#3b82f6", "📈"
    elif score >= 2:
        return "مراقبة", "#f59e0b", "🟡"
    elif rsi > 75:
        return "بيع", "#ef4444", "🔴"
    else:
        return "احتفاظ", "#94a3b8", "⚪"

def create_chart(df, ticker, target, stop_loss, name):
    """رسم بياني متقدم"""
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.45, 0.2, 0.2, 0.15],
        subplot_titles=("السعر والمتوسطات", "RSI", "MACD", "حجم التداول")
    )
    
    # الشموع
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="السعر"
    ), row=1, col=1)
    
    # المتوسطات
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA 20",
                             line=dict(color='#f59e0b')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA 50",
                             line=dict(color='#10b981')), row=1, col=1)
    
    # الهدف ووقف الخسارة
    if target > 0:
        fig.add_hline(y=target, line_dash="dash", line_color="#10b981",
                     annotation_text=f"الهدف: {target:.2f}", row=1, col=1)
    if stop_loss > 0:
        fig.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"وقف: {stop_loss:.2f}", row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                             line=dict(color='#8b5cf6')), row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    
    # MACD
    if 'MACD_12_26_9' in df.columns:
        hist = df['MACD_12_26_9'] - df['MACDs_12_26_9']
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in hist]
        fig.add_trace(go.Bar(x=df.index, y=hist, name="Histogram",
                             marker_color=colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'],
                                 name="MACD", line=dict(color='#3b82f6')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'],
                                 name="Signal", line=dict(color='#f59e0b')), row=3, col=1)
    
    # الحجم
    vol_colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981'
                  for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم",
                         marker_color=vol_colors), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Volume_MA'], name="المتوسط",
                             line=dict(color='#3b82f6', dash='dash')), row=4, col=1)
    
    fig.update_layout(template="plotly_dark", height=750, margin=dict(l=10, r=10, t=50, b=10))
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="الحجم", row=4, col=1)
    
    return fig

# ============================================================
# ماسح السوق
# ============================================================

def scan_market(market_type):
    """مسح الأسهم حسب السوق"""
    results = []
    
    if market_type == "مصر":
        stocks = EGYPT_STOCKS
    elif market_type == "السعودية":
        stocks = SAUDI_STOCKS
    elif market_type == "أمريكا":
        stocks = US_STOCKS
    else:
        stocks = ALL_STOCKS
    
    progress = st.progress(0)
    for i, (name, ticker) in enumerate(stocks.items()):
        df, _ = get_stock_data(ticker)
        if df is not None:
            score, _ = calculate_score(df)
            price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            
            if score >= 3.5:
                signal = "🟢 شراء قوي"
            elif score >= 2.5:
                signal = "📈 فرصة"
            elif score <= 1.5:
                signal = "🔴 بيع"
            else:
                signal = "🟡 مراقبة"
            
            results.append({
                "السهم": name,
                "الرمز": ticker,
                "السعر": round(price, 2),
                "RSI": round(rsi, 1),
                "الدرجة": score,
                "الإشارة": signal
            })
        progress.progress((i + 1) / len(stocks))
    
    return pd.DataFrame(results).sort_values("الدرجة", ascending=False)

# ============================================================
# الواجهة الرئيسية
# ============================================================

def main():
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 📊 المحلل المصري Pro")
        st.markdown("### جميع أسهم البورصات")
        st.markdown("---")
        
        market = st.radio("اختر البورصة", ["🇪🇬 مصر", "🇸🇦 السعودية", "🇺🇸 أمريكا", "🌍 الجميع"], index=0)
        
        st.markdown("---")
        
        # عرض الأسهم حسب البورصة
        if market == "🇪🇬 مصر":
            stock_list = EGYPT_STOCKS
        elif market == "🇸🇦 السعودية":
            stock_list = SAUDI_STOCKS
        elif market == "🇺🇸 أمريكا":
            stock_list = US_STOCKS
        else:
            stock_list = ALL_STOCKS
        
        selected = st.selectbox("اختر السهم", list(stock_list.keys()))
        ticker = stock_list[selected]
        
        st.caption(f"الرمز: {ticker}")
        st.markdown("---")
        
        st.metric("🇪🇬 أسهم مصر", len(EGYPT_STOCKS))
        st.metric("🇸🇦 أسهم السعودية", len(SAUDI_STOCKS))
        st.metric("🇺🇸 أسهم أمريكا", len(US_STOCKS))
        st.metric("📊 إجمالي الأسهم", len(ALL_STOCKS))
        
        st.markdown("---")
        
        if st.button("🔄 تحديث", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    # المحتوى الرئيسي
    st.markdown(f"## 📈 تحليل سهم {selected}")
    st.markdown(f"### {ticker}")
    st.markdown("---")
    
    df, info = get_stock_data(ticker)
    
    if df is not None and not df.empty:
        score, signals = calculate_score(df)
        price = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2] if len(df) > 1 else price
        change = ((price - prev) / prev) * 100
        rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
        
        target = df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else price * 1.05
        stop = df['Support'].iloc[-1] if not pd.isna(df['Support'].iloc[-1]) else price * 0.97
        
        decision, color, icon = get_decision(score, rsi)
        
        # بطاقات المعلومات
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("💰 السعر", f"{price:.2f}", f"{change:+.2f}%")
        c2.metric("📊 RSI", f"{rsi:.1f}")
        c3.metric("🎯 الدرجة", f"{score}/5")
        c4.metric("📋 القرار", f"{icon} {decision}")
        c5.metric("🎯 الهدف", f"{target:.2f}")
        
        # قرار التداول
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 2px solid {color}; border-radius: 20px;
                    padding: 20px; text-align: center; margin: 15px 0;">
            <h2 style="color: {color}; margin: 0;">
                {icon} {decision} {icon}
            </h2>
            <p style="color: #94a3b8;">وقف الخسارة: {stop:.2f} | الهدف: {target:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # التبويبات
        t1, t2, t3 = st.tabs(["📈 الرسم البياني", "📋 التحليل", "🔍 ماسح السوق"])
        
        with t1:
            fig = create_chart(df, ticker, target, stop, selected)
            st.plotly_chart(fig, use_container_width=True)
        
        with t2:
            for s in signals:
                if "✅" in s or "🔥" in s:
                    st.success(s)
                elif "⚠️" in s:
                    st.warning(s)
                else:
                    st.info(s)
        
        with t3:
            if st.button("🚀 تشغيل الماسح", use_container_width=True):
                market_type = market.replace("🇪🇬 ", "").replace("🇸🇦 ", "").replace("🇺🇸 ", "").replace("🌍 ", "")
                if market_type == "الجميع":
                    market_type = "الكل"
                df_scan = scan_market(market_type)
                if not df_scan.empty:
                    st.dataframe(df_scan, use_container_width=True, hide_index=True)
                else:
                    st.warning("لا توجد بيانات")
    
    else:
        st.error("❌ فشل في جلب البيانات")
        st.info("""
        💡 تأكد من:
        - صحة رمز السهم
        - اتصال الإنترنت
        - إعادة المحاولة بعد دقيقة
        """)
    
    st.markdown("---")
    st.caption("⚠️ تنويه: للتعليم فقط | 📊 بيانات Yahoo Finance | 🔄 تحديث تلقائي كل 60 ثانية")

if __name__ == "__main__":
    main()
