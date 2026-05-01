# app.py - التطبيق الرئيسي الكامل مع التحليل الآلي
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة أولاً
st.set_page_config(
    page_title="Stock AI Analyst Pro - التحليل الآلي 🏢",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== التهيئة الأمنية ======================
from security import initialize_security, validate_ticker, get_safe_ticker
initialize_security()

# ====================== الاستيرادات ======================
from pathlib import Path
import tempfile
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import pandas_ta as ta
from datetime import datetime
import io
from typing import Dict, Optional, List, Any

# استيراد core
try:
    import core
    from core import STOCKS, get_stock_list, get_stock_ticker, search_stocks
    STOCK_NAMES = list(STOCKS.keys()) if STOCKS else []
except ImportError:
    STOCKS = {
        "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
        "🇸🇦 أرامكو السعودية": "2222.SR",
        "🇺🇸 Apple Inc.": "AAPL"
    }
    STOCK_NAMES = list(STOCKS.keys())

# تعريف الإصدار
try:
    from config import APP_VERSION
except ImportError:
    APP_VERSION = "5.0.0"

# ====================== إعداد Gemini ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي"""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        pass
    return None

# ====================== دوال التحليل الآلي ======================

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """حساب مؤشر RSI"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    except:
        return 50

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """حساب مؤشر MACD"""
    try:
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]
    except:
        return 0, 0, 0

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2):
    """حساب Bollinger Bands"""
    try:
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]
    except:
        return prices.iloc[-1], prices.iloc[-1], prices.iloc[-1]

def calculate_support_resistance(df: pd.DataFrame, lookback: int = 50) -> tuple:
    """حساب مستويات الدعم والمقاومة"""
    try:
        recent_data = df.tail(lookback)
        resistance = recent_data['High'].max()
        support = recent_data['Low'].min()
        return support, resistance
    except:
        return df['Low'].min(), df['High'].max()

def determine_trend(prices: pd.Series) -> str:
    """تحديد اتجاه السهم"""
    if len(prices) < 10:
        return "محايد"
    
    current = prices.iloc[-1]
    sma_10 = prices.tail(10).mean()
    sma_20 = prices.tail(20).mean() if len(prices) >= 20 else sma_10
    
    if current > sma_10 and current > sma_20:
        return "صاعد 📈"
    elif current < sma_10 and current < sma_20:
        return "هابط 📉"
    else:
        return "جانبي ↔️"

def calculate_technical_indicators(df: pd.DataFrame) -> Dict:
    """
    حساب المؤشرات الفنية بشكل آلي
    """
    if df is None or df.empty:
        return {}
    
    indicators = {}
    
    # السعر الحالي
    indicators['current_price'] = df['Close'].iloc[-1]
    
    # التغير اليومي
    if len(df) >= 2:
        prev_close = df['Close'].iloc[-2]
        indicators['daily_change'] = ((indicators['current_price'] - prev_close) / prev_close) * 100
    else:
        indicators['daily_change'] = 0
    
    # المتوسطات المتحركة
    indicators['sma_20'] = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else indicators['current_price']
    indicators['sma_50'] = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else indicators['current_price']
    
    # RSI
    indicators['rsi'] = calculate_rsi(df['Close'], 14)
    
    # MACD
    indicators['macd'], indicators['macd_signal'], indicators['macd_hist'] = calculate_macd(df['Close'])
    
    # Bollinger Bands
    indicators['bb_upper'], indicators['bb_middle'], indicators['bb_lower'] = calculate_bollinger_bands(df['Close'])
    
    # الدعم والمقاومة
    indicators['support'], indicators['resistance'] = calculate_support_resistance(df)
    
    # الحجم
    indicators['avg_volume'] = df['Volume'].tail(20).mean() if len(df) >= 20 else df['Volume'].mean()
    indicators['current_volume'] = df['Volume'].iloc[-1]
    
    # الاتجاه العام
    indicators['trend'] = determine_trend(df['Close'].tail(20))
    
    # أعلى وأدنى 52 أسبوع
    if len(df) >= 252:
        indicators['high_52w'] = df['High'].tail(252).max()
        indicators['low_52w'] = df['Low'].tail(252).min()
    else:
        indicators['high_52w'] = df['High'].max()
        indicators['low_52w'] = df['Low'].min()
    
    return indicators

def generate_technical_signal(indicators: Dict) -> Dict:
    """
    توليد إشارة فنية بناءً على المؤشرات
    """
    signal = {
        "type": "NEUTRAL",
        "strength": 0,
        "reasons": [],
        "action": "انتظار",
        "risk": "متوسطة",
        "confidence": 50
    }
    
    score = 0
    confidence = 50
    
    # تحليل RSI
    rsi = indicators.get('rsi', 50)
    if rsi > 70:
        score -= 2
        confidence -= 15
        signal['reasons'].append(f"⚠️ RSI مرتفع ({rsi:.1f}) - منطقة ذروة شراء")
        signal['risk'] = "عالية"
    elif rsi < 30:
        score += 2
        confidence += 15
        signal['reasons'].append(f"✅ RSI منخفض ({rsi:.1f}) - منطقة ذروة بيع (فرصة)")
        signal['risk'] = "منخفضة"
    else:
        signal['reasons'].append(f"📊 RSI محايد ({rsi:.1f})")
    
    # تحليل السعر مقابل المتوسطات
    current = indicators.get('current_price', 0)
    sma_20 = indicators.get('sma_20', current)
    sma_50 = indicators.get('sma_50', current)
    
    if current > sma_20 and current > sma_50:
        score += 1
        confidence += 10
        signal['reasons'].append("📈 السعر أعلى من المتوسطات (اتجاه صاعد)")
    elif current < sma_20 and current < sma_50:
        score -= 1
        confidence -= 10
        signal['reasons'].append("📉 السعر أقل من المتوسطات (اتجاه هابط)")
    else:
        signal['reasons'].append("🔄 السعر قريب من المتوسطات")
    
    # تحليل MACD
    macd = indicators.get('macd', 0)
    macd_signal = indicators.get('macd_signal', 0)
    if macd > macd_signal:
        score += 1
        confidence += 10
        signal['reasons'].append("🟢 إشارة MACD إيجابية")
    elif macd < macd_signal:
        score -= 1
        confidence -= 10
        signal['reasons'].append("🔴 إشارة MACD سلبية")
    
    # تحليل الحجم
    current_volume = indicators.get('current_volume', 0)
    avg_volume = indicators.get('avg_volume', 1)
    if current_volume > avg_volume * 1.5:
        if score > 0:
            confidence += 10
            signal['reasons'].append("📊 حجم تداول مرتفع يدعم الاتجاه الصاعد")
        elif score < 0:
            confidence -= 10
            signal['reasons'].append("📊 حجم تداول مرتفع مع اتجاه هابط (خطر)")
    
    # تحديد الإشارة النهائية
    if score >= 2:
        signal['type'] = "BUY"
        signal['action'] = "شراء 🟢"
        signal['strength'] = min(score, 5)
    elif score <= -2:
        signal['type'] = "SELL"
        signal['action'] = "بيع 🔴"
        signal['strength'] = abs(min(score, -5))
    else:
        signal['type'] = "HOLD"
        signal['action'] = "انتظار 🟡"
        signal['strength'] = 1
    
    signal['confidence'] = min(max(confidence, 0), 100)
    
    return signal

def generate_ai_analysis(ticker: str, indicators: Dict, signal: Dict, model) -> str:
    """
    توليد تحليل بالذكاء الاصطناعي
    """
    if not model:
        return "❌ الذكاء الاصطناعي غير متوفر - أضف مفتاح API في secrets"
    
    prompt = f"""
أنت محلل أسهم محترف. قم بتحليل السهم {ticker} بناءً على البيانات التالية:

📊 **البيانات الفنية:**
- السعر الحالي: {indicators.get('current_price', 0):.2f}
- التغير اليومي: {indicators.get('daily_change', 0):.2f}%
- أعلى 52 أسبوع: {indicators.get('high_52w', 0):.2f}
- أدنى 52 أسبوع: {indicators.get('low_52w', 0):.2f}
- RSI (14): {indicators.get('rsi', 50):.1f}
- المتوسط المتحرك 20: {indicators.get('sma_20', 0):.2f}
- المتوسط المتحرك 50: {indicators.get('sma_50', 0):.2f}
- الاتجاه: {indicators.get('trend', 'محايد')}

📈 **المستويات:**
- الدعم: {indicators.get('support', 0):.2f}
- المقاومة: {indicators.get('resistance', 0):.2f}

🎯 **الإشارة الفنية:**
- التوصية: {signal.get('action', 'انتظار')}
- القوة: {signal.get('strength', 0)}/5
- الثقة: {signal.get('confidence', 50)}%

المطلوب:
1. تقييم عام للسهم
2. أهم نقاط القوة والضعف
3. توصية واضحة للمستثمر
4. مستوى المخاطرة المتوقع

الرد بالعربية بشكل مختصر ومفيد (حد أقصى 150 كلمة).
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ في التحليل: {str(e)}"

def render_analysis_section(indicators: Dict, signal: Dict):
    """
    عرض قسم التحليل بشكل جميل
    """
    st.markdown("### 📊 التحليل الفني الآلي")
    
    # عرض المؤشرات في أعمدة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 السعر الحالي", f"{indicators.get('current_price', 0):.2f}", 
                  delta=f"{indicators.get('daily_change', 0):+.2f}%")
    
    with col2:
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            rsi_status = "🟢 ذروة بيع"
        elif rsi > 70:
            rsi_status = "🔴 ذروة شراء"
        else:
            rsi_status = "🟡 محايد"
        st.metric(f"📊 RSI (14)", f"{rsi:.1f}", delta=rsi_status)
    
    with col3:
        st.metric("📈 الاتجاه", indicators.get('trend', 'محايد'))
    
    with col4:
        st.metric("🎯 التوصية", signal.get('action', 'انتظار'), 
                  delta=f"ثقة {signal.get('confidence', 50)}%")
    
    st.divider()
    
    # عرض المؤشرات الرئيسية
    st.markdown("#### 📋 ملخص الإشارات الفنية")
    
    col1, col2 = st.columns(2)
    with col1:
        for reason in signal.get('reasons', [])[:3]:
            st.write(f"• {reason}")
    with col2:
        for reason in signal.get('reasons', [])[3:6]:
            st.write(f"• {reason}")
    
    # عرض مستويات الدعم والمقاومة
    st.markdown("#### 🎯 المستويات الرئيسية")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🛡️ الدعم الرئيسي", f"{indicators.get('support', 0):.2f}")
    with col2:
        st.metric("⚡ المقاومة الرئيسية", f"{indicators.get('resistance', 0):.2f}")
    with col3:
        current = indicators.get('current_price', 0)
        support = indicators.get('support', 0)
        resistance = indicators.get('resistance', 0)
        if resistance > support:
            position = ((current - support) / (resistance - support)) * 100
            st.metric("📍 موقع السعر", f"{position:.0f}% بين الدعم والمقاومة")
    
    # عرض المؤشرات الإضافية
    with st.expander("📈 مؤشرات فنية متقدمة"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**MACD:** {indicators.get('macd', 0):.4f}")
            st.write(f"**MACD Signal:** {indicators.get('macd_signal', 0):.4f}")
            st.write(f"**المتوسط 20:** {indicators.get('sma_20', 0):.2f}")
            st.write(f"**المتوسط 50:** {indicators.get('sma_50', 0):.2f}")
        with col2:
            st.write(f"**متوسط حجم التداول:** {indicators.get('avg_volume', 0):,.0f}")
            st.write(f"**الحجم الحالي:** {indicators.get('current_volume', 0):,.0f}")
            st.write(f"**Bollinger وسط:** {indicators.get('bb_middle', 0):.2f}")
            ratio = indicators.get('current_volume', 0) / max(indicators.get('avg_volume', 1), 1)
            st.write(f"**نسبة الحجم:** {ratio:.2f}x")

def create_advanced_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """
    إنشاء رسم بياني متقدم
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=(f"السعر - {ticker}", "RSI (14)", "حجم التداول")
    )
    
    # سعر الإغلاق
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        name="السعر",
        line=dict(color='cyan', width=2)
    ), row=1, col=1)
    
    # المتوسطات المتحركة
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_20'],
            name="SMA 20",
            line=dict(color='orange', width=1.5, dash='dash')
        ), row=1, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'],
            name="RSI",
            line=dict(color='magenta', width=2)
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, row=2, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, row=2, col=1)
    
    # حجم التداول
    colors = ['red' if close < open else 'green' 
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        name="Volume",
        marker_color=colors,
        opacity=0.6
    ), row=3, col=1)
    
    # تحديث التنسيق
    fig.update_layout(
        height=700,
        template="plotly_dark",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="Volume", row=3, col=1)
    
    return fig

@st.cache_data(ttl=300)
def get_stock_data(ticker: str, period: str = "6mo"):
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None, None
        
        # إضافة المؤشرات الفنية
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['RSI'] = calculate_rsi(df['Close'], 14)
        
        return df, stock.info
    except Exception as e:
        return None, None

# ====================== واجهة المستخدم الرئيسية ======================

def main():
    st.title("🏢 بوت تحليل الأسهم المتكامل - التحليل الآلي")
    st.markdown(f"**الإصدار {APP_VERSION}** | دعم: مصر 🇪🇬 • السعودية 🇸🇦 • أمريكا 🇺🇸")
    st.markdown("---")
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("## 📊 لوحة التحكم")
        
        # إجمالي الأسهم
        st.metric("📈 إجمالي الأسهم", len(STOCKS))
        
        # حالة الذكاء الاصطناعي
        model = init_gemini()
        if model:
            st.success("🤖 Gemini: متصل ✅")
        else:
            st.warning("⚠️ Gemini: غير متصل - أضف المفتاح")
        
        st.divider()
        
        # إعدادات إضافية
        st.markdown("### ⚙️ الإعدادات")
        period = st.selectbox(
            "📅 الفترة الزمنية",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            index=2
        )
        
        st.caption("📊 البيانات من Yahoo Finance")
        st.caption("🧠 التحليل بالذكاء الاصطناعي")
    
    # التبويبات الرئيسية
    tab1, tab2 = st.tabs(["📈 تحليل الأسهم", "ℹ️ عن التطبيق"])
    
    with tab1:
        st.header("🔍 تحليل سهم فردي")
        
        # البحث عن سهم
        search_term = st.text_input(
            "🔎 ابحث عن سهم بالاسم أو الرمز",
            placeholder="مثال: CIB أو البنك التجاري أو AAPL",
            help="اكتب اسم الشركة أو رمز السهم"
        )
        
        if search_term:
            # البحث في الأسهم
            found_stocks = {}
            for name, ticker in STOCKS.items():
                if (search_term.lower() in name.lower() or 
                    search_term.lower() in ticker.lower()):
                    found_stocks[name] = ticker
            
            if found_stocks:
                st.success(f"✅ تم العثور على {len(found_stocks)} نتيجة")
                
                # اختيار السهم
                selected_name = st.selectbox(
                    "اختر السهم للتحليل",
                    options=list(found_stocks.keys()),
                    format_func=lambda x: f"{x} ({found_stocks[x]})"
                )
                selected_ticker = found_stocks[selected_name]
                
                # جلب البيانات والتحليل
                with st.spinner("📡 جاري تحميل بيانات السهم..."):
                    df, info = get_stock_data(selected_ticker, period)
                
                if df is not None and not df.empty:
                    # حساب المؤشرات الفنية
                    indicators = calculate_technical_indicators(df)
                    signal = generate_technical_signal(indicators)
                    
                    # عرض معلومات الشركة
                    company_name = info.get('longName', selected_name)
                    sector = info.get('sector', 'غير محدد')
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"🏢 **الشركة:** {company_name[:40]}")
                    with col2:
                        st.info(f"📂 **القطاع:** {sector}")
                    with col3:
                        st.info(f"🆔 **الرمز:** {selected_ticker}")
                    
                    st.divider()
                    
                    # عرض المؤشرات الأساسية
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    with metrics_col1:
                        st.metric("💰 السعر", f"{indicators['current_price']:.2f}")
                    with metrics_col2:
                        st.metric("📊 RSI", f"{indicators['rsi']:.1f}")
                    with metrics_col3:
                        st.metric("📈 الاتجاه", indicators['trend'])
                    with metrics_col4:
                        st.metric("🎯 التوصية", signal['action'])
                    
                    # الرسم البياني المتقدم
                    fig = create_advanced_chart(df, selected_ticker)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # عرض التحليل الفني
                    render_analysis_section(indicators, signal)
                    
                    # تحليل الذكاء الاصطناعي
                    st.markdown("### 🤖 تحليل الذكاء الاصطناعي")
                    
                    col_ai1, col_ai2 = st.columns([1, 3])
                    with col_ai1:
                        if st.button("🧠 تحليل بـ Gemini", type="primary", use_container_width=True):
                            with st.spinner("جاري التحليل الذكي..."):
                                ai_result = generate_ai_analysis(selected_ticker, indicators, signal, model)
                                st.session_state['ai_analysis'] = ai_result
                    
                    if 'ai_analysis' in st.session_state:
                        st.success(st.session_state['ai_analysis'])
                    
                    # معلومات إضافية
                    with st.expander("ℹ️ معلومات إضافية"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**أعلى 52 أسبوع:** {indicators.get('high_52w', 0):.2f}")
                            st.write(f"**أدنى 52 أسبوع:** {indicators.get('low_52w', 0):.2f}")
                            st.write(f"**متوسط 20 يوم:** {indicators.get('sma_20', 0):.2f}")
                        with col2:
                            st.write(f"**متوسط 50 يوم:** {indicators.get('sma_50', 0):.2f}")
                            st.write(f"**متوسط الحجم:** {indicators.get('avg_volume', 0):,.0f}")
                            st.write(f"**Bollinger وسط:** {indicators.get('bb_middle', 0):.2f}")
                    
                    # زر تحديث البيانات
                    if st.button("🔄 تحديث البيانات", use_container_width=True):
                        st.cache_data.clear()
                        st.rerun()
                        
                else:
                    st.error("❌ لا توجد بيانات للسهم. تأكد من صحة الرمز")
            else:
                st.warning("⚠️ لم يتم العثور على نتائج. جرب كلمة بحث أخرى")
        else:
            # عرض أسهم مقترحة
            st.info("💡 **أمثلة للبحث:** اكتب 'CIB' للبنك التجاري، أو 'أرامكو'، أو 'AAPL' لشركة أبل")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🇪🇬 أسهم مصرية مقترحة:**")
                for name in list(STOCKS.keys())[:3]:
                    if '.CA' in STOCKS.get(name, ''):
                        st.write(f"• {name}")
            
            with col2:
                st.markdown("**🇸🇦 أسهم سعودية مقترحة:**")
                for name in list(STOCKS.keys())[:3]:
                    if '.SR' in STOCKS.get(name, ''):
                        st.write(f"• {name}")
            
            with col3:
                st.markdown("**🇺🇸 أسهم أمريكية مقترحة:**")
                for name in list(STOCKS.keys())[:3]:
                    ticker = STOCKS.get(name, '')
                    if ticker in ['AAPL', 'MSFT', 'GOOGL']:
                        st.write(f"• {name}")
    
    with tab2:
        st.header("ℹ️ معلومات عن التطبيق")
        st.markdown(f"""
        ### 🏆 Stock AI Analyst Pro - التحليل الآلي
        
        **الإصدار:** {APP_VERSION}
        
        **الميزات الرئيسية:**
        - ✅ تحليل فني آلي بالكامل
        - ✅ مؤشر RSI مع تنبيهات ذكية
        - ✅ مستويات دعم ومقاومة تلقائية
        - ✅ إشارات شراء/بيع/انتظار
        - ✅ تحليل بالذكاء الاصطناعي Gemini
        - ✅ رسوم بيانية متقدمة
        - ✅ دعم الأسواق المصرية والسعودية والأمريكية
        
        **المؤشرات الفنية المستخدمة:**
        - RSI (Relative Strength Index)
        - SMA (Simple Moving Average)
        - MACD (Moving Average Convergence Divergence)
        - Bollinger Bands
        - تحليل حجم التداول
        
        **المصادر:**
        - 📊 البيانات: Yahoo Finance API
        - 🧠 الذكاء الاصطناعي: Google Gemini
        
        **التنصل:**
        ⚠️ هذا التطبيق للأغراض التعليمية فقط. لا يقدم نصائح استثمارية.
        قرارات الاستثمار مسؤوليتك الشخصية.
        
        ---
        **آخر تحديث:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """)

if __name__ == "__main__":
    main()
