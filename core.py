# ============================================================
# core.py - المحرك الأساسي
# تم تصحيح: جميع الدوال تبدأ بـ def (حرف صغير)
# ============================================================

import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

warnings.filterwarnings('ignore')

# ============================================================
# قائمة الأسهم
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
    if rsi < 25:
        score += 2
        signals.append(f"🔥🔥 RSI {rsi:.1f} - ذروة بيع شديدة")
    elif rsi < 30:
        score += 1.5
        signals.append(f"🔥 RSI {rsi:.1f} - منطقة شراء ممتازة")
    elif rsi < 40:
        score += 1
        signals.append(f"📈 RSI {rsi:.1f} - منطقة تجميع")
    elif rsi > 75:
        score -= 1.5
        signals.append(f"⚠️⚠️ RSI {rsi:.1f} - ذروة شراء شديدة")
    elif rsi > 70:
        score -= 1
        signals.append(f"⚠️ RSI {rsi:.1f} - منطقة بيع")
    else:
        score += 0.5
        signals.append(f"✅ RSI {rsi:.1f} - طبيعي")
    
    # الحجم
    vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
    if vol_ratio > 2.5:
        score += 1.5
        signals.append(f"💰💰 حجم قياسي ({vol_ratio:.1f}x)")
    elif vol_ratio > 2:
        score += 1
        signals.append(f"💰 حجم مرتفع جداً ({vol_ratio:.1f}x)")
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
    
    if score >= 4.5:
        rec, color = "🔥🔥 شراء قوي جداً", "#10b981"
    elif score >= 3.5:
        rec, color = "🟢 شراء قوي", "#22c55e"
    elif score >= 2.5:
        rec, color = "📈 شراء محتمل", "#3b82f6"
    elif score >= 1.5:
        rec, color = "🟡 مراقبة", "#f59e0b"
    else:
        rec, color = "🔴 تجنب", "#ef4444"
    
    return score, signals, rec, color

# ============================================================
# مونت كارلو
# ============================================================

def monte_carlo_gbm(df, days=30, sims=3000):
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
            "median": np.median(final),
            "best_95": np.percentile(final, 95),
            "worst_5": np.percentile(final, 5),
            "var_95": last_price - np.percentile(final, 5),
            "var_99": last_price - np.percentile(final, 1),
            "var_95_pct": ((last_price - np.percentile(final, 5)) / last_price) * 100,
            "profit_prob": np.sum(final > last_price) / sims * 100,
            "target_5_prob": np.sum(final >= last_price * 1.05) / sims * 100,
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
    resistance = df['Resistance'].iloc[-1] if not pd.isna(df['Resistance'].iloc[-1]) else last_price * 1.07
    support = df['Support'].iloc[-1] if not pd.isna(df['Support'].iloc[-1]) else last_price * 0.93
    
    target = target or resistance
    stop = stop or support
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=("السعر مع المتوسطات", "RSI", "MACD", "حجم التداول")
    )
    
    # الشموع اليابانية
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="السعر"
    ), row=1, col=1)
    
    # المتوسطات المتحركة
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20",
                             line=dict(color='#f59e0b', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50",
                             line=dict(color='#10b981', width=1.5)), row=1, col=1)
    
    # الهدف ووقف الخسارة
    if target > 0:
        fig.add_hline(y=target, line_dash="dash", line_color="#10b981",
                     annotation_text=f"🎯 الهدف: {target:.2f}", 
                     annotation_position="top right", row=1, col=1)
    if stop > 0:
        fig.add_hline(y=stop, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"🛑 وقف: {stop:.2f}",
                     annotation_position="bottom right", row=1, col=1)
    
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
    
    fig.update_layout(
        title=f"📊 التحليل الفني لسهم {name} ({ticker})",
        template="plotly_dark",
        height=700,
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
# إدارة المخاطر
# ============================================================

def risk_management(capital, price, stop_percent=5, risk_percent=2):
    """حساب حجم الصفقة المناسب"""
    if capital <= 0 or price <= 0:
        return 0, 0, 0, "بيانات غير صالحة"
    
    risk_amount = capital * (risk_percent / 100)
    stop_loss = price * (1 - stop_percent / 100)
    stop_distance = price - stop_loss
    
    if stop_distance <= 0:
        return 0, 0, 0, "خطأ: إعداد وقف الخسارة غير صالح"
    
    shares = int(risk_amount / stop_distance)
    position = shares * price
    actual_risk = (position / capital) * 100
    
    if actual_risk > risk_percent:
        advice = f"⚠️ المخاطرة الفعلية ({actual_risk:.1f}%) تتجاوز الحد المسموح ({risk_percent}%)"
    elif actual_risk < risk_percent * 0.5:
        advice = f"✅ مخاطرة منخفضة ({actual_risk:.1f}%) - يمكن زيادة الحجم"
    else:
        advice = f"✅ مناسب: المخاطرة ضمن الحدود المسموحة"
    
    return shares, round(position, 2), round(actual_risk, 1), advice

# ============================================================
# ماسح السوق (متوازي)
# ============================================================

def scan_market_parallel():
    """مسح جميع الأسهم بالتوازي"""
    results = []
    
    def scan_one(item):
        name, ticker = item
        df, _ = get_data(ticker)
        if df is not None and not df.empty:
            score, _, rec, _ = analyze(df)
            price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
            return {
                "السهم": name,
                "السعر": round(price, 2),
                "RSI": round(rsi, 1),
                "الدرجة": score,
                "التوصية": rec
            }
        return None
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scan_one, item): item for item in STOCKS.items()}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return pd.DataFrame(results).sort_values("الدرجة", ascending=False)
