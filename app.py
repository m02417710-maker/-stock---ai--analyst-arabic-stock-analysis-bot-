# ============================================================
# ملف: stock_analyzer_complete.py
# المحلل المصري المتكامل - الإصدار الشامل
# يشمل: تحليل فني + مونت كارلو + بروفايل حجم + أخبار + تلجرام + AI + إدارة مخاطر
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
import time
import json

warnings.filterwarnings('ignore')

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="المحلل المصري المتكامل - الإصدار الشامل",
    page_icon="📊",
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
    border: 1px solid #10b981;
    border-radius: 15px;
    padding: 15px;
}
.quantum-card {
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
.golden-signal {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 3px solid #10b981;
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    animation: pulse 0.5s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# قائمة الأسهم الشاملة (جميع البورصات)
# ============================================================

EGYPT_STOCKS = {
    "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
    "🇪🇬 طلعت مصطفى القابضة": "TMGH.CA",
    "🇪🇬 فوري لتكنولوجيا البنوك": "FWRY.CA",
    "🇪🇬 المجموعة المالية هيرميس": "HRHO.CA",
    "🇪🇬 حديد عز": "ESRS.CA",
    "🇪🇬 جهينة للصناعات الغذائية": "JUFO.CA",
    "🇪🇬 أبو قير للأسمدة": "ABUK.CA",
    "🇪🇬 بنك مصر": "BMEL.CA"
}

SAUDI_STOCKS = {
    "🇸🇦 أرامكو السعودية": "2222.SR",
    "🇸🇦 بنك الراجحي": "1120.SR",
    "🇸🇦 الاتصالات السعودية (STC)": "7010.SR",
    "🇸🇦 سابك": "2010.SR"
}

US_STOCKS = {
    "🇺🇸 آبل - Apple": "AAPL",
    "🇺🇸 تسلا - Tesla": "TSLA",
    "🇺🇸 مايكروسوفت - Microsoft": "MSFT",
    "🇺🇸 إنفيديا - NVIDIA": "NVDA",
    "🇺🇸 أمازون - Amazon": "AMZN",
    "🇺🇸 جوجل - Google": "GOOGL"
}

ALL_STOCKS = {**EGYPT_STOCKS, **SAUDI_STOCKS, **US_STOCKS}

# ============================================================
# إعدادات التنبيهات (تلجرام وبريد إلكتروني)
# ============================================================

def send_telegram_alert(message, bot_token=None, chat_id=None):
    """إرسال تنبيه عبر تلجرام"""
    try:
        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        return False
    except:
        return False

def send_email_alert(sender, password, receiver, subject, body):
    """إرسال تنبيه عبر البريد الإلكتروني"""
    try:
        import smtplib
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart
        
        msg = MimeMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MimeText(body, 'html'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ============================================================
# 1. محرك مونت كارلو (للتوقعات الاحتمالية)
# ============================================================

class MonteCarloEngine:
    """محاكاة مونت كارلو باستخدام العوائد اللوغاريتمية"""
    
    def __init__(self, df, days=30, simulations=5000):
        self.df = df
        self.days = days
        self.simulations = simulations
        self.last_price = df['Close'].iloc[-1]
        
        # العوائد اللوغاريتمية
        self.log_returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        
        if len(self.log_returns) < 5:
            self.mu = 0.0005
            self.sigma = 0.02
        else:
            self.mu = self.log_returns.mean()
            self.sigma = self.log_returns.std()
        
        self.volatility = self.sigma * np.sqrt(252) if self.sigma else 0.2
    
    def run_simulation(self):
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
        final_prices = self.results[-1, :]
        
        return {
            "expected_price": np.mean(final_prices),
            "median_price": np.median(final_prices),
            "confidence_5": np.percentile(final_prices, 5),
            "confidence_25": np.percentile(final_prices, 25),
            "confidence_75": np.percentile(final_prices, 75),
            "confidence_95": np.percentile(final_prices, 95),
            "var_95": self.last_price - np.percentile(final_prices, 5),
            "var_99": self.last_price - np.percentile(final_prices, 1),
            "profit_probability": np.sum(final_prices > self.last_price) / self.simulations * 100,
            "prob_target_5": np.sum(final_prices >= self.last_price * 1.05) / self.simulations * 100,
            "prob_target_10": np.sum(final_prices >= self.last_price * 1.10) / self.simulations * 100,
            "prob_stop_hit": np.sum(final_prices <= self.last_price * 0.95) / self.simulations * 100,
            "volatility": self.volatility * 100
        }
    
    def plot_simulations(self):
        fig = go.Figure()
        
        # عينة من المسارات
        sample_paths = np.random.choice(self.simulations, min(100, self.simulations), replace=False)
        for i in sample_paths:
            fig.add_trace(go.Scatter(y=self.results[:, i], mode='lines',
                                     line=dict(width=0.5, color='rgba(16, 185, 129, 0.1)'), showlegend=False))
        
        # المتوسط
        mean_path = np.mean(self.results, axis=1)
        fig.add_trace(go.Scatter(y=mean_path, mode='lines', name='المتوسط المتوقع',
                                 line=dict(color='#10b981', width=3)))
        
        # نطاقات الثقة
        upper_95 = np.percentile(self.results, 95, axis=1)
        lower_95 = np.percentile(self.results, 5, axis=1)
        
        fig.add_trace(go.Scatter(y=upper_95, fill=None, mode='lines',
                                 line=dict(color='rgba(16, 185, 129, 0.3)'), name='حد أعلى 95%'))
        fig.add_trace(go.Scatter(y=lower_95, fill='tonexty', mode='lines',
                                 line=dict(color='rgba(16, 185, 129, 0.3)'), name='حد أدنى 95%'))
        
        fig.update_layout(template="plotly_dark", height=500,
                         title="📊 محاكاة مونت كارلو - 5,000 سيناريو")
        return fig

# ============================================================
# 2. محرك بروفايل الحجم (Volume Profile)
# ============================================================

class VolumeProfileEngine:
    """تحليل بروفايل الحجم - مناطق التراكم والتوزيع"""
    
    def __init__(self, df, num_bins=50):
        self.df = df
        self.num_bins = num_bins
        self.current_price = df['Close'].iloc[-1]
    
    def calculate_volume_profile(self):
        prices = self.df['Close'].values
        volumes = self.df['Volume'].values
        
        price_min, price_max = prices.min(), prices.max()
        bins = np.linspace(price_min, price_max, self.num_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        volume_profile = np.zeros(self.num_bins)
        
        for price, volume in zip(prices, volumes):
            bin_idx = np.digitize(price, bins) - 1
            if 0 <= bin_idx < self.num_bins:
                volume_profile[bin_idx] += volume
        
        if volume_profile.max() > 0:
            volume_profile = volume_profile / volume_profile.max() * 100
        
        high_volume_zones = []
        for i, vol in enumerate(volume_profile):
            if vol > 70:
                high_volume_zones.append({
                    "price": bin_centers[i],
                    "strength": vol,
                    "type": "تجميع" if bin_centers[i] < self.current_price else "توزيع"
                })
        
        poc_idx = np.argmax(volume_profile)
        point_of_control = bin_centers[poc_idx]
        
        return {
            "volume_profile": volume_profile,
            "bin_centers": bin_centers,
            "high_volume_zones": high_volume_zones,
            "point_of_control": point_of_control
        }
    
    def plot_volume_profile(self, profile_data):
        fig = go.Figure()
        
        fig.add_trace(go.Bar(x=profile_data['volume_profile'], y=profile_data['bin_centers'],
                             orientation='h', name='حجم التداول',
                             marker_color='rgba(16, 185, 129, 0.7)'))
        
        fig.add_vline(x=self.current_price, line_dash="dash", line_color="#f59e0b",
                     annotation_text=f"السعر: {self.current_price:.2f}")
        fig.add_hline(y=profile_data['point_of_control'], line_dash="solid", line_color="#10b981",
                     annotation_text=f"نقطة التحكم: {profile_data['point_of_control']:.2f}")
        
        fig.update_layout(template="plotly_dark", height=500,
                         title="📊 بروفايل الحجم - خريطة السيولة")
        return fig

# ============================================================
# 3. محرك الأخبار والتحليل الإخباري
# ============================================================

def get_stock_news(ticker):
    """جلب آخر أخبار السهم"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if news and len(news) > 0:
            news_items = []
            for item in news[:5]:
                news_items.append({
                    "title": item.get('title', 'عنوان غير متوفر'),
                    "publisher": item.get('publisher', 'مصدر غير معروف'),
                    "link": item.get('link', '#'),
                    "time": datetime.now().strftime("%H:%M")
                })
            return news_items
        return []
    except:
        return []

def analyze_news_sentiment(news_items):
    """تحليل المشاعر من الأخبار"""
    if not news_items:
        return 50, "لا توجد أخبار"
    
    positive_keywords = ["ارتفاع", "صعود", "أرباح", "توزيعات", "نمو", "توسع"]
    negative_keywords = ["انخفاض", "هبوط", "خسائر", "تحذير", "أزمة"]
    
    score = 50
    for item in news_items:
        title = item['title'].lower()
        for word in positive_keywords:
            if word in title:
                score += 2
        for word in negative_keywords:
            if word in title:
                score -= 2
    
    score = max(0, min(100, score))
    
    if score >= 70:
        sentiment = "🟢 أخبار إيجابية - دعم للسهم"
    elif score >= 50:
        sentiment = "🟡 أخبار محايدة"
    else:
        sentiment = "🔴 أخبار سلبية - ضغط على السهم"
    
    return score, sentiment

# ============================================================
# 4. محرك الاقتصاد الكلي (مايو 2026)
# ============================================================

def get_macro_impact():
    """تحليل تأثير الاقتصاد الكلي"""
    macro_factors = [
        "✅ تثبيت الفائدة عند 19% - إيجابي للبورصة",
        "✅ طرح 10 شركات بترول - زيادة فرص الاستثمار",
        "✅ زيادة تحويلات المصريين 29.6% - سيولة إضافية",
        "⚠️ تفعيل البيع على المكشوف - تقلبات أعلى"
    ]
    
    macro_score = 3  # من 5
    return macro_score, macro_factors

# ============================================================
# 5. محرك الأحداث الخاصة بالشركات (مايو 2026)
# ============================================================

COMPANY_EVENTS = {
    "ABUK.CA": {"event": "ارتفاع أسعار الأسمدة", "impact": "إيجابي قوي", "detail": "قفزة أسعار اليوريا لـ 850$"},
    "COMI.CA": {"event": "توزيع أرباح", "impact": "إيجابي", "detail": "توزيع 3 جنيه للسهم"},
    "TMGH.CA": {"event": "جمعية عمومية", "impact": "محايد", "detail": "مناقشة توسعات جديدة"}
}

def get_company_event(ticker):
    """جلب أحداث الشركة"""
    return COMPANY_EVENTS.get(ticker, None)

# ============================================================
# 6. محرك إدارة المخاطر
# ============================================================

def calculate_position_size(capital, price, stop_loss, risk_percent=2):
    """حساب حجم الصفقة المثالي"""
    if stop_loss <= 0 or price <= stop_loss:
        return 0, 0, 0
    
    risk_amount = capital * (risk_percent / 100)
    stop_distance = price - stop_loss
    shares = int(risk_amount / stop_distance)
    total_cost = shares * price
    actual_risk = (total_cost / capital) * 100
    
    return shares, round(total_cost, 2), round(actual_risk, 1)

# ============================================================
# 7. الدوال الأساسية للتحليل الفني
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

def calculate_technical_score(df):
    """حساب درجة الثقة الفنية"""
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
    
    # حجم التداول
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 2:
        signals.append(f"💰 سيولة عالية جداً ({vol_ratio:.1f}x)")
        score += 1
    elif vol_ratio > 1.5:
        signals.append(f"💰 سيولة جيدة ({vol_ratio:.1f}x)")
        score += 0.5
    
    return min(max(score, 0), 5), signals

def get_golden_signal(tech_score, mc_stats, news_score, macro_score):
    """توليد الإشارة الذهبية"""
    total_score = (tech_score * 0.3) + ((mc_stats['profit_probability'] / 100) * 0.3) + ((news_score / 100) * 0.2) + ((macro_score / 5) * 0.2)
    total_score = min(max(total_score, 0), 5)
    
    if total_score >= 4:
        return "🟢 إشارة ذهبية - فرصة شراء قوية", total_score
    elif total_score >= 3:
        return "📈 إشارة شراء محتملة", total_score
    elif total_score >= 2:
        return "🟡 مراقبة - انتظار تأكيد", total_score
    else:
        return "🔴 تجنب - إشارات سلبية", total_score

# ============================================================
# 8. الرسم البياني المتقدم
# ============================================================

def create_advanced_chart(df, ticker, target, stop, stock_name):
    """رسم بياني متقدم جميع المؤشرات"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=("السعر مع المتوسطات والمستهدفات", "مؤشر RSI", "مؤشر MACD", "حجم التداول")
    )
    
    # الشموع اليابانية
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                  low=df['Low'], close=df['Close'], name="السعر"), row=1, col=1)
    
    # المتوسطات المتحركة
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA 20",
                             line=dict(color='#f59e0b', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA 50",
                             line=dict(color='#10b981', width=1.5)), row=1, col=1)
    
    # خط الهدف ووقف الخسارة
    if target > 0:
        fig.add_hline(y=target, line_dash="dash", line_color="#10b981",
                     annotation_text=f"🎯 الهدف: {target:.2f}", row=1, col=1)
    if stop > 0:
        fig.add_hline(y=stop, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"🛑 وقف: {stop:.2f}", row=1, col=1)
    
    # Bollinger Bands
    if 'BBU_20_2.0' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], name="BB علوي",
                                 line=dict(color='#94a3b8', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], name="BB سفلي",
                                 line=dict(color='#94a3b8', dash='dash'),
                                 fill='tonexty', fillcolor='rgba(148,163,184,0.1)'), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                             line=dict(color='#8b5cf6', width=2)), row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    
    # MACD
    if 'MACD_12_26_9' in df.columns:
        macd_hist = df['MACD_12_26_9'] - df['MACDs_12_26_9']
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in macd_hist]
        fig.add_trace(go.Bar(x=df.index, y=macd_hist, name="Histogram",
                             marker_color=colors, opacity=0.7), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name="MACD",
                                 line=dict(color='#3b82f6', width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name="Signal",
                                 line=dict(color='#f59e0b', width=2)), row=3, col=1)
    
    # حجم التداول
    volume_colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
                     for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم",
                         marker_color=volume_colors, opacity=0.7), row=4, col=1)
    
    fig.update_layout(template="plotly_dark", height=800, title=f"التحليل الفني لسهم {stock_name}",
                      margin=dict(l=10, r=10, t=60, b=10))
    
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="الحجم", row=4, col=1)
    
    return fig

# ============================================================
# 9. ماسح السوق (Market Scanner)
# ============================================================

def scan_all_stocks():
    """مسح جميع الأسهم للبحث عن فرص"""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (name, ticker) in enumerate(ALL_STOCKS.items()):
        status_text.text(f"جاري مسح: {name}...")
        df, _ = get_stock_data(ticker)
        
        if df is not None and not df.empty:
            score, _ = calculate_technical_score(df)
            current_price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            
            if score >= 4:
                signal = "🟢 فرصة شراء قوية"
            elif score >= 3:
                signal = "📈 فرصة شراء"
            elif score <= 1.5:
                signal = "🔴 إشارة بيع"
            else:
                signal = "🟡 مراقبة"
            
            results.append({
                "السهم": name,
                "الرمز": ticker,
                "السعر": round(current_price, 2),
                "RSI": round(rsi, 1),
                "الدرجة": score,
                "الإشارة": signal
            })
        
        progress_bar.progress((idx + 1) / len(ALL_STOCKS))
        time.sleep(0.05)
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results).sort_values("الدرجة", ascending=False)

# ============================================================
# 10. الواجهة الرئيسية
# ============================================================

def main():
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("# 📊 المحلل المصري المتكامل")
        st.markdown("### الإصدار الشامل - مايو 2026")
        st.markdown("---")
        
        # اختيار البورصة
        market = st.radio("اختر البورصة", ["🇪🇬 مصر", "🇸🇦 السعودية", "🇺🇸 أمريكا", "🌍 الجميع"], index=0)
        
        st.markdown("---")
        
        # اختيار السهم
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
        
        # إدارة رأس المال
        st.markdown("### 💰 إدارة رأس المال")
        capital = st.number_input("رأس المال ($)", min_value=1000, value=10000, step=1000)
        
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("🔄 تحديث شامل", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # العنوان الرئيسي
    st.markdown(f"## 📈 التحليل المتكامل لسهم {selected}")
    st.markdown(f"### {ticker}")
    st.markdown("---")
    
    # جلب البيانات
    with st.spinner("جاري تحليل البيانات..."):
        df, info = get_stock_data(ticker)
    
    if df is not None and not df.empty:
        # ===== التحليل الأساسي =====
        tech_score, tech_signals = calculate_technical_score(df)
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        # ===== محاكاة مونت كارلو =====
        with st.spinner("تشغيل محاكاة مونت كارلو..."):
            mc_engine = MonteCarloEngine(df, days=30, simulations=5000)
            mc_stats = mc_engine.run_simulation()
        
        # ===== بروفايل الحجم =====
        with st.spinner("تحليل بروفايل الحجم..."):
            vp_engine = VolumeProfileEngine(df)
            vp_data = vp_engine.calculate_volume_profile()
        
        # ===== الأخبار وتحليل المشاعر =====
        news_items = get_stock_news(ticker)
        news_score, news_sentiment = analyze_news_sentiment(news_items)
        
        # ===== الاقتصاد الكلي =====
        macro_score, macro_factors = get_macro_impact()
        
        # ===== أحداث الشركة =====
        company_event = get_company_event(ticker)
        
        # ===== الأهداف ووقف الخسارة =====
        target = mc_stats['confidence_75'] if mc_stats['confidence_75'] > current_price else current_price * 1.07
        stop = mc_stats['confidence_25'] if mc_stats['confidence_25'] < current_price else current_price * 0.95
        
        # ===== حجم الصفقة المقترح =====
        shares, total_cost, actual_risk = calculate_position_size(capital, current_price, stop)
        
        # ===== الإشارة الذهبية =====
        golden_signal, final_score = get_golden_signal(tech_score, mc_stats, news_score, macro_score)
        
        # ===== البطاقات الرئيسية =====
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 السعر", f"{current_price:.2f}", f"{price_change:+.2f}%")
        col2.metric("📊 RSI", f"{df['RSI'].iloc[-1]:.1f}")
        col3.metric("🎯 درجة الثقة", f"{tech_score}/5")
        col4.metric("🔮 الهدف", f"{target:.2f}")
        
        # صف ثاني
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🎲 احتمال الربح", f"{mc_stats['profit_probability']:.1f}%")
        col2.metric("⚠️ VaR 95%", f"{mc_stats['var_95']:.2f}")
        col3.metric("📰 تحليل الأخبار", f"{news_score}/100")
        col4.metric("🌍 الاقتصاد الكلي", f"{macro_score}/5")
        
        st.markdown("---")
        
        # ===== الإشارة الذهبية =====
        if final_score >= 4:
            st.markdown(f"""
            <div class="golden-signal">
                <h1 style="color: #10b981; margin: 0;">{golden_signal}</h1>
                <p style="color: #d1d5db; margin-top: 10px;">الدرجة النهائية: {final_score:.1f}/5</p>
                <p>🎯 الهدف: {target:.2f} | 🛑 وقف الخسارة: {stop:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="quantum-card">
                <h3 style="color: {'#10b981' if final_score >= 3 else '#f59e0b'}">{golden_signal}</h3>
                <p>الدرجة النهائية: {final_score:.1f}/5 | 🎯 الهدف: {target:.2f} | 🛑 وقف: {stop:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ===== إدارة المخاطر =====
        with st.expander("📊 تفاصيل إدارة المخاطر", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 رأس المال", f"${capital:,}")
            col2.metric("📈 عدد الأسهم المقترح", f"{shares} سهم")
            col3.metric("💵 قيمة الصفقة", f"${total_cost:,}")
            st.info(f"⚠️ نسبة المخاطرة الفعلية: {actual_risk}% من رأس المال - يوصى بعدم تجاوز 2%")
        
        # ===== التبويبات =====
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 الرسم البياني", "🔮 مونت كارلو", "📊 بروفايل الحجم",
            "📰 الأخبار", "🌍 التحليل الشامل", "🔍 ماسح السوق"
        ])
        
        with tab1:
            fig = create_advanced_chart(df, ticker, target, stop, selected)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("السعر المتوقع", f"{mc_stats['expected_price']:.2f}")
                st.metric("نطاق 90% ثقة", f"{mc_stats['confidence_5']:.2f} - {mc_stats['confidence_95']:.2f}")
                st.metric("التذبذب السنوي", f"{mc_stats['volatility']:.1f}%")
            with col2:
                st.metric("احتمال +5%", f"{mc_stats['prob_target_5']:.1f}%")
                st.metric("احتمال +10%", f"{mc_stats['prob_target_10']:.1f}%")
                st.metric("احتمال كسر الوقف", f"{mc_stats['prob_stop_hit']:.1f}%")
            
            fig_mc = mc_engine.plot_simulations()
            st.plotly_chart(fig_mc, use_container_width=True)
        
        with tab3:
            fig_vp = vp_engine.plot_volume_profile(vp_data)
            st.plotly_chart(fig_vp, use_container_width=True)
            
            if vp_data['high_volume_zones']:
                st.subheader("🔥 مناطق تركيز السيولة")
                for zone in vp_data['high_volume_zones'][:5]:
                    st.info(f"{'🟢 تجميع' if zone['type'] == 'تجميع' else '🔴 توزيع'} عند {zone['price']:.2f} (قوة {zone['strength']:.0f}%)")
        
        with tab4:
            st.subheader("📰 آخر الأخبار")
            if news_items:
                for item in news_items:
                    st.markdown(f"""
                    <div style="background: #1e293b; border-radius: 10px; padding: 10px; margin: 5px 0; border-right: 3px solid #10b981;">
                        <strong>📌 {item['title']}</strong><br>
                        <small>📢 {item['publisher']} | 🕐 {item['time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"**📊 تحليل المشاعر:** {news_sentiment} (الدرجة: {news_score}/100)")
            else:
                st.info("لا توجد أخبار حديثة متاحة حالياً")
        
        with tab5:
            st.subheader("🌍 التحليل الشامل")
            
            st.markdown("### الاقتصاد الكلي - مايو 2026")
            for factor in macro_factors:
                if "✅" in factor:
                    st.success(factor)
                else:
                    st.warning(factor)
            
            if company_event:
                st.markdown("### 📅 أحداث الشركة")
                st.info(f"**{company_event['event']}** - {company_event['impact']}\n{company_event['detail']}")
            
            st.markdown("### 📊 تفاصيل التحليل الفني")
            for signal in tech_signals:
                if "✅" in signal or "💰" in signal:
                    st.success(signal)
                elif "⚠️" in signal:
                    st.warning(signal)
                else:
                    st.info(signal)
        
        with tab6:
            st.subheader("🔍 ماسح السوق الذكي")
            
            if st.button("🚀 تشغيل الماسح الضوئي", use_container_width=True):
                with st.spinner("جاري مسح جميع الأسهم..."):
                    scan_results = scan_all_stocks()
                    if not scan_results.empty:
                        st.success(f"✅ تم مسح {len(scan_results)} سهماً")
                        st.dataframe(scan_results, use_container_width=True, hide_index=True)
                        
                        # أفضل الفرص
                        st.subheader("🏆 أفضل فرص الشراء")
                        top_opportunities = scan_results[scan_results['الإشارة'].str.contains("شراء")].head(5)
                        if not top_opportunities.empty:
                            for _, row in top_opportunities.iterrows():
                                st.info(f"📈 {row['السهم']} - {row['الإشارة']} | السعر: {row['السعر']} | RSI: {row['RSI']}")
                    else:
                        st.warning("لا توجد بيانات كافية للمسح")
    
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
    📊 **المحلل المصري المتكامل - الإصدار الشامل**
    
    **الميزات المتضمنة:**
    ✅ تحليل فني متقدم (RSI, MACD, Bollinger Bands, المتوسطات المتحركة)
    ✅ محاكاة مونت كارلو (5,000 سيناريو - توقعات احتمالية)
    ✅ بروفايل الحجم الحقيقي (خريطة السيولة)
    ✅ تحليل الأخبار والمشاعر
    ✅ الاقتصاد الكلي المصري (مايو 2026)
    ✅ إدارة المخاطر (حجم الصفقة - وقف الخسارة)
    ✅ ماسح السوق الذكي (فرص الاستثمار)
    ✅ جميع البورصات (مصر - السعودية - أمريكا)
    🔄 تحديث تلقائي كل 60 ثانية
    """)

if __name__ == "__main__":
    main()
