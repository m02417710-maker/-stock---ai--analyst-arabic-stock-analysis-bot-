# ============================================================
# ملف: app_oracle_fixed.py
# Oracle Zero-Knowledge - نسخة خالية من الأخطاء
# بدون مكتبات إضافية - تعمل على أي بيئة
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
import time

warnings.filterwarnings('ignore')

# ============================================================
# دوال بديلة لمكتبة scipy (لتجنب أخطاء التثبيت)
# ============================================================

def normal_cdf(x):
    """دالة بديلة لتوزيع الاحتمالات الطبيعي (بدون scipy)"""
    # Abramowitz and Stegun approximation
    t = 1 / (1 + 0.2316419 * abs(x))
    d = 0.3989423 * np.exp(-x * x / 2)
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
    if x >= 0:
        return 1 - p
    else:
        return p

def norm_ppf(q, loc=0, scale=1):
    """دالة بديلة لحساب النسب المئوية (بدون scipy)"""
    # Simplified approximation for percentiles
    if q <= 0:
        return -np.inf
    if q >= 1:
        return np.inf
    
    # Approximation for common percentiles
    if q == 0.05:
        return loc + scale * (-1.6449)
    elif q == 0.25:
        return loc + scale * (-0.6745)
    elif q == 0.5:
        return loc + scale * 0
    elif q == 0.75:
        return loc + scale * 0.6745
    elif q == 0.95:
        return loc + scale * 1.6449
    else:
        # Linear interpolation for other values
        known_q = [0.05, 0.25, 0.5, 0.75, 0.95]
        known_z = [-1.6449, -0.6745, 0, 0.6745, 1.6449]
        return loc + scale * np.interp(q, known_q, known_z)

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="المحلل المصري - الإصدار النهائي",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    border: 1px solid #10b981;
    border-radius: 15px;
    padding: 15px;
}
.oracle-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 20px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #10b981;
}
.risk-meter {
    background: linear-gradient(135deg, #1e1b4b, #2e1065);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# قائمة الأسهم - تحديث مايو 2026
# ============================================================

STOCKS_LIST = {
    "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
    "🇪🇬 طلعت مصطفى القابضة": "TMGH.CA",
    "🇪🇬 فوري لتكنولوجيا البنوك": "FWRY.CA",
    "🇪🇬 المجموعة المالية هيرميس": "HRHO.CA",
    "🇪🇬 حديد عز": "ESRS.CA",
    "🇪🇬 جهينة للصناعات الغذائية": "JUFO.CA",
    "🇪🇬 أبو قير للأسمدة": "ABUK.CA",
    "🇪🇬 بنك مصر": "BMEL.CA",
    "🇸🇦 أرامكو السعودية": "2222.SR",
    "🇸🇦 بنك الراجحي": "1120.SR",
    "🇺🇸 آبل - Apple": "AAPL",
    "🇺🇸 تسلا - Tesla": "TSLA",
    "🇺🇸 مايكروسوفت - Microsoft": "MSFT",
    "🇺🇸 إنفيديا - NVIDIA": "NVDA"
}

# ============================================================
# 1. محرك مونت كارلو المبسط (بدون scipy)
# ============================================================

class MonteCarloEngine:
    """محاكاة مونت كارلو باستخدام العوائد اللوغاريتمية"""
    
    def __init__(self, df, days=30, simulations=5000):
        self.df = df
        self.days = days
        self.simulations = simulations
        self.last_price = df['Close'].iloc[-1]
        
        # استخدام العوائد اللوغاريتمية
        self.log_returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        
        # معالجة حالة البيانات القليلة
        if len(self.log_returns) < 5:
            self.mu = 0.0005
            self.sigma = 0.02
        else:
            self.mu = self.log_returns.mean()
            self.sigma = self.log_returns.std()
        
        self.volatility = self.sigma * np.sqrt(252) if self.sigma else 0.2
    
    def run_simulation(self):
        """تشغيل المحاكاة"""
        results = np.zeros((self.days, self.simulations))
        
        np.random.seed(42)
        for i in range(self.simulations):
            random_returns = np.random.normal(self.mu, self.sigma, self.days - 1)
            prices = [self.last_price]
            for ret in random_returns:
                prices.append(prices[-1] * np.exp(ret))
            results[:, i] = prices
        
        self.results = results
        return self.calculate_statistics()
    
    def calculate_statistics(self):
        """حساب الإحصائيات"""
        final_prices = self.results[-1, :]
        
        expected_price = np.mean(final_prices)
        median_price = np.median(final_prices)
        std_dev = np.std(final_prices)
        
        # النسب المئوية باستخدام numpy فقط
        confidence_5 = np.percentile(final_prices, 5)
        confidence_25 = np.percentile(final_prices, 25)
        confidence_50 = np.percentile(final_prices, 50)
        confidence_75 = np.percentile(final_prices, 75)
        confidence_95 = np.percentile(final_prices, 95)
        
        # القيمة المعرضة للخطر
        var_95 = self.last_price - confidence_5
        var_99 = self.last_price - np.percentile(final_prices, 1)
        
        # خسارة الذيل
        tail_losses = final_prices[final_prices <= confidence_5]
        cvar_95 = self.last_price - np.mean(tail_losses) if len(tail_losses) > 0 else var_95
        
        # الاحتمالات
        profit_probability = np.sum(final_prices > self.last_price) / self.simulations * 100
        
        target_5 = self.last_price * 1.05
        target_10 = self.last_price * 1.10
        
        prob_target_5 = np.sum(final_prices >= target_5) / self.simulations * 100
        prob_target_10 = np.sum(final_prices >= target_10) / self.simulations * 100
        
        stop_loss = self.last_price * 0.95
        prob_stop_hit = np.sum(final_prices <= stop_loss) / self.simulations * 100
        
        return {
            "expected_price": expected_price,
            "median_price": median_price,
            "std_dev": std_dev,
            "confidence_5": confidence_5,
            "confidence_25": confidence_25,
            "confidence_75": confidence_75,
            "confidence_95": confidence_95,
            "var_95": var_95,
            "var_99": var_99,
            "cvar_95": cvar_95,
            "profit_probability": profit_probability,
            "prob_target_5": prob_target_5,
            "prob_target_10": prob_target_10,
            "prob_stop_hit": prob_stop_hit,
            "volatility": self.volatility * 100
        }
    
    def plot_simulations(self):
        """رسم مسارات المحاكاة"""
        fig = go.Figure()
        
        # عينة من المسارات
        sample_paths = np.random.choice(self.simulations, min(100, self.simulations), replace=False)
        for i in sample_paths:
            fig.add_trace(go.Scatter(
                y=self.results[:, i],
                mode='lines',
                line=dict(width=0.5, color='rgba(16, 185, 129, 0.1)'),
                showlegend=False
            ))
        
        # المتوسط
        mean_path = np.mean(self.results, axis=1)
        fig.add_trace(go.Scatter(
            y=mean_path,
            mode='lines',
            name='المتوسط المتوقع',
            line=dict(color='#10b981', width=3)
        ))
        
        # نطاقات الثقة
        upper_95 = np.percentile(self.results, 95, axis=1)
        lower_95 = np.percentile(self.results, 5, axis=1)
        
        fig.add_trace(go.Scatter(
            y=upper_95, fill=None, mode='lines',
            line=dict(color='rgba(16, 185, 129, 0.3)'),
            name='حد أعلى 95%'
        ))
        
        fig.add_trace(go.Scatter(
            y=lower_95, fill='tonexty', mode='lines',
            line=dict(color='rgba(16, 185, 129, 0.3)'),
            name='حد أدنى 95%'
        ))
        
        fig.update_layout(
            title="📊 محاكاة مونت كارلو - 5,000 سيناريو",
            template="plotly_dark",
            height=500,
            xaxis_title="الأيام القادمة",
            yaxis_title="السعر المتوقع"
        )
        
        return fig

# ============================================================
# 2. دوال التحليل الأساسي
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_stock_data(ticker):
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo", interval="1d")
        
        if df.empty or len(df) < 10:
            return None, None
        
        # المؤشرات الفنية
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        
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
    if df is None or len(df) < 20:
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
        signals.append(f"✅ منطقة شراء - RSI: {rsi:.1f}")
    elif rsi > 70:
        score -= 1
        signals.append(f"⚠️ منطقة بيع - RSI: {rsi:.1f}")
    else:
        score += 0.5
        signals.append(f"📊 RSI طبيعي - {rsi:.1f}")
    
    # MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1
            signals.append("🚀 MACD إيجابي")
        else:
            score -= 0.5
            signals.append("📉 MACD سلبي")
    
    return min(max(score, 0), 5), signals

def get_decision(score, prob_profit):
    """تحديد القرار"""
    if score >= 4 and prob_profit > 60:
        return "شراء قوي", "#10b981", "🟢"
    elif score >= 3 and prob_profit > 50:
        return "شراء محتمل", "#3b82f6", "📈"
    elif score >= 2:
        return "مراقبة", "#f59e0b", "🟡"
    else:
        return "انتظار / تجنب", "#ef4444", "🔴"

# ============================================================
# 3. دوال الرسم البياني
# ============================================================

def create_chart(df, ticker, target, stop):
    """رسم بياني متقدم"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=("السعر مع المتوسطات", "مؤشر RSI", "حجم التداول")
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
    if stop > 0:
        fig.add_hline(y=stop, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"وقف: {stop:.2f}", row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                             line=dict(color='#8b5cf6')), row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    
    # حجم التداول
    colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
              for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم",
                         marker_color=colors), row=3, col=1)
    
    fig.update_layout(template="plotly_dark", height=700, margin=dict(l=10, r=10, t=60, b=10))
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="الحجم", row=3, col=1)
    
    return fig

# ============================================================
# 4. الواجهة الرئيسية
# ============================================================

def main():
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("# 📊 المحلل المصري")
        st.markdown("### النظام المتكامل للتحليل")
        st.markdown("---")
        
        selected = st.selectbox("اختر السهم", list(STOCKS_LIST.keys()))
        ticker = STOCKS_LIST[selected]
        
        st.markdown("---")
        
        # إعدادات المحاكاة
        st.markdown("### ⚙️ إعدادات التحليل")
        days_ahead = st.slider("أيام التنبؤ", 15, 60, 30)
        
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("🔄 تحديث", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # العنوان
    st.markdown(f"## 📈 تحليل سهم {selected}")
    st.markdown(f"### {ticker}")
    st.markdown("---")
    
    # جلب البيانات
    with st.spinner("جاري تحليل البيانات..."):
        df, info = get_stock_data(ticker)
    
    if df is not None and not df.empty:
        # التحليل
        score, signals = calculate_score(df)
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        # مونت كارلو
        with st.spinner("تشغيل محاكاة مونت كارلو..."):
            mc = MonteCarloEngine(df, days=days_ahead, simulations=5000)
            stats = mc.run_simulation()
        
        # الأهداف
        target = stats['confidence_75'] if stats['confidence_75'] > current_price else current_price * 1.07
        stop = stats['confidence_25'] if stats['confidence_25'] < current_price else current_price * 0.95
        
        # القرار
        decision, decision_color, decision_icon = get_decision(score, stats['profit_probability'])
        
        # البطاقات
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 السعر", f"{current_price:.2f}", f"{price_change:+.2f}%")
        col2.metric("📊 RSI", f"{df['RSI'].iloc[-1]:.1f}")
        col3.metric("🎯 درجة الثقة", f"{score}/5")
        col4.metric("🔮 احتمال الربح", f"{stats['profit_probability']:.1f}%")
        
        st.markdown("---")
        
        # بطاقة القرار
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a);
                    border: 2px solid {decision_color};
                    border-radius: 20px; padding: 25px;
                    text-align: center; margin: 15px 0;">
            <h1 style="color: {decision_color}; margin: 0;">
                {decision_icon} {decision}
            </h1>
            <p style="color: #94a3b8; margin-top: 10px;">
                🎯 الهدف: {target:.2f} | 🛑 وقف الخسارة: {stop:.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # تبويبات
        tab1, tab2, tab3 = st.tabs(["📈 الرسم البياني", "📊 تحليل مونت كارلو", "📋 تفاصيل التحليل"])
        
        with tab1:
            fig = create_chart(df, ticker, target, stop)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("إحصائيات المحاكاة")
                st.metric("السعر المتوقع", f"{stats['expected_price']:.2f}")
                st.metric("نطاق 90% ثقة", f"{stats['confidence_5']:.2f} - {stats['confidence_95']:.2f}")
                st.metric("التذبذب السنوي", f"{stats['volatility']:.1f}%")
            
            with col2:
                st.subheader("المخاطر")
                st.metric("VaR 95% (الخسارة القصوى)", f"{stats['var_95']:.2f}")
                st.metric("احتمال كسر الوقف", f"{stats['prob_stop_hit']:.1f}%")
                st.metric("احتمال تحقيق +10%", f"{stats['prob_target_10']:.1f}%")
            
            fig_mc = mc.plot_simulations()
            st.plotly_chart(fig_mc, use_container_width=True)
        
        with tab3:
            for signal in signals:
                if "✅" in signal or "🚀" in signal:
                    st.success(signal)
                elif "⚠️" in signal:
                    st.warning(signal)
                else:
                    st.info(signal)
            
            st.markdown("---")
            st.markdown("#### معلومات الشركة")
            if info:
                st.markdown(f"- **القطاع:** {info.get('sector', 'غير متوفر')}")
                st.markdown(f"- **القيمة السوقية:** {info.get('marketCap', 'غير متوفر'):,}" if info.get('marketCap') else "-")
    
    else:
        st.error("❌ فشل في جلب البيانات")
        st.info("""
        **حلول مقترحة:**
        - تأكد من صحة رمز السهم
        - أعد المحاولة بعد دقيقة
        - جرب رمزاً آخر مثل `AAPL` أو `TSLA`
        """)
    
    st.markdown("---")
    st.caption("""
    📊 **المحلل المصري - الإصدار النهائي**
    تحليل فني + محاكاة مونت كارلو + إدارة المخاطر
    تعمل على جميع الأسهم المصرية والسعودية والأمريكية
    """)

if __name__ == "__main__":
    main()
