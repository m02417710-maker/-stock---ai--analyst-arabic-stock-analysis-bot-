# ============================================================
# core.py - المحرك الأساسي (مصحح)
# تم التصحيح: جميع الدوال تبدأ بـ def (حرف صغير)
# ============================================================

import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings('ignore')

# ============================================================
# قائمة الأسهم - في المستوى العام (بدون مسافات قبلها)
# ============================================================

STOCKS = {
    "🇪🇬 البنك التجاري الدولي": "COMI.CA",
    "🇪🇬 طلعت مصطفى": "TMGH.CA",
    "🇪🇬 فوري": "FWRY.CA",
    "🇪🇬 حديد عز": "ESRS.CA",
    "🇪🇬 أبو قير للأسمدة": "ABUK.CA",
    "🇪🇬 جهينة": "JUFO.CA",
    "🇸🇦 أرامكو": "2222.SR",
    "🇸🇦 الراجحي": "1120.SR",
    "🇺🇸 آبل": "AAPL",
    "🇺🇸 تسلا": "TSLA",
    "🇺🇸 مايكروسوفت": "MSFT",
    "🇺🇸 إنفيديا": "NVDA",
}

# ============================================================
# جلب البيانات
# ============================================================

def get_data(ticker):
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo", interval="1d")
        
        if df.empty or len(df) < 10:
            return None, None
        
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        
        macd = ta.macd(df['Close'])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        
        df['Volume_MA'] = df['Volume'].rolling(20).mean()
        df['Support'] = df['Low'].rolling(20).min()
        df['Resistance'] = df['High'].rolling(20).max()
        
        return df, stock.info
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None, None

# ============================================================
# التحليل الفني
# ============================================================

def analyze(df):
    """تحليل السهم وإعطاء درجة وإشارات"""
    if df is None or len(df) < 20:
        return 0, [], "لا توجد بيانات", "#6b7280"
    
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
        signals.append(f"🔥 RSI {rsi:.1f} - منطقة شراء ممتازة")
    elif rsi > 70:
        score -= 1
        signals.append(f"⚠️ RSI {rsi:.1f} - منطقة بيع")
    else:
        score += 0.5
        signals.append(f"✅ RSI {rsi:.1f} - طبيعي")
    
    # حجم التداول
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 2:
        score += 1
        signals.append(f"💰 حجم قياسي ({vol_ratio:.1f}x)")
    elif vol_ratio > 1.5:
        score += 0.5
        signals.append(f"📊 حجم مرتفع ({vol_ratio:.1f}x)")
    
    # MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1
            signals.append("🚀 MACD إيجابي")
        else:
            score -= 0.5
            signals.append("📉 MACD سلبي")
    
    score = min(max(score, 0), 5)
    
    if score >= 4:
        rec, color = "🟢 شراء قوي", "#10b981"
    elif score >= 3:
        rec, color = "📈 شراء محتمل", "#3b82f6"
    elif score >= 2:
        rec, color = "🟡 مراقبة", "#f59e0b"
    else:
        rec, color = "🔴 تجنب", "#ef4444"
    
    return score, signals, rec, color

# ============================================================
# مونت كارلو
# ============================================================

def monte_carlo_gbm(df, days=30, sims=2000):
    """محاكاة مونت كارلو"""
    if df is None or len(df) < 20:
        return None
    
    try:
        last_price = df['Close'].iloc[-1]
        returns = df['Close'].pct_change().dropna()
        
        mu = returns.mean()
        sigma = returns.std()
        dt = 1 / 252
        
        results = np.zeros((days, sims))
        np.random.seed(42)
        
        for i in range(sims):
            prices = [last_price]
            shocks = np.random.normal(0, 1, days - 1)
            for j in range(days - 1):
                price = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * shocks[j] * np.sqrt(dt))
                prices.append(price)
            results[:, i] = prices
        
        final = results[-1, :]
        
        return {
            "expected": np.mean(final),
            "best_95": np.percentile(final, 95),
            "worst_5": np.percentile(final, 5),
            "var_95_pct": ((last_price - np.percentile(final, 5)) / last_price) * 100,
            "profit_prob": np.sum(final > last_price) / sims * 100,
            "target_10_prob": np.sum(final >= last_price * 1.10) / sims * 100,
            "stop_prob": np.sum(final <= last_price * 0.95) / sims * 100,
        }
    except:
        return None

# ============================================================
# الرسم البياني
# ============================================================

def create_chart(df, ticker, name, target=None, stop=None):
    """إنشاء رسم بياني متكامل"""
    if df is None or df.empty:
        return None
    
    last_price = df['Close'].iloc[-1]
    target = target or (df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else last_price * 1.07)
    stop = stop or last_price * 0.95
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=("السعر مع المتوسطات", "RSI", "حجم التداول")
    )
    
    # الشموع
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="السعر"
    ), row=1, col=1)
    
    # المتوسطات
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20",
                             line=dict(color='#f59e0b')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50",
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
    
    # الحجم
    colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
              for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="الحجم",
                         marker_color=colors), row=3, col=1)
    
    fig.update_layout(
        template="plotly_dark",
        height=600,
        title=f"تحليل سهم {name}",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    
    return fig

# ============================================================
# إدارة المخاطر
# ============================================================

def risk_management(capital, price, stop_percent=5, risk_percent=2):
    """حساب حجم الصفقة"""
    if capital <= 0 or price <= 0:
        return 0, 0, 0, "بيانات غير صالحة"
    
    risk_amount = capital * (risk_percent / 100)
    stop_loss = price * (1 - stop_percent / 100)
    stop_distance = price - stop_loss
    
    if stop_distance <= 0:
        return 0, 0, 0, "خطأ: وقف خسارة غير صالح"
    
    shares = int(risk_amount / stop_distance)
    position = shares * price
    actual_risk = (position / capital) * 100
    
    if actual_risk > risk_percent:
        advice = f"⚠️ المخاطرة ({actual_risk:.1f}%) تتجاوز الحد المسموح"
    else:
        advice = f"✅ مناسب: المخاطرة ضمن الحدود"
    
    return shares, round(position, 2), round(actual_risk, 1), advice

# ============================================================
# ماسح السوق
# ============================================================

def scan_market_parallel():
    """مسح جميع الأسهم"""
    results = []
    
    for name, ticker in STOCKS.items():
        df, _ = get_data(ticker)
        if df is not None and not df.empty:
            score, _, rec, _ = analyze(df)
            price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            
            results.append({
                "السهم": name,
                "السعر": round(price, 2),
                "RSI": round(rsi, 1),
                "الدرجة": score,
                "التوصية": rec
            })
    
    return pd.DataFrame(results).sort_values("الدرجة", ascending=False)
