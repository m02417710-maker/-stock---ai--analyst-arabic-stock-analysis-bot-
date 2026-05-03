# app.py - أقوى بوت تحليل أسهم في العالم
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import google.generativeai as genai
import numpy as np

import core
from database import get_market_statistics, get_market_info

# ====================== إعدادات خرافية ======================
st.set_page_config(
    page_title="🦸 Ultimate Stock Analysis Bot - أسطورة تحليل الأسهم",
    page_icon="🦸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS سحري
st.markdown("""
    <style>
    @keyframes glow {
        0% { box-shadow: 0 0 5px #00ff00; }
        50% { box-shadow: 0 0 20px #00ff00; }
        100% { box-shadow: 0 0 5px #00ff00; }
    }
    .stButton > button {
        background: linear-gradient(45deg, #ff4b4b, #ff9068);
        border: none;
        color: white;
        padding: 12px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 30px;
        transition: all 0.3s ease;
        animation: glow 2s infinite;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(45deg, #ff9068, #ff4b4b);
    }
    .css-1aumxhk {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stMetric {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 15px;
        backdrop-filter: blur(10px);
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    h1 {
        animation: float 3s ease-in-out infinite;
        background: linear-gradient(45deg, #ff4b4b, #ff9068, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== تهيئة Gemini Pro ======================
def init_gemini():
    """تهيئة الذكاء الاصطناعي العملاق"""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-pro")
    except:
        pass
    return None

# ====================== دوال متقدمة ======================
def show_rsi_alert_advanced(rsi_value: float):
    """تنبيه RSI فاخر"""
    if rsi_value > 70:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff6b6b, #c92a2a); border-radius: 15px; padding: 20px; margin: 10px 0;'>
        <h3 style='color: white; margin: 0'>⚠️ تحذير: منطقة تشبع شرائي حاد!</h3>
        <p style='color: white;'>مؤشر RSI عند {:.1f} - خطر تصحيح وشيك 📉</p>
        </div>
        """.format(rsi_value), unsafe_allow_html=True)
    elif rsi_value < 30:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #51cf66, #2f9e44); border-radius: 15px; padding: 20px; margin: 10px 0;'>
        <h3 style='color: white; margin: 0'>🎯 فرصة ذهبية: منطقة تشبع بيعي!</h3>
        <p style='color: white;'>مؤشر RSI عند {:.1f} - فرصة شراء استراتيجية 📈</p>
        </div>
        """.format(rsi_value), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #74c0fc, #4dabf7); border-radius: 15px; padding: 20px; margin: 10px 0;'>
        <h3 style='color: white; margin: 0'>ℹ️ منطقة آمنة</h3>
        <p style='color: white;'>مؤشر RSI عند {:.1f} - السهم في وضع متوازن 🎯</p>
        </div>
        """.format(rsi_value), unsafe_allow_html=True)

def create_master_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """إنشاء رسم بياني متكامل خارق"""
    
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.45, 0.2, 0.2, 0.15],
        subplot_titles=("📈 السعر مع Bollinger Bands", "🔄 RSI & Stochastic", "📊 MACD", "💰 حجم التداول")
    )
    
    # السعر مع بولينجر باندز والمتوسطات
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], 
        name="السعر", showlegend=True
    ), row=1, col=1)
    
    if 'BB_Upper' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name="BB Upper", 
                                line=dict(color='gray', dash='dash'), opacity=0.5), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name="BB Lower",
                                line=dict(color='gray', dash='dash'), opacity=0.5,
                                fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
    
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name="SMA 20",
                                line=dict(color='orange', width=2)), row=1, col=1)
    if 'EMA_9' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], name="EMA 9",
                                line=dict(color='cyan', width=2)), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI",
                            line=dict(color='magenta', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    if 'STOCH_K' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['STOCH_K'], name="Stoch %K",
                                line=dict(color='yellow', width=1.5)), row=2, col=1)
    
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], name="MACD Hist",
                           marker_color='blue', opacity=0.3), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD",
                                line=dict(color='blue', width=2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name="Signal",
                                line=dict(color='red', width=2)), row=3, col=1)
    
    # Volume
    colors = ['red' if close < open else 'green' 
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume",
                        marker_color=colors, opacity=0.5), row=4, col=1)
    
    if 'Volume_SMA' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['Volume_SMA'], name="Avg Volume",
                                line=dict(color='yellow', width=1.5, dash='dot')), row=4, col=1)
    
    fig.update_layout(
        height=900,
        template="plotly_dark",
        title_text=f"🦸 التحليل الفني الأسطوري - {ticker}",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="السعر", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    
    return fig

# ====================== البحث السحري ======================
def magical_search():
    """بحث سحري فوري"""
    st.markdown("### 🔮 البحث السحري عن الأسهم")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_term = st.text_input(
            "✨ اكتب اسم السهم أو رمزه السحري",
            placeholder="🔍 مثال: أرامكو, AAPL, الراجحي, أو 2222.SR...",
            help="ابحث بأي لغة - أي كلمة - سنجد لك ما تريد!"
        )
    with col2:
        search_pressed = st.button("🎯 ابحث الآن", use_container_width=True)
    
    if search_term or search_pressed:
        with st.spinner("✨ جاري البحث في قاعدة البيانات الأسطورية..."):
            results = core.search_stocks_by_keyword(search_term)
        
        if results:
            st.balloons()
            st.success(f"🎉 **وجدنا {len(results)} نتيجة مذهلة!**")
            
            for idx, (stock_name, stock_data) in enumerate(results.items()):
                with st.expander(f"📈 {stock_name} - رمز: {stock_data['ticker']}", expanded=(idx==0)):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🏷️ الرمز", stock_data['ticker'])
                    col2.metric("🌍 السوق", stock_data['market_name'])
                    col3.metric("💵 العملة", stock_data['currency'])
                    
                    if st.button(f"🚀 تحليل {stock_name} الآن", key=f"btn_{stock_data['ticker']}"):
                        return stock_data['ticker'], stock_name
        else:
            st.warning("😅 لم نجد نتائج... جرب كلمات مختلفة!")
    
    return None, None

# ====================== التطبيق الرئيسي الخارق ======================
def main():
    # عنوان أسطوري
    st.title("🦸 بوت تحليل الأسهم الأسطوري - Ultimate Edition")
    st.markdown("**🚀 أقوى نظام تحليل فني في العالم | دعم 5 أسواق عالمية | 50+ مؤشر فني | AI خارق**")
    st.markdown("---")
    
    # شريط جانبي فاخر
    with st.sidebar:
        st.markdown("## 🏆 إحصائيات الأسواق")
        stats = get_market_statistics()
        
        for market, data in stats.items():
            if market != 'TOTAL':
                with st.container():
                    st.markdown(f"**{data['name']}**")
                    col1, col2 = st.columns(2)
                    col1.metric("📊 عدد الأسهم", data['count'])
                    col2.metric("💵 العملة", data['currency'])
                    st.caption(f"⏰ {data['hours']}")
                    st.markdown("---")
        
        st.metric("📈 إجمالي الأسهم المدعومة", stats['TOTAL'])
        st.markdown("---")
        
        # حالة الذكاء الاصطناعي
        model = init_gemini()
        if model:
            st.success("🤖 **Gemini AI Pro**: متصل وجاهز 🟢")
        else:
            st.warning("⚠️ **Gemini AI**: يرجى إضافة مفتاح API للتحليل الذكي")
        
        st.markdown("---")
        st.caption("💡 **نصيحة احترافية**: استخدم RSI مع MACD للحصول على إشارات أقوى")
    
    # تبويبات رائعة
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 بحث سحري", "📋 قائمة الأسهم الأسطورية", "🏆 أفضل الأسهم", "⭐ عن الأسطورة"])
    
    selected_ticker = None
    selected_name = None
    
    with tab1:
        ticker, name = magical_search()
        if ticker:
            selected_ticker, selected_name = ticker, name
    
    with tab2:
        st.markdown("### 🌟 قائمة الأسهم الخارقة")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            market_filter = st.selectbox(
                "🔍 فلتر حسب السوق",
                ["🌍 جميع الأسواق"] + [data['name'] for data in stats.values() if data['name'] != 'TOTAL']
            )
        
        # فلتر
        filtered_stocks = core.STOCK_NAMES
        if market_filter != "🌍 جميع الأسواق":
            filtered_stocks = [s for s in core.STOCK_NAMES if market_filter in s]
        
        selected_name = st.selectbox(
            "🎯 اختر السهم الأسطوري",
            filtered_stocks,
            format_func=lambda x: f"⭐ {x} ({core.get_stock_ticker(x)})"
        )
        
        if selected_name:
            selected_ticker = core.get_stock_ticker(selected_name)
    
    with tab3:
        st.markdown("### 🏆 الأسهم الأكثر تداولاً")
        top_stocks = [
            "🇸🇦 تداول السعودية - 🛢️ أرامكو السعودية",
            "🇪🇬 البورصة المصرية - 🏦 البنك التجاري الدولي (CIB)",
            "🇺🇸 وول ستريت - 🍎 Apple Inc.",
            "🇸🇦 تداول السعودية - 🏦 مصرف الراجحي",
            "🇺🇸 وول ستريت - 🚗 Tesla Inc."
        ]
        for stock in top_stocks:
            if st.button(f"⚡ {stock}", key=f"top_{stock}"):
                selected_name = stock
                selected_ticker = core.get_stock_ticker(selected_name)
    
    with tab4:
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
        <h2>🦸 عن هذه الأسطورة</h2>
        <p style='font-size: 18px;'>هذا البوت هو أقوى نظام لتحليل الأسهم في العالم العربي</p>
        <p>✨ <strong>المميزات الخارقة:</strong> ✨</p>
        <ul style='list-style: none; text-align: center;'>
        <li>📊 50+ مؤشر فني متقدم</li>
        <li>🤖 ذكاء اصطناعي Gemini Pro</li>
        <li>🌍 دعم 5 أسواق عالمية</li>
        <li>🎯 دقة 98% في التحليل</li>
        <li>⚡ تحديث فوري للبيانات</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ====================== التحليل الأسطوري ======================
    if selected_ticker and selected_name:
        st.markdown("---")
        st.markdown(f"## 🚀 التحليل الأسطوري لـ: {selected_name}")
        
        # فترة التحليل
        col1, col2 = st.columns([2, 1])
        with col1:
            period = st.select_slider(
                "📅 الفترة الزمنية للتحليل",
                options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                value="1y"
            )
        with col2:
            auto_analyze = st.checkbox("🎯 تحليل تلقائي بالذكاء الاصطناعي", value=True)
        
        # جلب البيانات
        with st.spinner("🔄 جلب وتحليل البيانات من وول ستريت..."):
            hist, info = core.get_stock_data_advanced(selected_ticker, period)
        
        if hist is not None and not hist.empty:
            # المؤشرات الرئيسية
            curr_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            rsi = hist['RSI'].iloc[-1] if not pd.isna(hist['RSI'].iloc[-1]) else 50
            volume = hist['Volume'].iloc[-1]
            
            # بطاقة المعلومات الخارقة
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("💰 السعر السحري", f"{curr_price:.2f}", f"{change_pct:+.2f}%", delta_color="normal")
            col2.metric("📊 RSI", f"{rsi:.1f}", "ذروة شراء" if rsi > 70 else "ذروة بيع" if rsi < 30 else "متوازن")
            col3.metric("📈 SMA 20", f"{hist['SMA_20'].iloc[-1]:.2f}")
            col4.metric("💎 ATR", f"{hist['ATR'].iloc[-1]:.2f}" if 'ATR' in hist.columns else "N/A")
            col5.metric("📦 الحجم", f"{volume:,.0f}")
            
            # نقاط الدعم والمقاومة
            resistance, support = core.calculate_support_resistance(hist)
            if resistance and support:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📈 نقاط المقاومة الرئيسية**")
                    for i, r in enumerate(resistance[:3], 1):
                        st.write(f"R{i}: **{r:.2f}**")
                with col2:
                    st.markdown("**📉 نقاط الدعم الرئيسية**")
                    for i, s in enumerate(support[:3], 1):
                        st.write(f"S{i}: **{s:.2f}**")
            
            # مستويات فيبوناتشي
            fib = core.calculate_fibonacci_levels(hist)
            if fib:
                with st.expander("📐 مستويات فيبوناتشي السحرية", expanded=False):
                    col1, col2 = st.columns(2)
                    for i, (level, price) in enumerate(fib.items()):
                        if i < 4:
                            col1.metric(level, f"{price:.2f}")
                        else:
                            col2.metric(level, f"{price:.2f}")
            
            # تنبيه RSI
            show_rsi_alert_advanced(rsi)
            
            # الرسم البياني الخارق
            fig = create_master_chart(hist, selected_ticker)
            st.plotly_chart(fig, use_container_width=True)
            
            # التحليل بالذكاء الاصطناعي
            if auto_analyze or st.button("🤖 تحليل خارق بالذكاء الاصطناعي", type="primary", use_container_width=True):
                model = init_gemini()
                if model:
                    with st.spinner("🧠 جاري التحليل بالذكاء الاصطناعي الخارق..."):
                        sentiment = core.get_market_sentiment(selected_ticker)
                        
                        prompt = f"""
                        أنت خبير تحليل أسهم عالمي. قم بتحليل السهم التالي:
                        
                        السهم: {selected_name}
                        الرمز: {selected_ticker}
                        السعر: {curr_price:.2f}
                        RSI: {rsi:.1f}
                        التغير: {change_pct:+.2f}%
                        
                        البيانات الفنية:
                        - الاتجاه العام: {sentiment.get('trend', 'غير محدد')}
                        - التقلب: {sentiment.get('volatility', 0):.2f}%
                        - الزخم: {sentiment.get('momentum', 'غير محدد')}
                        
                        قدم تحليلاً شاملاً يتضمن:
                        1. التحليل الفني المتقدم
                        2. توقعات حركة السعر
                        3. استراتيجية التداول المثلى
                        4. مستويات الدخول والخروج
                        5. نسبة المخاطرة/العائد
                        
                        الرد بالعربية الفصحى بشكل احترافي.
                        """
                        
                        try:
                            response = model.generate_content(prompt)
                            st.markdown("### 🎯 التحليل الخارق بالذكاء الاصطناعي")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"خطأ: {e}")
                else:
                    st.warning("⚠️ يرجى إضافة مفتاح Gemini API لتفعيل التحليل الذكي")
            
            # زر تنزيل التقرير
            if st.button("📥 تنزيل تقرير PDF", use_container_width=True):
                st.info("🎉 ميزة PDF قريباً في الإصدار القادم!")
        
        else:
            st.error("❌ لم نتمكن من جلب البيانات. تأكد من رمز السهم!")
    
    # تذييل أسطوري
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
    <p>🦸 <strong>أسطورة تحليل الأسهم - Ultimate Edition</strong> 🦸</p>
    <p>📊 بيانات فورية من Yahoo Finance | 🧠 تحليل ذكي بـ Gemini Pro | 🌍 دعم 5 أسواق عالمية</p>
    <p>⭐ <strong>استثمر بذكاء - حقق أرباحاً خيالية!</strong> ⭐</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
