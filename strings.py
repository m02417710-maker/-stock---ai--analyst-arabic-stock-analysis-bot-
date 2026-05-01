# ============================================================
# strings.py - جميع نصوص الواجهة في مكان واحد
# لتسهيل التعديل والصيانة والترجمة لاحقاً
# ============================================================

UI_TEXT = {
    # عناوين رئيسية
    "app_title": "📊 المحلل المالي المتكامل — Pro",
    "app_subtitle": "تحليل فني | توقعات مونت كارلو | إدارة مخاطر | ماسح سوق",
    
    # الشريط الجانبي
    "sidebar_capital": "💰 إدارة رأس المال",
    "sidebar_capital_label": "المبلغ بالدولار",
    "sidebar_risk_label": "نسبة المخاطرة (%)",
    "sidebar_update_btn": "تحديث الآن",
    "sidebar_refresh": "تحديث تلقائي كل 5 دقائق",
    "sidebar_stocks_count": "إجمالي الأسهم",
    
    # الصفحة الرئيسية
    "page_title": "تحليل {selected} — نظرة سريعة",
    "ticker_label": "الرمز: {ticker}",
    
    # بطاقات المؤشرات
    "metric_price": "السعر",
    "metric_confidence": "ثقة التحليل",
    "metric_rsi": "RSI",
    "metric_position": "قيمة الصفقة المقترحة",
    "metric_profit_prob": "احتمال الربح",
    "metric_target_10": "هدف +10%",
    "metric_var_95": "VaR 95%",
    "metric_stop_prob": "كسر الوقف",
    
    # بطاقة التوصية
    "recommendation_title": "توصية حالية",
    "price_info": "وقف خسارة: {stop:.2f} · هدف: {target:.2f}",
    
    # التبويبات
    "tab_chart": "الرسم البياني",
    "tab_analysis": "التحليل الفني",
    "tab_forecast": "التوقعات",
    "tab_risk": "إدارة المخاطر",
    "tab_scanner": "ماسح السوق",
    
    # تبويب التحليل الفني
    "analysis_signals_title": "تفاصيل الإشارات الفنية",
    "analysis_points_title": "نقاط التداول",
    "analysis_entry": "نقطة الدخول",
    "analysis_target1": "الهدف الأول (مقاومة)",
    "analysis_target2": "الهدف الثاني (8%)",
    "analysis_target3": "الهدف الثالث (10%)",
    "analysis_stop": "وقف الخسارة (5%)",
    "analysis_risk_reward": "نسبة المخاطرة/العائد",
    
    # تبويب التوقعات
    "forecast_title": "توقعات مونت كارلو (GBM)",
    "forecast_expected": "السعر المتوقع",
    "forecast_median": "السعر الوسيط",
    "forecast_best": "أفضل سيناريو (95%)",
    "forecast_worst": "أسوأ سيناريو (5%)",
    "forecast_profit": "احتمال الربح",
    "forecast_target": "احتمال +10%",
    "forecast_analysis_profit": "التحليل الإحصائي: احتمال الربح {prob:.0f}% - {assessment}",
    "forecast_good": "فرصة مواتية",
    "forecast_average": "متوسط",
    "forecast_caution": "توخ الحذر",
    
    # تبويب إدارة المخاطر
    "risk_title": "إدارة المخاطر المتقدمة",
    "risk_capital": "رأس المال",
    "risk_allowed": "نسبة المخاطرة المسموحة",
    "risk_shares": "عدد الأسهم المقترح",
    "risk_position": "قيمة الصفقة",
    "risk_actual": "المخاطرة الفعلية",
    "risk_total": "المخاطرة الكلية",
    "risk_recommendations": "توصيات إدارة المخاطر",
    "risk_warning_invalid": "خطأ: إعداد وقف الخسارة غير صالح",
    "risk_warning_exceed": "تحذير: المخاطرة الفعلية ({actual}%) تتجاوز الحد المسموح ({allowed}%)",
    "risk_safe": "مناسب: المخاطرة ضمن الحدود المسموحة",
    "risk_principles_title": "مبادئ إدارة المخاطر",
    "risk_principle_1": "القاعدة الذهبية: لا تخاطر بأكثر من 1-2% من رأس المال في صفقة واحدة",
    "risk_principle_2": "نسبة المخاطرة/العائد: يفضل أن تكون 1:2 على الأقل",
    "risk_principle_3": "تنويع المحفظة: لا تضع كل رأس المال في قطاع واحد",
    "risk_principle_4": "وقف الخسارة المتحرك: ارفع وقف الخسارة بعد تحقيق أرباح",
    
    # تبويب الماسح
    "scanner_title": "ماسح السوق الذكي",
    "scanner_button": "تشغيل الماسح الضوئي",
    "scanner_success": "تم فحص {count} سهمًا بنجاح",
    "scanner_top_title": "أفضل 5 فرص استثمارية",
    "scanner_no_data": "لا توجد بيانات كافية للمسح",
    
    # أخطاء وحلول
    "error_fetch": "تعذر جلب البيانات",
    "error_solutions": "اقتراحات إصلاح: تأكد من اتصال الإنترنت; أعد المحاولة بعد دقيقة; جرّب رمزاً آخر.",
    
    # تذييل
    "footer": "تحليل فني متقدم | توقعات مونت كارلو (GBM) | إدارة مخاطر احترافية | ماسح سوق متوازي",
}

# مستويات التوصية
RECOMMENDATIONS = {
    "strong_buy": {"text": "🔥🔥 شراء قوي جداً", "color": "#10b981"},
    "buy": {"text": "🟢 شراء قوي", "color": "#22c55e"},
    "potential_buy": {"text": "📈 شراء محتمل", "color": "#3b82f6"},
    "watch": {"text": "🟡 مراقبة", "color": "#f59e0b"},
    "avoid": {"text": "🔴 تجنب", "color": "#ef4444"},
    "no_data": {"text": "لا توجد بيانات", "color": "#6b7280"},
}

# إشارات التحليل
SIGNAL_TYPES = {
    "positive": ["✅", "🔥", "💰", "🚀", "🎯"],
    "warning": ["⚠️"],
    "neutral": ["📊", "📈", "📉"],
}
