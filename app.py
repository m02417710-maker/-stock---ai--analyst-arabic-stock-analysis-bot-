import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title="المحلل المصري",
    page_icon="📈",
    layout="wide"
)

# قائمة الأسهم
STOCKS_LIST = {
    "البنك التجاري الدولي (مصر)": "COMI.CA",
    "طلعت مصطفى (مصر)": "TMGH.CA",
    "فوري (مصر)": "FWRY.CA",
    "أرامكو (السعودية)": "2222.SR",
    "الراجحي (السعودية)": "1120.SR",
    "آبل (أمريكا)": "AAPL",
    "تسلا (أمريكا)": "TSLA",
    "مايكروسوفت (أمريكا)": "MSFT",
    "إنفيديا (أمريكا)": "NVDA"
}

# دالة جلب البيانات
@st.cache_data(ttl=300)
def load_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        if df.empty:
            return None, None, None
        
        # حساب المؤشرات
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        dividends = stock.dividends
        
        return df, dividends, stock.info
        
    except Exception as e:
        return None, None, None

# الشريط الجانبي
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=50)
    st.title("المحلل المصري")
    st.markdown("---")
    
    selected = st.selectbox("اختر السهم", list(STOCKS_LIST.keys()))
    custom_ticker = st.text_input("أو أدخل رمز السهم", placeholder="AAPL, TSLA, 2222.SR")
    
    if custom_ticker:
        ticker = custom_ticker.upper().strip()
    else:
        ticker = STOCKS_LIST[selected]
    
    st.info(f"الرمز: `{ticker}`")
    st.markdown("---")
    
    if st.button("🔄 تحديث", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.caption(f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")

# العنوان الرئيسي
st.title(f"📊 تحليل سهم {ticker}")
st.markdown("---")

# جلب البيانات
df, dividends, info = load_data(ticker)

if df is not None and not df.empty:
    
    # ===== معلومات سريعة =====
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
    change = ((current_price - prev_price) / prev_price) * 100
    
    rsi = df['RSI'].iloc[-1]
    volume = df['Volume'].iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("السعر", f"{current_price:.2f}", f"{change:+.2f}%")
    col2.metric("RSI", f"{rsi:.1f}")
    col3.metric("الحجم", f"{volume/1000000:.1f}M")
    col4.metric("المتوسط 20", f"{df['SMA20'].iloc[-1]:.2f}")
    
    st.markdown("---")
    
    # ===== إشارة التداول =====
    if rsi < 30:
        signal = "🟢 إشارة شراء (منطقة ذروة بيع)"
        signal_color = "green"
    elif rsi > 70:
        signal = "🔴 إشارة بيع (منطقة ذروة شراء)"
        signal_color = "red"
    else:
        signal = "🟡 منطقة محايدة - انتظار"
        signal_color = "yellow"
    
    st.markdown(f"""
    <div style="background:#1e222d; padding:15px; border-radius:10px; text-align:center; margin:10px 0">
        <h3 style="color:{signal_color}; margin:0">{signal}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== التبويبات =====
    tab1, tab2, tab3 = st.tabs(["📈 الرسم البياني", "📊 المؤشرات", "💰 التوزيعات"])
    
    with tab1:
        # رسم الشموع
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="السعر"
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA20'],
            name="SMA 20",
            line=dict(color='orange', width=1.5)
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA50'],
            name="SMA 50",
            line=dict(color='green', width=1.5)
        ))
        
        fig.update_layout(
            title=f"رسم بياني لسهم {ticker}",
            template="plotly_dark",
            height=500,
            xaxis_title="التاريخ",
            yaxis_title="السعر",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True, key="candlestick_chart")
        
        # حجم التداول
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df.index, y=df['Volume'], name="حجم التداول", marker_color='steelblue'))
        fig2.update_layout(
            title="حجم التداول",
            template="plotly_dark",
            height=300,
            xaxis_title="التاريخ",
            yaxis_title="الحجم",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True, key="volume_chart")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # رسم RSI
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple', width=2)))
            fig3.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="ذروة شراء")
            fig3.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="ذروة بيع")
            fig3.add_hrect(y0=30, y1=70, fillcolor="gray", opacity=0.1)
            fig3.update_layout(
                title="مؤشر القوة النسبية RSI",
                template="plotly_dark",
                height=400,
                yaxis_range=[0, 100],
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig3, use_container_width=True, key="rsi_chart")
        
        with col2:
            # رسم MACD
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name="Histogram", marker_color='gray'))
            fig4.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='blue', width=2)))
            fig4.add_trace(go.Scatter(x=df.index, y=df['Signal'], name="Signal", line=dict(color='red', width=2)))
            fig4.update_layout(
                title="مؤشر MACD",
                template="plotly_dark",
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig4, use_container_width=True, key="macd_chart")
        
        # معلومات إضافية
        st.markdown("---")
        st.subheader("📋 ملخص المؤشرات")
        
        latest = df.iloc[-1]
        metrics_data = {
            "السعر الحالي": f"{latest['Close']:.2f}",
            "المتوسط 20": f"{latest['SMA20']:.2f}",
            "المتوسط 50": f"{latest['SMA50']:.2f}",
            "RSI": f"{latest['RSI']:.1f}",
            "MACD": f"{latest['MACD']:.3f}",
            "إشارة MACD": f"{latest['Signal']:.3f}"
        }
        
        for key, value in metrics_data.items():
            st.metric(key, value)
    
    with tab3:
        st.subheader("💰 توزيعات الأرباح السابقة")
        
        if not dividends.empty:
            div_data = []
            for date, amount in dividends.tail(10).items():
                div_data.append({"التاريخ": date.strftime('%Y-%m-%d'), "القيمة": f"{amount:.3f}"})
            
            st.table(pd.DataFrame(div_data))
            
            total = dividends.sum()
            avg = dividends.mean()
            
            col1, col2 = st.columns(2)
            col1.metric("إجمالي التوزيعات", f"{total:.3f}")
            col2.metric("متوسط التوزيع", f"{avg:.3f}")
        else:
            st.info("لا توجد بيانات توزيعات أرباح متاحة لهذا السهم")
    
    # ===== معلومات الشركة =====
    st.markdown("---")
    with st.expander("ℹ️ معلومات إضافية عن الشركة"):
        if info:
            st.write(f"**الاسم:** {info.get('longName', 'غير متوفر')}")
            st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")
            st.write(f"**السوق:** {info.get('market', 'غير متوفر')}")
            if info.get('marketCap'):
                st.write(f"**القيمة السوقية:** ${info.get('marketCap', 0):,}")
        else:
            st.write("معلومات الشركة غير متوفرة حالياً")

else:
    st.error("❌ لا يمكن جلب البيانات")
    st.markdown("""
    ### 💡 الأسباب المحتملة:
    
    1. **رمز السهم غير صحيح**
       - الأسهم الأمريكية: `AAPL`, `TSLA`, `MSFT`
       - الأسهم السعودية: `2222.SR`, `1120.SR`
       - الأسهم المصرية: `COMI.CA`, `TMGH.CA`
    
    2. **مشكلة في الاتصال**: انتظر دقيقة ثم حاول مرة أخرى
    
    3. **السهم غير موجود**: تأكد من الرمز في Yahoo Finance
    
    ### ✅ جرب هذه الرموز:
    - `AAPL` - آبل
    - `TSLA` - تسلا
    - `2222.SR` - أرامكو
    - `COMI.CA` - البنك التجاري المصري
    """)

st.markdown("---")
st.caption("⚠️ تنويه: هذا التحليل لأغراض تعليمية فقط وليس توصية استثمارية")
