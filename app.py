# ============================================================
# ملف: stock_analyzer_final.py
# الإصدار النهائي المتكامل: نظام متعدد الخيوط + رادار + تنبيهات
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import warnings
import threading
import queue
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings('ignore')

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="المحلل المصري Pro - النظام المتكامل",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# متغيرات عامة وإعدادات
# ============================================================

# قائمة الأسهم الموسعة
STOCKS_LIST = {
    "البنك التجاري الدولي (مصر)": "COMI.CA",
    "طلعت مصطفى (مصر)": "TMGH.CA",
    "فوري (مصر)": "FWRY.CA",
    "أرامكو (السعودية)": "2222.SR",
    "الراجحي (السعودية)": "1120.SR",
    "آبل (أمريكا)": "AAPL",
    "تسلا (أمريكا)": "TSLA",
    "مايكروسوفت (أمريكا)": "MSFT",
    "إنفيديا (أمريكا)": "NVDA",
    "أمازون (أمريكا)": "AMZN",
    "جوجل (أمريكا)": "GOOGL",
    "ميتا (أمريكا)": "META"
}

# إعدادات التنبيهات (ضع التوكن الحقيقي هنا)
TELEGRAM_BOT_TOKEN = ""  # أدخل توكن البوت هنا
TELEGRAM_CHAT_ID = ""     # أدخل معرف المحادثة هنا

# قائمة التنبيهات
alerts_queue = queue.Queue()

# ============================================================
# دوال التنبيه والإشعارات
# ============================================================

def send_telegram_alert(message):
    """إرسال تنبيه عبر تيليجرام"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"خطأ في إرسال التنبيه: {e}")
            return False
    return False

def add_alert(ticker, alert_type, price, message):
    """إضافة تنبيه إلى قائمة الانتظار"""
    alert = {
        "ticker": ticker,
        "type": alert_type,
        "price": price,
        "message": message,
        "timestamp": datetime.now()
    }
    alerts_queue.put(alert)
    
    # إرسال التنبيه فوراً
    send_telegram_alert(f"🔔 <b>تنبيه جديد</b>\n{message}\nالسهم: {ticker}\nالسعر: {price}\nالوقت: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# دوال التحليل المتقدمة
# ============================================================

def is_bottom_breakout(df):
    """يكتشف إذا كان السهم يبدأ الصعود من القاع"""
    if len(df) < 50:
        return False
    
    try:
        # شرط 1: السعر كان تحت المتوسط المتحرك 50 لفترة طويلة
        was_down = df['Close'].iloc[-10] < df['MA50'].iloc[-10]
        # شرط 2: السعر الآن اخترق المتوسط 20 للأعلى
        breaking_up = df['Close'].iloc[-1] > df['MA20'].iloc[-1]
        # شرط 3: RSI بدأ يخرج من منطقة ذروة البيع (أكبر من 30)
        rsi_rising = 30 < df['RSI'].iloc[-1] < 50
        
        return was_down and breaking_up and rsi_rising
    except:
        return False

def detect_bottom_growth(df):
    """اكتشاف نمو السهم من القاع (إشارة الانفراج)"""
    if len(df) < 50:
        return False
    
    try:
        # شرط 1: السعر في قاع أو قريب منه
        lowest_50 = df['Low'].rolling(window=50).min().iloc[-1]
        is_at_low = df['Close'].iloc[-1] <= lowest_50 * 1.05
        
        # شرط 2: مؤشر RSI بدأ يصعد
        rsi_rising = df['RSI'].iloc[-1] > df['RSI'].iloc[-3]
        
        # شرط 3: اختراق المتوسط 10
        ma10 = df['Close'].rolling(window=10).mean()
        confirmed = df['Close'].iloc[-1] > ma10.iloc[-1]
        
        return is_at_low and rsi_rising and confirmed
    except:
        return False

def get_exit_signals(df):
    """تحديد إشارات البيع ووقف الخسارة"""
    if len(df) < 2:
        return False, 0
    
    last_price = df['Close'].iloc[-1]
    stop_loss = df['Low'].iloc[-2] * 0.97 if len(df) > 1 else last_price * 0.97
    exit_signal = last_price < stop_loss or last_price < df['MA20'].iloc[-1]
    
    return exit_signal, stop_loss

def get_trading_orders(df):
    """توليد أوامر بيع وشراء محددة"""
    if len(df) < 20:
        return "قيد التحليل", 0, 0
    
    current_price = df['Close'].iloc[-1]
    stop_loss = df['Low'].tail(2).min() * 0.98
    target = df['High'].rolling(window=20).max().iloc[-1]
    
    if current_price < stop_loss:
        return "❌ أمر بيع فوري (كسر وقف الخسارة)", stop_loss, target
    elif current_price >= target:
        return "💰 أمر بيع (تحقيق هدف)", stop_loss, target
    else:
        return "⏳ احتفاظ", stop_loss, target

def calculate_smart_score(df):
    """حساب درجة ذكية مع أوزان مختلفة لكل مؤشر"""
    if df.empty or len(df) < 20:
        return 0, [], {}
    
    score = 0
    reasons = []
    details = {}
    last = df.iloc[-1]
    
    # 1. الاتجاه العام
    if last['Close'] > last['MA20']:
        score += 1.0
        reasons.append("✅ السعر فوق المتوسط 20")
        details['trend'] = 'up'
    else:
        reasons.append("⚠️ السعر تحت المتوسط 20")
        details['trend'] = 'down'
        score -= 0.5
    
    # 2. RSI
    rsi = last['RSI']
    details['rsi'] = round(rsi, 1)
    
    if rsi <= 30:
        score += 1.5
        reasons.append(f"🔥 فرصة شراء - RSI {rsi:.1f}")
    elif 30 < rsi <= 40:
        score += 1.0
        reasons.append(f"✅ منطقة شراء - RSI {rsi:.1f}")
    elif 40 < rsi < 55:
        score += 0.5
        reasons.append(f"✅ منطقة تجميع - RSI {rsi:.1f}")
    elif rsi >= 70:
        score -= 1.0
        reasons.append(f"⚠️ ذروة شراء - RSI {rsi:.1f}")
    
    # 3. MACD
    if 'MACD_12_26_9' in last and 'MACDs_12_26_9' in last:
        if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
            score += 1.0
            reasons.append("🚀 MACD إيجابي")
            details['macd'] = 'bullish'
        else:
            score -= 0.5
            reasons.append("📉 MACD سلبي")
            details['macd'] = 'bearish'
    
    # 4. حجم التداول
    vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
    if last['Volume'] > vol_ma:
        score += 0.5
        reasons.append("💰 سيولة عالية")
    
    return round(score, 1), reasons, details

# ============================================================
# دوال جلب البيانات (متعددة الخيوط)
# ============================================================

def fetch_single_stock(ticker, name):
    """جلب بيانات سهم واحد (للاستخدام مع الـ Threading)"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo", interval="1d")
        
        if df.empty or len(df) < 20:
            return None
        
        # حساب المؤشرات الأساسية
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        
        # MACD
        macd = ta.macd(df['Close'])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        
        # حجم التداول المتوسط
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        return {
            'name': name,
            'ticker': ticker,
            'df': df,
            'current_price': df['Close'].iloc[-1],
            'volume': df['Volume'].iloc[-1],
            'rsi': df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
        }
    except Exception as e:
        return None

def fetch_all_stocks_multithreaded(stock_list, max_workers=5):
    """جلب بيانات جميع الأسهم باستخدام تعدد الخيوط"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for name, ticker in stock_list.items():
            future = executor.submit(fetch_single_stock, ticker, name)
            futures[future] = name
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return results

@st.cache_data(ttl=900, show_spinner=False)
def get_full_data(ticker):
    """جلب البيانات الكاملة لسهم واحد"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        
        if df.empty or len(df) < 20:
            return None, None
        
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA50'] = ta.sma(df['Close'], length=50)
        df['MA200'] = ta.sma(df['Close'], length=200)
        
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df = pd.concat([df, bb], axis=1)
        
        macd = ta.macd(df['Close'])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        return df, stock.info
        
    except Exception as e:
        return None, None

# ============================================================
# دوال الرسم البياني المتقدم مع المستهدفات
# ============================================================

def create_chart_with_targets(df, ticker, stop_loss, target):
    """رسم بياني مع خطوط المستهدفات ووقف الخسارة"""
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("📈 السعر مع المستهدفات", "📊 RSI", "💰 حجم التداول")
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
        go.Scatter(x=df.index, y=df['MA20'], name="MA 20", line=dict(color='#f59e0b')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA50'], name="MA 50", line=dict(color='#10b981')),
        row=1, col=1
    )
    
    # خط الهدف
    if target > 0:
        fig.add_hline(
            y=target, line_dash="dash", line_color="#10b981",
            annotation_text=f"🎯 الهدف: {target:.2f}", annotation_position="top right",
            row=1, col=1
        )
    
    # خط وقف الخسارة
    if stop_loss > 0:
        fig.add_hline(
            y=stop_loss, line_dash="dash", line_color="#ef4444",
            annotation_text=f"🛑 وقف الخسارة: {stop_loss:.2f}", annotation_position="bottom right",
            row=1, col=1
        )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#8b5cf6')),
        row=2, col=1
    )
    fig.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.2, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#10b981", opacity=0.2, row=2, col=1)
    
    # حجم التداول
    volume_colors = ['#ef4444' if df['Close'].iloc[i] < df['Open'].iloc[i] else '#10b981' 
                     for i in range(len(df))]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name="الحجم", marker_color=volume_colors),
        row=3, col=1
    )
    
    fig.update_layout(
        title=f"📊 التحليل الفني لسهم {ticker}",
        template="plotly_dark",
        height=700,
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=True
    )
    
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="الحجم", row=3, col=1)
    
    return fig

# ============================================================
# دالة الماسح الضوئي للسوق (Stock Scanner)
# ============================================================

def market_scanner(stock_list):
    """الماسح الضوئي للسوق - يكتشف فرص الشراء والبيع"""
    opportunities = []
    stocks_data = fetch_all_stocks_multithreaded(stock_list)
    
    for stock in stocks_data:
        if stock is None:
            continue
        
        df = stock['df']
        score, _, details = calculate_smart_score(df)
        bottom_breakout = is_bottom_breakout(df)
        bottom_growth = detect_bottom_growth(df)
        exit_signal, stop_loss = get_exit_signals(df)
        
        # تحديد فرص الشراء القوية
        if score >= 3.5 or bottom_breakout or bottom_growth:
            opportunities.append({
                "السهم": stock['name'],
                "الرمز": stock['ticker'],
                "السعر": round(stock['current_price'], 2),
                "RSI": round(stock['rsi'], 1),
                "درجة الثقة": score,
                "نوع الإشارة": "🟢 شراء قوي" if bottom_breakout else ("🟢 انفراج قاع" if bottom_growth else ("🟢 شراء" if score >= 3.5 else "🟡 مراقبة")),
                "الهدف المقترح": round(stock['current_price'] * 1.1, 2)
            })
        
        # اكتشاف إشارات البيع
        if exit_signal:
            add_alert(stock['ticker'], "SELL", stock['current_price'], 
                     f"⚠️ إشارة بيع للسهم {stock['name']} عند سعر {stock['current_price']:.2f}")
            
            opportunities.append({
                "السهم": stock['name'],
                "الرمز": stock['ticker'],
                "السعر": round(stock['current_price'], 2),
                "RSI": round(stock['rsi'], 1),
                "درجة الثقة": score,
                "نوع الإشارة": "🔴 بيع/خروج",
                "الهدف المقترح": round(stop_loss, 2) if stop_loss else 0
            })
    
    return pd.DataFrame(opportunities)

# ============================================================
# الواجهة الرئيسية
# ============================================================

def main():
    """الدالة الرئيسية"""
    
    # التحديث التلقائي
    st_autorefresh(interval=900000, key="auto_refresh")
    
    # تصميم الشريط الجانبي
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 24px; color: #2563eb;">📊 المحلل المصري Pro</h1>
            <p style="color: #94a3b8;">النظام المتكامل - إصدار المؤسسات</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # اختيار السهم
        selected_stock = st.selectbox("🔍 اختيار سهم", list(STOCKS_LIST.keys()))
        ticker = STOCKS_LIST[selected_stock]
        
        st.markdown("---")
        
        # أزرار التحكم
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 تحديث", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("📊 مسح السوق", use_container_width=True):
                st.session_state['run_scanner'] = True
        
        st.markdown("---")
        
        # إعدادات التنبيهات
        with st.expander("⚙️ إعدادات التنبيهات", expanded=False):
            st.info("""
            لتفعيل تنبيهات التيليجرام:
            1. أنشئ بوت عبر @BotFather
            2. احصل على التوكن
            3. احصل على Chat ID
            4. أضفهم في الكود
            """)
    
    # العنوان الرئيسي
    st.markdown(f'<h2 style="text-align: center;">📈 التحليل المتكامل لسهم {ticker}</h2>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # جلب البيانات
    with st.spinner("🔄 جاري تحليل البيانات..."):
        df, info = get_full_data(ticker)
    
    if df is not None and not df.empty:
        # حساب المؤشرات
        score, reasons, details = calculate_smart_score(df)
        exit_signal, stop_loss = get_exit_signals(df)
        order_text, order_stop, order_target = get_trading_orders(df)
        bottom_breakout = is_bottom_breakout(df)
        bottom_growth = detect_bottom_growth(df)
        
        # بطاقات المعلومات السريعة
        col1, col2, col3, col4, col5 = st.columns(5)
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        with col1:
            st.metric("💰 السعر", f"{current_price:.2f}", f"{price_change:+.2f}%")
        with col2:
            st.metric("📊 RSI", f"{details.get('rsi', 50):.1f}")
        with col3:
            st.metric("🎯 درجة الثقة", f"{score}/5")
        with col4:
            detection = "🟢 قاع" if bottom_breakout else ("🟢 انفراج" if bottom_growth else "🟡 عادي")
            st.metric("🔍 الاكتشاف", detection)
        with col5:
            st.metric("📋 الأمر", order_text.split()[0])
        
        st.markdown("---")
        
        # إشارات خاصة
        if bottom_breakout:
            st.success("🎉 **اكتشاف: السهم يبدأ الصعود من القاع!** فرصة شراء مبكرة")
        elif bottom_growth:
            st.info("📈 **اكتشاف: نمو من القاع - إشارة انفراج إيجابية**")
        
        # رسالة وقف الخسارة
        if exit_signal:
            st.error(f"⚠️ **تنبيه: إشارة بيع/خروج!** وقف الخسارة عند {stop_loss:.2f}")
            add_alert(ticker, "EXIT", current_price, f"إشارة خروج للسهم {ticker} عند {current_price:.2f}")
        
        # التبويبات
        tab1, tab2, tab3, tab4 = st.tabs(["📈 الرسم البياني", "📋 التحليل", "🎯 الأوامر", "🏢 معلومات"])
        
        with tab1:
            fig = create_chart_with_targets(df, ticker, order_stop, order_target)
            st.plotly_chart(fig, use_container_width=True, key="main_chart")
        
        with tab2:
            st.subheader("📋 تفاصيل التحليل الفني")
            for reason in reasons:
                st.markdown(reason)
            
            st.markdown("---")
            st.subheader("🔍 اكتشافات إضافية")
            st.markdown(f"- **كسر القاع:** {'✅ نعم' if bottom_breakout else '❌ لا'}")
            st.markdown(f"- **انفراج القاع:** {'✅ نعم' if bottom_growth else '❌ لا'}")
            st.markdown(f"- **إشارة خروج:** {'⚠️ نعم' if exit_signal else '✅ لا'}")
        
        with tab3:
            st.subheader("🎯 أوامر التداول المقترحة")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📊 الأمر الحالي:** {order_text}")
                st.markdown(f"**🛑 وقف الخسارة:** {order_stop:.2f}")
            with col2:
                st.markdown(f"**🎯 الهدف الأول:** {order_target:.2f}")
                st.markdown(f"**📈 نسبة المخاطرة:** {((order_target - current_price) / (current_price - order_stop)):.2f}" if order_stop < current_price else "غير متاح")
        
        with tab4:
            if info:
                st.markdown(f"**🏢 الاسم:** {info.get('longName', 'غير متوفر')}")
                st.markdown(f"**🏭 القطاع:** {info.get('sector', 'غير متوفر')}")
                st.markdown(f"**💰 القيمة السوقية:** ${info.get('marketCap', 0):,}")
                if info.get('longBusinessSummary'):
                    st.markdown("**📝 نبذة:**")
                    st.markdown(info.get('longBusinessSummary')[:500] + "...")
        
    else:
        st.error("❌ فشل في جلب البيانات")
    
    st.markdown("---")
    
    # ===== ماسح السوق (Stock Scanner) =====
    st.subheader("🔍 ماسح السوق الذكي - فرص الاستثمار")
    
    if st.button("🔄 تشغيل الماسح الضوئي للسوق", use_container_width=True):
        with st.spinner("🔄 جاري مسح جميع الأسهم (باستخدام تقنية تعدد الخيوط)..."):
            opportunities_df = market_scanner(STOCKS_LIST)
            
            if not opportunities_df.empty:
                st.success(f"✅ تم العثور على {len(opportunities_df)} فرصة")
                st.dataframe(opportunities_df, use_container_width=True, hide_index=True)
                
                # عرض التنبيهات
                if not alerts_queue.empty():
                    st.subheader("🔔 التنبيهات المرسلة")
                    while not alerts_queue.empty():
                        alert = alerts_queue.get()
                        st.info(f"📢 {alert['message']} - {alert['timestamp'].strftime('%H:%M:%S')}")
            else:
                st.warning("⚠️ لم يتم العثور على فرص استثمارية حالياً")
    
    # عرض قائمة التنبيهات الحالية
    if not alerts_queue.empty():
        with st.expander("🔔 سجل التنبيهات", expanded=False):
            while not alerts_queue.empty():
                alert = alerts_queue.get()
                st.warning(f"{alert['timestamp'].strftime('%H:%M:%S')} - {alert['message']}")
    
    # تذييل
    st.markdown("---")
    st.caption("""
    ⚠️ **تنويه مهم:** هذا التحليل لأغراض تعليمية فقط. 
    نظام متعدد الخيوط | تنبيهات فورية | ماسح سوق ذكي | إصدار المؤسسات
    """)

# ============================================================
# تشغيل التطبيق
# ============================================================

if __name__ == "__main__":
    main()
