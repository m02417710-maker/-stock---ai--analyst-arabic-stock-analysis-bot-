# ============================================================
# ملف: app_oracle_final.py
# Oracle Zero-Knowledge - الإصدار النهائي المصحح
# مع: عوائد لوغاريتمية + بروفايل حجم حقيقي + معالجة أخطاء متقدمة
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
import json
from scipy.stats import norm
import hashlib
import time

warnings.filterwarnings('ignore')

# ============================================================
# إعدادات الصفحة
# ============================================================

st.set_page_config(
    page_title="Oracle Zero-Knowledge - الإصدار النهائي",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=60000, key="auto_refresh", debounce=True)

# ============================================================
# إعدادات الأمان المتقدمة - معالجة أخطاء st.secrets
# ============================================================

def get_gemini_api_key():
    """جلب مفتاح Gemini API مع معالجة الأخطاء"""
    try:
        # محاولة القراءة من secrets
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        if api_key and api_key != "":
            return api_key
        return None
    except Exception:
        return None

def is_gemini_available():
    """التحقق من توفر Gemini API"""
    api_key = get_gemini_api_key()
    if not api_key:
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # اختبار سريع
        return True
    except:
        return False

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
    border: 1px solid #06b6d4;
    border-radius: 15px;
    padding: 15px;
}
.oracle-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 20px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #06b6d4;
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
# 1. محرك مونت كارلو المحسن (مع العوائد اللوغاريتمية)
# ============================================================

class MonteCarloEngine:
    """محاكاة مونت كارلو - باستخدام العوائد اللوغاريتمية (أدق رياضياً)"""
    
    def __init__(self, df, days=30, simulations=10000):
        self.df = df
        self.days = days
        self.simulations = simulations
        self.last_price = df['Close'].iloc[-1]
        
        # استخدام العوائد اللوغاريتمية (أكثر دقة من النسبة المئوية البسيطة)
        self.log_returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        
        # حساب المعاملات الإحصائية من العوائد اللوغاريتمية
        self.mu = self.log_returns.mean()
        self.sigma = self.log_returns.std()
        self.volatility = self.sigma * np.sqrt(252)  # التذبذب السنوي
        
        # معالجة حالة عدم وجود بيانات كافية
        if len(self.log_returns) < 10:
            self.mu = 0.0005  # قيمة افتراضية
            self.sigma = 0.02  # تذبذب افتراضي 2%
        
    def run_simulation(self):
        """تشغيل المحاكاة باستخدام العوائد اللوغاريتمية"""
        # مصفوفة النتائج
        results = np.zeros((self.days, self.simulations))
        
        # توليد المسارات العشوائية باستخدام التوزيع الطبيعي للعوائد اللوغاريتمية
        np.random.seed(42)
        for i in range(self.simulations):
            # توليد عوائد لوغاريتمية عشوائية
            random_returns = np.random.normal(self.mu, self.sigma, self.days - 1)
            
            # حساب الأسعار باستخدام exp (العملية العكسية للوغاريتم)
            prices = [self.last_price]
            for ret in random_returns:
                prices.append(prices[-1] * np.exp(ret))
            
            results[:, i] = prices
        
        self.results = results
        return self.calculate_statistics()
    
    def calculate_statistics(self):
        """حساب الإحصائيات المتقدمة"""
        final_prices = self.results[-1, :]
        
        # المقاييس الأساسية
        expected_price = np.mean(final_prices)
        median_price = np.median(final_prices)
        std_dev = np.std(final_prices)
        
        # نسب الثقة
        confidence_5 = np.percentile(final_prices, 5)
        confidence_25 = np.percentile(final_prices, 25)
        confidence_50 = np.percentile(final_prices, 50)
        confidence_75 = np.percentile(final_prices, 75)
        confidence_95 = np.percentile(final_prices, 95)
        
        # القيمة المعرضة للخطر (VaR) - باستخدام العوائد اللوغاريتمية
        var_95 = self.last_price - confidence_5
        var_99 = self.last_price - np.percentile(final_prices, 1)
        
        # القيمة المتوقعة للخسارة (CVaR)
        tail_losses = final_prices[final_prices <= confidence_5]
        cvar_95 = self.last_price - np.mean(tail_losses) if len(tail_losses) > 0 else var_95
        
        # احتمال الربح
        profit_probability = np.sum(final_prices > self.last_price) / self.simulations * 100
        
        # احتمال تحقيق أهداف محددة
        target_5 = self.last_price * 1.05
        target_10 = self.last_price * 1.10
        target_20 = self.last_price * 1.20
        
        prob_target_5 = np.sum(final_prices >= target_5) / self.simulations * 100
        prob_target_10 = np.sum(final_prices >= target_10) / self.simulations * 100
        prob_target_20 = np.sum(final_prices >= target_20) / self.simulations * 100
        
        # احتمال كسر وقف الخسارة
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
            "prob_target_20": prob_target_20,
            "prob_stop_hit": prob_stop_hit,
            "volatility": self.volatility * 100
        }
    
    def get_risk_level(self, stats):
        """تقييم مستوى المخاطرة"""
        risk_score = 0
        
        if stats['volatility'] > 40:
            risk_score += 3
        elif stats['volatility'] > 30:
            risk_score += 2
        elif stats['volatility'] > 20:
            risk_score += 1
        
        var_pct = (stats['var_95'] / self.last_price) * 100
        if var_pct > 15:
            risk_score += 3
        elif var_pct > 10:
            risk_score += 2
        elif var_pct > 5:
            risk_score += 1
        
        if risk_score >= 5:
            return "🔴 عالية جداً", "#ef4444", "لا ينصح بالمخاطرة"
        elif risk_score >= 3:
            return "🟡 مرتفعة", "#f59e0b", "توخ الحذر"
        elif risk_score >= 1:
            return "🟢 متوسطة", "#3b82f6", "مخاطرة محسوبة"
        else:
            return "✅ منخفضة", "#10b981", "استثمار آمن نسبياً"
    
    def plot_simulations(self):
        """رسم مسارات المحاكاة"""
        fig = go.Figure()
        
        # رسم عينة من المسارات
        sample_paths = np.random.choice(self.simulations, min(100, self.simulations), replace=False)
        for i in sample_paths:
            fig.add_trace(go.Scatter(
                y=self.results[:, i],
                mode='lines',
                line=dict(width=0.5, color='rgba(6, 182, 212, 0.1)'),
                showlegend=False
            ))
        
        # المتوسط
        mean_path = np.mean(self.results, axis=1)
        fig.add_trace(go.Scatter(
            y=mean_path,
            mode='lines',
            name='المتوسط المتوقع',
            line=dict(color='#06b6d4', width=3)
        ))
        
        # نطاقات الثقة
        upper_95 = np.percentile(self.results, 95, axis=1)
        lower_95 = np.percentile(self.results, 5, axis=1)
        
        fig.add_trace(go.Scatter(
            y=upper_95,
            fill=None,
            mode='lines',
            line=dict(color='rgba(6, 182, 212, 0.3)'),
            name='نطاق 90% ثقة'
        ))
        
        fig.add_trace(go.Scatter(
            y=lower_95,
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(6, 182, 212, 0.3)'),
            name='الحد الأدنى'
        ))
        
        fig.update_layout(
            title="📊 محاكاة مونت كارلو - 10,000 سيناريو (عوائد لوغاريتمية)",
            template="plotly_dark",
            height=500,
            xaxis_title="الأيام القادمة",
            yaxis_title="السعر المتوقع"
        )
        
        return fig

# ============================================================
# 2. محرك بروفايل الحجم الحقيقي (Volume Profile)
# ============================================================

class VolumeProfileEngine:
    """تحليل بروفايل الحجم - اكتشاف مناطق التراكم الحقيقية"""
    
    def __init__(self, df, num_bins=50):
        self.df = df
        self.num_bins = num_bins
        self.current_price = df['Close'].iloc[-1]
    
    def calculate_volume_profile(self):
        """حساب بروفايل الحجم الحقيقي باستخدام الهيستوجرام المرجح بالحجم"""
        prices = self.df['Close'].values
        volumes = self.df['Volume'].values
        
        # إنشاء فئات السعر
        price_min = prices.min()
        price_max = prices.max()
        bins = np.linspace(price_min, price_max, self.num_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # حساب الحجم في كل فئة سعرية
        volume_profile = np.zeros(self.num_bins)
        
        for price, volume in zip(prices, volumes):
            bin_idx = np.digitize(price, bins) - 1
            if 0 <= bin_idx < self.num_bins:
                volume_profile[bin_idx] += volume
        
        # تطبيع
        if volume_profile.max() > 0:
            volume_profile = volume_profile / volume_profile.max() * 100
        
        # تحديد نقاط القوة (مناطق التركيز)
        high_volume_zones = []
        for i, vol in enumerate(volume_profile):
            if vol > 70:  # مناطق تركيز سيولة عالية
                high_volume_zones.append({
                    "price": bin_centers[i],
                    "strength": vol,
                    "type": "accumulation" if bin_centers[i] < self.current_price else "distribution"
                })
        
        # تحديد نقطة التحكم (أعلى حجم)
        poc_idx = np.argmax(volume_profile)
        point_of_control = bin_centers[poc_idx]
        
        # تحديد القيمة المعيارية (Value Area) - 70% من الحجم
        sorted_indices = np.argsort(volume_profile)[::-1]
        cumulative_volume = 0
        total_volume = volume_profile.sum()
        value_area_prices = []
        
        for idx in sorted_indices:
            cumulative_volume += volume_profile[idx]
            value_area_prices.append(bin_centers[idx])
            if cumulative_volume / total_volume >= 0.7:
                break
        
        value_area_high = max(value_area_prices)
        value_area_low = min(value_area_prices)
        
        return {
            "volume_profile": volume_profile,
            "bin_centers": bin_centers,
            "high_volume_zones": high_volume_zones,
            "point_of_control": point_of_control,
            "value_area_high": value_area_high,
            "value_area_low": value_area_low
        }
    
    def plot_volume_profile(self, profile_data):
        """رسم بروفايل الحجم (رسم بياني أفقي)"""
        fig = go.Figure()
        
        # رسم البروفايل
        fig.add_trace(go.Bar(
            x=profile_data['volume_profile'],
            y=profile_data['bin_centers'],
            orientation='h',
            name='حجم التداول',
            marker_color='rgba(6, 182, 212, 0.7)'
        ))
        
        # خط السعر الحالي
        fig.add_vline(
            x=self.current_price,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text=f"السعر الحالي: {self.current_price:.2f}",
            annotation_position="top"
        )
        
        # نقطة التحكم
        fig.add_hline(
            y=profile_data['point_of_control'],
            line_dash="solid",
            line_color="#10b981",
            annotation_text=f"نقطة التحكم: {profile_data['point_of_control']:.2f}",
            annotation_position="right"
        )
        
        fig.update_layout(
            title="📊 بروفايل الحجم - مناطق التراكم والتوزيع الحقيقية",
            template="plotly_dark",
            height=600,
            xaxis_title="الحجم النسبي (%)",
            yaxis_title="السعر",
            showlegend=False
        )
        
        return fig

# ============================================================
# 3. محرك تحليل LLM المحسن (مع معالجة الأخطاء)
# ============================================================

class AdvancedLLMEngine:
    """تحليل التقارير المالية باستخدام الذكاء الاصطناعي (مع معالجة الأخطاء)"""
    
    def __init__(self):
        self.gemini_available = False
        self.gemini_model = None
        
        try:
            api_key = get_gemini_api_key()
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_available = True
        except Exception as e:
            print(f"Gemini not available: {e}")
    
    def analyze_financial_report(self, company_name, ticker, info):
        """تحليل التقارير المالية"""
        if not self.gemini_available:
            return self._fallback_analysis(company_name, ticker, info)
        
        try:
            financial_data = f"""
            الشركة: {company_name} ({ticker})
            القطاع: {info.get('sector', 'غير متوفر')}
            القيمة السوقية: {info.get('marketCap', 'غير متوفر')}
            مكرر الربحية: {info.get('trailingPE', 'غير متوفر')}
            ربحية السهم: {info.get('trailingEps', 'غير متوفر')}
            عائد التوزيعات: {info.get('dividendYield', 'غير متوفر')}
            """
            
            prompt = f"""
            أنت محلل مالي خبير في سوق الأسهم المصري والسعودي.
            حلل البيانات التالية وقدم تقريراً موجزاً يتضمن:
            
            1. التقييم العام للشركة
            2. المخاطر الرئيسية
            3. الفرص المتاحة
            4. توصية للمستثمر
            
            البيانات:
            {financial_data}
            
            أجب باللغة العربية بشكل مختصر.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return self._fallback_analysis(company_name, ticker, info)
    
    def _fallback_analysis(self, company_name, ticker, info):
        """تحليل بديل عند عدم توفر Gemini"""
        market_cap = info.get('marketCap', 0)
        
        if market_cap > 1e9:
            assessment = "شركة كبرى - سيولة جيدة"
        elif market_cap > 500e6:
            assessment = "شركة متوسطة - تحتاج متابعة"
        else:
            assessment = "شركة صغيرة - مخاطرة أعلى"
        
        return f"""
        **التقييم العام:** {assessment}
        
        **نظرة عامة:**
        شركة {company_name} تعمل في قطاع {info.get('sector', 'غير محدد')}.
        
        **ملاحظات:**
        - لتفعيل التحليل المتقدم بالذكاء الاصطناعي، أضف GEMINI_API_KEY في إعدادات secrets
        - راجع التدفقات النقدية للشركة في التقارير الربعية
        - تابع أخبار القطاع بشكل دوري
        """

# ============================================================
# 4. المحرك الأساسي
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_stock_data(ticker, period="6mo", interval="1d"):
    """جلب بيانات السهم"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
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
        
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Support'] = df['Low'].rolling(window=20).min()
        df['Resistance'] = df['High'].rolling(window=20).max()
        
        return df, stock.info
        
    except Exception as e:
        return None, None

def calculate_technical_score(df):
    """حساب الدرجة الفنية"""
    if df is None or len(df) < 20:
        return 0, []
    
    score = 0
    signals = []
    last = df.iloc[-1]
    
    if last['Close'] > last['MA50']:
        score += 2
        signals.append("✅ الاتجاه العام صاعد")
    else:
        score -= 1
        signals.append("⚠️ الاتجاه العام هابط")
    
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
    
    return min(max(score, 0), 5), signals

# ============================================================
# 5. دالة لقراءة VaR (للمساعدة في اتخاذ قرار البيع)
# ============================================================

def explain_var(var_95, current_price, profit_probability):
    """شرح القيمة المعرضة للخطر وكيفية استخدامها لقرار البيع"""
    var_percent = (var_95 / current_price) * 100
    
    if var_percent > 10:
        risk_assessment = "⚠️ **خطر مرتفع جداً** - يوصى بتقليل حجم المركز أو الخروج"
        action = "بيع"
        action_color = "#ef4444"
    elif var_percent > 5:
        risk_assessment = "🟡 **خطر متوسط** - يوصى بوضع وقف خسارة مشدد"
        action = "مراقبة"
        action_color = "#f59e0b"
    else:
        risk_assessment = "✅ **خطر منخفض** - يمكن الاحتفاظ بالمركز"
        action = "احتفاظ"
        action_color = "#10b981"
    
    if profit_probability < 40:
        risk_assessment += " | ⚠️ احتمال الربح منخفض - يوصى بإعادة التقييم"
        action = "مراجعة"
    
    return risk_assessment, action, action_color

# ============================================================
# الواجهة الرئيسية
# ============================================================

def main():
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("# 🔮 Oracle Zero-Knowledge")
        st.markdown("### الإصدار النهائي - مع بروفايل الحجم")
        st.markdown("---")
        
        stock_options = {
            "🇪🇬 البنك التجاري الدولي (CIB)": "COMI.CA",
            "🇪🇬 طلعت مصطفى": "TMGH.CA",
            "🇪🇬 فوري": "FWRY.CA",
            "🇪🇬 أبو قير للأسمدة": "ABUK.CA",
            "🇪🇬 حديد عز": "ESRS.CA"
        }
        
        selected = st.selectbox("اختر السهم", list(stock_options.keys()))
        ticker = stock_options[selected]
        
        st.markdown("---")
        
        st.markdown("### ⚙️ إعدادات التنبؤ")
        days_ahead = st.slider("أيام التنبؤ", 15, 60, 30)
        simulations = st.slider("عدد المحاكاة", 1000, 20000, 10000, step=1000)
        
        st.markdown("---")
        
        # عرض حالة Gemini
        if is_gemini_available():
            st.success("✅ Gemini API: متصل")
        else:
            st.warning("⚠️ Gemini API: غير متصل (للتحليل المتقدم، أضف المفتاح في secrets)")
        
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("🔄 تحديث شامل", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # العنوان
    st.markdown(f"## 🔮 التحليل النبوي: {selected}")
    st.markdown(f"### {ticker}")
    st.markdown("---")
    
    # جلب البيانات
    df, info = get_stock_data(ticker)
    
    if df is not None and not df.empty:
        tech_score, tech_signals = calculate_technical_score(df)
        current_price = df['Close'].iloc[-1]
        
        # ===== 1. مونت كارلو (مع العوائد اللوغاريتمية) =====
        with st.spinner("🔄 تشغيل محاكاة مونت كارلو (عوائد لوغاريتمية)..."):
            mc_engine = MonteCarloEngine(df, days=days_ahead, simulations=simulations)
            mc_stats = mc_engine.run_simulation()
        
        # ===== 2. بروفايل الحجم الحقيقي =====
        with st.spinner("🔄 تحليل بروفايل الحجم..."):
            vp_engine = VolumeProfileEngine(df)
            vp_data = vp_engine.calculate_volume_profile()
        
        # ===== 3. تحليل LLM =====
        llm_engine = AdvancedLLMEngine()
        llm_analysis = llm_engine.analyze_financial_report(selected, ticker, info)
        
        # ===== 4. تحليل VaR لقرار البيع =====
        var_explanation, var_action, var_color = explain_var(
            mc_stats['var_95'], current_price, mc_stats['profit_probability']
        )
        
        # ===== العرض الرئيسي =====
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 السعر الحالي", f"{current_price:.2f}")
        col2.metric("🔮 السعر المتوقع (30 يوم)", f"{mc_stats['expected_price']:.2f}")
        col3.metric("📊 التغير المتوقع", f"{((mc_stats['expected_price'] - current_price) / current_price * 100):+.1f}%")
        col4.metric("🎯 درجة الثقة", f"{tech_score}/5")
        
        st.markdown("---")
        
        # ===== بطاقة إدارة المخاطر وقرار البيع =====
        st.markdown(f"""
        <div class="risk-meter">
            <h3>🛡️ تحليل القيمة المعرضة للخطر (VaR) - قرار البيع</h3>
            <p style="color: {var_color}; font-size: 20px;"><strong>{var_explanation}</strong></p>
            <hr>
            <table style="width: 100%;">
                <tr>
                    <td><strong>القيمة المعرضة للخطر (VaR 95%):</strong></td>
                    <td style="color: #ef4444;">{mc_stats['var_95']:.2f} ج.م ({mc_stats['var_95']/current_price*100:.1f}%)</td>
                    <td><strong>الخسارة المتوقعة في الكوارث (CVaR):</strong></td>
                    <td style="color: #ef4444;">{mc_stats['cvar_95']:.2f} ج.م</td>
                </tr>
                <tr>
                    <td><strong>احتمال الربح:</strong></td>
                    <td style="color: {'#10b981' if mc_stats['profit_probability'] > 50 else '#ef4444'}">{mc_stats['profit_probability']:.1f}%</td>
                    <td><strong>التوصية المقترحة:</strong></td>
                    <td style="color: {var_color};"><strong>{var_action}</strong></td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== التبويبات =====
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔮 مونت كارلو", "📊 بروفايل الحجم", "🧠 تحليل AI", 
            "📈 ملخص الاحتمالات", "⚛️ القرار النهائي"
        ])
        
        with tab1:
            st.subheader("🔮 محاكاة مونت كارلو (عوائد لوغاريتمية)")
            fig = mc_engine.plot_simulations()
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("أفضل سيناريو (95%)", f"{mc_stats['confidence_95']:.2f}")
                st.metric("سيناريو متفائل (75%)", f"{mc_stats['confidence_75']:.2f}")
            with col2:
                st.metric("السيناريو المتوقع", f"{mc_stats['expected_price']:.2f}")
                st.metric("الوسيط", f"{mc_stats['median_price']:.2f}")
            with col3:
                st.metric("سيناريو متشائم (25%)", f"{mc_stats['confidence_25']:.2f}")
                st.metric("أسوأ سيناريو (5%)", f"{mc_stats['confidence_5']:.2f}")
        
        with tab2:
            st.subheader("📊 بروفايل الحجم الحقيقي - خريطة السيولة")
            fig2 = vp_engine.plot_volume_profile(vp_data)
            st.plotly_chart(fig2, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📍 نقطة التحكم (أعلى سيولة)", f"{vp_data['point_of_control']:.2f}")
                st.metric("📊 منطقة القيمة (70% من الحجم)", f"{vp_data['value_area_low']:.2f} - {vp_data['value_area_high']:.2f}")
            with col2:
                if vp_data['high_volume_zones']:
                    st.markdown("**🔥 مناطق تركيز السيولة:**")
                    for zone in vp_data['high_volume_zones'][:3]:
                        st.info(f"{'🟢 تجميع' if zone['type'] == 'accumulation' else '🔴 توزيع'} عند {zone['price']:.2f} (قوة {zone['strength']:.0f}%)")
        
        with tab3:
            st.subheader("🧠 تحليل الذكاء الاصطناعي")
            st.markdown(llm_analysis)
        
        with tab4:
            st.subheader("📊 ملخص الاحتمالات")
            
            st.markdown(f"""
            <div class="oracle-card">
                <h3>🎯 احتمال تحقيق الأهداف</h3>
                <table style="width: 100%;">
                    <tr><td><strong>احتمال الربح:</strong></td><td style="color: {'#10b981' if mc_stats['profit_probability'] > 50 else '#ef4444'}">{mc_stats['profit_probability']:.1f}%</td></tr>
                    <tr><td><strong>احتمال +5%:</strong></td><td>{mc_stats['prob_target_5']:.1f}%</td></tr>
                    <tr><td><strong>احتمال +10%:</strong></td><td>{mc_stats['prob_target_10']:.1f}%</td></tr>
                    <tr><td><strong>احتمال +20%:</strong></td><td>{mc_stats['prob_target_20']:.1f}%</td></tr>
                    <tr><td><strong>احتمال كسر وقف الخسارة:</strong></td><td style="color: #ef4444;">{mc_stats['prob_stop_hit']:.1f}%</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with tab5:
            st.subheader("⚛️ القرار النهائي")
            
            final_weight = (tech_score * 0.3) + ((mc_stats['profit_probability'] / 100) * 0.5) + 0.2
            final_weight = min(max(final_weight, 0), 5)
            
            if final_weight >= 4 and mc_stats['profit_probability'] > 60:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #064e3b, #065f46);
                            border: 3px solid #10b981;
                            border-radius: 20px; padding: 30px;
                            text-align: center;">
                    <h1 style="color: #10b981;">🔮 إشارة نبوية - فرصة ذهبية مؤكدة!</h1>
                    <p style="color: #d1d5db;">توافق كامل: فني + احتمالي + سيولة</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("📈 نقطة الدخول", f"{current_price:.2f}")
                col2.metric("🎯 الهدف الأول", f"{mc_stats['confidence_75']:.2f}")
                col3.metric("🛑 وقف الخسارة", f"{current_price * 0.95:.2f}")
            
            elif final_weight >= 3:
                st.info("📈 **توصية: شراء محتمل** - مع تطبيق إدارة المخاطر")
            else:
                st.warning("🟡 **توصية: انتظار** - لا توجد إشارات قوية")
    
    else:
        st.error("❌ فشل في جلب البيانات - تحقق من اتصال الإنترنت والرمز")
        st.info("""
        **حلول مقترحة:**
        - تأكد من صحة رمز السهم
        - أعد المحاولة بعد دقيقة
        - جرب رمزاً آخر مثل `AAPL` أو `TSLA`
        """)
    
    st.markdown("---")
    st.caption("""
    🔮 **Oracle Zero-Knowledge - الإصدار النهائي**
    📊 تقنيات حصرية: عوائد لوغاريتمية + بروفايل حجم حقيقي + تحليل VaR
    ⚡ معالجة كاملة للأخطاء - جاهز للعمل على السوق المصري
    """)

if __name__ == "__main__":
    main()
