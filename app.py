# ============================================================
# ملف: app_final.py
# المحلل المصري Pro - الإصدار النهائي المتكامل
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

warnings.filterwarnings('ignore')

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="المحلل المصري Pro - الإصدار النهائي",
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
/* الخلفية الرئيسية */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* بطاقات المؤشرات */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #3b82f6;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

/* أزرار */
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

/* تبويبات */
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

/* شريط جانبي */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e293b);
    border-right: 1px solid #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# قائمة الأسهم الموسعة
# ============================================================

STOCKS_DB = {
    "🏦 البنك التجاري الدولي (مصر)": "COMI.CA",
    "🏗️ طلعت مصطفى (مصر)": "TMGH.CA",
    "💳 فوري (مصر)": "FWRY.CA",
    "🛢️ أرامكو (السعودية)": "2222.SR",
    "🏦 الراجحي (السعودية)": "1120.SR",
    "🍎 آبل (أمريكا)": "AAPL",
    "🚀 تسلا (أمريكا)": "TSLA",
    "💻 مايكروسوفت (أمريكا)": "MSFT",
    "🎮 إنفيديا (أمريكا)": "NVDA",
    "📦 أمازون (أمريكا)": "AMZN",
    "🔍 جوجل (أمريكا)": "GOOGL",
    "📘 ميتا (أمريكا)": "META"
}

# ============================================================
# دوال التحليل المتقدمة
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_stock_data(ticker):
    """جلب بيانات السهم مع جميع المؤشرات"""
    try:
        stock = yf.Ticker(ticker)
        
        # جلب بيانات 3 أشهر للتحليل
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
        st.error(f"خطأ: {str(e)}")
        return None, None

def calculate_score(df):
    """حساب درجة الثقة المتقدمة"""
    if df.empty or len(df) < 20:
        return 0, []
    
    score = 0
    signals = []
    last = df.iloc[-1]
    
    # 1. الاتجاه (وزن 2)
    if last['Close'] > last['MA50']:
        score += 2
        signals.append("✅ الاتجاه العام صاعد")
    else:
        signals.append("⚠️ الاتجاه العام هابط")
        score -= 1
    
    # 2. الزخم (وزن 1.5)
    if last['RSI'] < 30:
        score += 1.5
        signals.append(f"🔥 منطقة ذروة بيع - RSI: {last['RSI']:.1f}")
    elif last['RSI'] > 70:
        score -= 1
        signals.append(f"⚠️ منطقة ذروة شراء - RSI: {last['RSI']:.1f}")
    else:
        score += 0.5
        signals.append(f"✅ RSI طبيعي - {last['RSI']:.1f}")
    
    # 3. MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1
            signals.append("🚀 MACD إيجابي")
        else:
            signals.append("📉 MACD سلبي")
            score -= 0.5
    
    # 4. الحجم
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 1.5:
        score += 1
        signals.append(f"💰 سيولة عالية ({vol_ratio:.1f}x)")
    elif vol_ratio < 0.5:
        score -= 0.5
        signals.append(f"📉 سيولة ضعيفة")
    
    return min(max(score, 0), 5), signals

def get_trading_decision(df, score):
    """تحديد قرار التداول"""
    if df.empty:
        return "لا توجد بيانات", "#gray", "⏸️"
    
    last = df.iloc[-1]
    rsi = last['RSI'] if not pd.isna(last['RSI']) else 50
    
    # قرار الشراء القوي
    if score >= 4 or (rsi < 35 and last['Close'] > last['MA20']):
        return "شراء قوي", "#10b981", "🟢"
    # قرار شراء محتمل
    elif score >= 3 or (40 < rsi < 50):
        return "شراء محتمل", "#3b82f6", "📈"
    # قرار مراقبة
    elif score >= 2:
        return "مراقبة", "#f59e0b", "🟡"
    # قرار بيع
    elif rsi > 75:
        return "بيع/تصريف", "#ef4444", "🔴"
    else:
        return "احتفاظ", "#94a3b8", "⚪"

# ============================================================
# دوال الرسم البياني
# ============================================================

def create_advanced_chart(df, ticker, target_price, stop_loss):
    """رسم بياني متقدم مع المستهدفات"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.45, 0.2, 0.2, 0.15],
        subplot_titles=("📈 السعر مع المتوسطات والمستهدفات", "📊 مؤشر RSI", "⚡ مؤشر MACD", "💰 حجم التداول")
    )
    
    # ===== الرسم الرئيسي =====
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
    
    # ===== RSI =====
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                   line=dict(color='#8b5cf6', width=2)),
        row=2, col=1
    )
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    
    # ===== MACD =====
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
    
    # ===== حجم التداول =====
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
    
    # تنسيق الرسم
    fig.update_layout(
        title=f"📊 التحليل الفني لسهم {ticker}",
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
# ماسح السوق (Market Scanner)
# ============================================================

def scan_all_stocks():
    """مسح جميع الأسهم للبحث عن فرص"""
    results = []
    
    with st.spinner("🔄 جاري مسح جميع الأسهم..."):
        for name, ticker in STOCKS_DB.items():
            df, _ = get_stock_data(ticker)
            if df is not None:
                score, _ = calculate_score(df)
                last_price = df['Close'].iloc[-1]
                rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
                
                # تحديد مستوى الفرصة
                if score >= 4:
                    signal = "🟢 فرصة شراء قوية"
                elif score >= 3:
                    signal = "📈 فرصة شراء"
                elif score <= 1.5:
                    signal = "🔴 إشارة بيع"
                else:
                    signal = "🟡 مراقبة"
                
                results.append({
                    "السهم": name.split(" ")[1] if len(name.split(" ")) > 1 else name,
                    "الرمز": ticker,
                    "السعر": round(last_price, 2),
                    "RSI": round(rsi, 1),
                    "الدرجة": score,
                    "الإشارة": signal
                })
    
    return pd.DataFrame(results)

# ============================================================
# الواجهة الرئيسية
# ============================================================

def main():
    # شريط جانبي
    with st.sidebar:
        st.markdown("## 📊 المحلل المصري Pro")
        st.markdown("---")
        
        # اختيار السهم
        st.markdown("### 🔍 اختيار السهم")
        selected = st.selectbox("", list(STOCKS_DB.keys()), label_visibility="collapsed")
        ticker = STOCKS_DB[selected]
        
        st.markdown("---")
        
        # إحصائيات سريعة
        st.markdown("### 📈 معلومات")
        st.caption(f"🕐 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")
        st.caption(f"🔄 تحديث تلقائي كل 60 ثانية")
        st.caption(f"📊 مصدر: Yahoo Finance")
        
        st.markdown("---")
        
        # زر التحديث اليدوي
        if st.button("🔄 تحديث يدوي", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # عنوان رئيسي
    st.markdown(f"## 📈 التحليل المتكامل لسهم {selected}")
    st.markdown("---")
    
    # جلب البيانات
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
        
        # ===== بطاقات المعلومات =====
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta = f"{price_change:+.2f}%"
            st.metric("💰 السعر", f"{current_price:.2f}", delta)
        
        with col2:
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            st.metric("📊 RSI", f"{rsi:.1f}")
        
        with col3:
            st.metric("🎯 درجة الثقة", f"{score}/5")
        
        with col4:
            st.metric("📋 القرار", decision)
        
        with col5:
            st.metric("🎯 الهدف", f"{target_price:.2f}")
        
        st.markdown("---")
        
        # ===== بطاقة القرار =====
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 2px solid {decision_color};
                    border-radius: 20px; padding: 20px;
                    text-align: center; margin: 15px 0;">
            <h2 style="color: {decision_color}; margin: 0;">
                {decision_icon} {decision} {decision_icon}
            </h2>
            <p style="color: #94a3b8; margin: 10px 0 0 0;">
                🛑 وقف الخسارة: {stop_loss:.2f} | 🎯 الهدف: {target_price:.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== التبويبات =====
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 الرسم البياني", "📋 التحليل الفني", "🔍 ماسح السوق", "🏢 معلومات الشركة"
        ])
        
        with tab1:
            fig = create_advanced_chart(df, ticker, target_price, stop_loss)
            st.plotly_chart(fig, use_container_width=True, key="main_chart")
        
        with tab2:
            st.subheader("📋 تفاصيل التحليل الفني")
            
            # عرض الإشارات
            for signal in signals:
                if "✅" in signal or "🚀" in signal:
                    st.success(signal)
                elif "⚠️" in signal or "⚠" in signal:
                    st.warning(signal)
                else:
                    st.info(signal)
            
            st.markdown("---")
            
            # جدول المؤشرات
            st.subheader("📊 المؤشرات الحالية")
            last = df.iloc[-1]
            indicators = {
                "المؤشر": ["السعر", "المتوسط 20", "المتوسط 50", "RSI", "المقاومة", "الدعم"],
                "القيمة": [
                    f"{last['Close']:.2f}",
                    f"{last['MA20']:.2f}",
                    f"{last['MA50']:.2f}",
                    f"{last['RSI']:.1f}",
                    f"{last['Resistance']:.2f}",
                    f"{last['Support']:.2f}"
                ]
            }
            st.dataframe(pd.DataFrame(indicators), use_container_width=True, hide_index=True)
        
        with tab3:
            st.subheader("🔍 ماسح السوق الذكي")
            
            if st.button("🚀 تشغيل الماسح الضوئي", use_container_width=True):
                results_df = scan_all_stocks()
                if not results_df.empty:
                    st.success(f"✅ تم العثور على {len(results_df)} فرصة")
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                    
                    # عرض أفضل 3 فرص
                    st.subheader("🏆 أفضل الفرص حالياً")
                    top_opportunities = results_df[results_df['الإشارة'].str.contains("شراء")].head(3)
                    if not top_opportunities.empty:
                        for _, row in top_opportunities.iterrows():
                            st.info(f"📈 {row['السهم']} - {row['الإشارة']} | السعر: {row['السعر']} | RSI: {row['RSI']}")
                    else:
                        st.info("لا توجد فرص شراء قوية حالياً")
                else:
                    st.warning("⚠️ لا توجد بيانات كافية للمسح")
        
        with tab4:
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
                        st.markdown(f"**📊 مكرر الأرباح:** {info.get('trailingPE', 'غير متوفر')}")
                    if info.get('dividendYield'):
                        st.markdown(f"**💵 عائد التوزيعات:** {info.get('dividendYield', 0)*100:.2f}%")
                
                if info.get('longBusinessSummary'):
                    st.markdown("---")
                    st.markdown("**📝 نبذة عن الشركة:**")
                    st.markdown(info.get('longBusinessSummary')[:500] + "...")
            else:
                st.info("معلومات الشركة غير متوفرة حالياً")
    
    else:
        st.error("❌ فشل في جلب البيانات")
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <p>⚠️ تأكد من:</p>
            <ul style="text-align: right;">
                <li>صحة رمز السهم</li>
                <li>اتصال الإنترنت</li>
                <li>إعادة المحاولة بعد دقيقة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # تذييل
    st.markdown("---")
    st.caption("""
    ⚠️ **تنويه:** هذا التحليل لأغراض تعليمية فقط.
    🔄 يتم تحديث البيانات تلقائياً كل 60 ثانية.
    📊 البيانات مقدمة من Yahoo Finance.
    """)

if __name__ == "__main__":
    main()
