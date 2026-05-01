# ============================================================
# ملف: engines.py
# المحركات الحسابية المتقدمة (مونت كارلو، بروفايل الحجم، Smart Money)
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go

class MonteCarloEngine:
    """محاكاة مونت كارلو"""
    
    def __init__(self, df, days=30, simulations=5000):
        self.df = df
        self.days = days
        self.simulations = simulations
        self.last_price = df['Close'].iloc[-1]
        
        self.log_returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
        
        if len(self.log_returns) < 5:
            self.mu = 0.0005
            self.sigma = 0.02
        else:
            self.mu = self.log_returns.mean()
            self.sigma = self.log_returns.std()
        
        self.volatility = self.sigma * np.sqrt(252) if self.sigma else 0.2
        self.results = None
    
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
            "std_dev": np.std(final_prices),
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
            "volatility": self.volatility * 100,
        }
    
    def plot_simulations(self):
        fig = go.Figure()
        
        sample_paths = np.random.choice(self.simulations, min(100, self.simulations), replace=False)
        for i in sample_paths:
            fig.add_trace(go.Scatter(y=self.results[:, i], mode='lines',
                                     line=dict(width=0.5, color='rgba(16, 185, 129, 0.1)'), showlegend=False))
        
        mean_path = np.mean(self.results, axis=1)
        fig.add_trace(go.Scatter(y=mean_path, mode='lines', name='المتوسط المتوقع',
                                 line=dict(color='#10b981', width=3)))
        
        upper_95 = np.percentile(self.results, 95, axis=1)
        lower_95 = np.percentile(self.results, 5, axis=1)
        
        fig.add_trace(go.Scatter(y=upper_95, fill=None, mode='lines',
                                 line=dict(color='rgba(16, 185, 129, 0.3)'), name='حد أعلى 95%'))
        fig.add_trace(go.Scatter(y=lower_95, fill='tonexty', mode='lines',
                                 line=dict(color='rgba(16, 185, 129, 0.3)'), name='حد أدنى 95%'))
        
        fig.update_layout(template="plotly_dark", height=500,
                         title="📊 محاكاة مونت كارلو - 5,000 سيناريو")
        return fig


class VolumeProfileEngine:
    """بروفايل الحجم"""
    
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
            "point_of_control": point_of_control,
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


class TechnicalAnalysisEngine:
    """محرك التحليل الفني المتقدم"""
    
    @staticmethod
    def calculate_score(df):
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
        
        if 'Volume_MA' in df.columns:
            vol_ratio = last['Volume'] / last['Volume_MA'] if last['Volume_MA'] > 0 else 1
            if vol_ratio > 2:
                signals.append(f"💰 سيولة عالية جداً ({vol_ratio:.1f}x)")
                score += 1
            elif vol_ratio > 1.5:
                signals.append(f"💰 سيولة جيدة ({vol_ratio:.1f}x)")
                score += 0.5
        
        return min(max(score, 0), 5), signals
    
    @staticmethod
    def detect_smart_money(df):
        """
        اكتشاف دخول المؤسسات (Smart Money)
        إذا كان السعر يتحرك عرضياً مع حجم تداول عالي جداً، فهذا تجميع مؤسسي
        """
        if df is None or len(df) < 20:
            return None
        
        last = df.iloc[-1]
        vol_spike = last['Volume'] > (df['Volume_MA'].iloc[-1] * 2) if 'Volume_MA' in df.columns else False
        price_range = (last['High'] - last['Low']) / last['Close']
        
        # السعر يتحرك في نطاق ضيق (عرضي) مع حجم عالي
        is_consolidation = price_range < df['Close'].pct_change().std() * 0.5
        
        if vol_spike and is_consolidation:
            return {
                "signal": "🔥 اكتشاف تجميع مؤسسي (Smart Money)",
                "strength": "قوي",
                "action": "متابعة لصيقة"
            }
        elif vol_spike:
            return {
                "signal": "⚠️ نشاط غير طبيعي - قد يكون دخول مؤسسات أو تصريف",
                "strength": "متوسط",
                "action": "مراقبة"
            }
        
        return None


class RiskManagementEngine:
    """محرك إدارة المخاطر"""
    
    @staticmethod
    def calculate_position_size(capital, price, stop_loss, risk_percent=2):
        if stop_loss <= 0 or price <= stop_loss:
            return 0, 0, 0
        
        risk_amount = capital * (risk_percent / 100)
        stop_distance = price - stop_loss
        shares = int(risk_amount / stop_distance)
        total_cost = shares * price
        actual_risk = (total_cost / capital) * 100 if capital > 0 else 0
        
        return shares, round(total_cost, 2), round(actual_risk, 1)
    
    @staticmethod
    def get_risk_level(volatility, var_95, current_price):
        var_percent = (var_95 / current_price) * 100 if current_price > 0 else 0
        
        if volatility > 40 or var_percent > 15:
            return "🔴 عالية جداً", "#ef4444", "لا ينصح بالمخاطرة"
        elif volatility > 30 or var_percent > 10:
            return "🟡 مرتفعة", "#f59e0b", "توخ الحذر"
        elif volatility > 20 or var_percent > 5:
            return "🟢 متوسطة", "#3b82f6", "مخاطرة محسوبة"
        else:
            return "✅ منخفضة", "#10b981", "استثمار آمن نسبياً"


class GoldenSignalEngine:
    """محرك توليد الإشارة الذهبية"""
    
    @staticmethod
    def calculate_final_score(tech_score, mc_stats, news_score, macro_score, intelligence_score=0):
        total_score = (tech_score * 0.25) + \
                     ((mc_stats['profit_probability'] / 100) * 0.25) + \
                     ((news_score / 100) * 0.2) + \
                     ((macro_score / 5) * 0.15) + \
                     (intelligence_score * 0.15)
        
        return min(max(total_score, 0), 5)
    
    @staticmethod
    def get_signal(final_score):
        if final_score >= 4:
            return "🟢 إشارة ذهبية - فرصة شراء قوية", final_score
        elif final_score >= 3:
            return "📈 إشارة شراء محتملة", final_score
        elif final_score >= 2:
            return "🟡 مراقبة - انتظار تأكيد", final_score
        else:
            return "🔴 تجنب - إشارات سلبية", final_score


class ComparisonEngine:
    """محرك مقارنة الأسهم - لمقارنة سهمين من نفس القطاع"""
    
    @staticmethod
    def compare_stocks(df1, df2, name1, name2):
        """مقارنة سهمين وإرجاع أيهما أفضل"""
        
        # حساب الدرجات
        score1, _ = TechnicalAnalysisEngine.calculate_score(df1)
        score2, _ = TechnicalAnalysisEngine.calculate_score(df2)
        
        # مقارنة الأداء
        perf1 = (df1['Close'].iloc[-1] - df1['Close'].iloc[-20]) / df1['Close'].iloc[-20] * 100 if len(df1) > 20 else 0
        perf2 = (df2['Close'].iloc[-1] - df2['Close'].iloc[-20]) / df2['Close'].iloc[-20] * 100 if len(df2) > 20 else 0
        
        # تقييم المخاطرة
        vol1 = df1['Close'].pct_change().std() * np.sqrt(252) * 100 if len(df1) > 1 else 0
        vol2 = df2['Close'].pct_change().std() * np.sqrt(252) * 100 if len(df2) > 1 else 0
        
        # تحديد الأفضل
        if score1 > score2 and perf1 > perf2:
            winner = name1
            reason = f"درجة أعلى ({score1} vs {score2}) وأداء أفضل ({perf1:.1f}% vs {perf2:.1f}%)"
        elif score2 > score1 and perf2 > perf1:
            winner = name2
            reason = f"درجة أعلى ({score2} vs {score1}) وأداء أفضل ({perf2:.1f}% vs {perf1:.1f}%)"
        elif score1 > score2:
            winner = name1
            reason = f"درجة فنية أعلى ({score1} vs {score2})"
        else:
            winner = name2
            reason = f"درجة فنية أعلى ({score2} vs {score1})"
        
        return {
            "winner": winner,
            "reason": reason,
            "score1": score1,
            "score2": score2,
            "perf1": round(perf1, 1),
            "perf2": round(perf2, 1),
            "vol1": round(vol1, 1),
            "vol2": round(vol2, 1)
        }
