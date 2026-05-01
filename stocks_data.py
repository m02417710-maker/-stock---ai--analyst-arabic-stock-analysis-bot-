# ============================================================
# ملف: stocks_data.py
# قاعدة بيانات الأسهم مع التصنيفات القطاعية
# ============================================================

# تعريف القطاعات الاقتصادية
SECTORS = {
    "القطاع البنكي": ["COMI.CA", "BMEL.CA", "ADIB.CA", "HDBK.CA"],
    "العقارات والتشييد": ["TMGH.CA", "ORAS.CA", "PHDC.CA", "OCDI.CA"],
    "الأسمدة والبتروكيماويات": ["ABUK.CA", "MFOT.CA", "EKHO.CA", "EGPC.CA"],
    "التكنولوجيا والاتصالات": ["FWRY.CA", "ISLS.CA", "ETEL.CA", "RADO.CA"],
    "الغذاء والدواء": ["JUFO.CA", "BIM.CA", "SUCE.CA", "AMOC.CA"],
    "الطاقة": ["EGPC.CA", "MOPC.CA", "APSW.CA"],
    "السياحة والترفيه": ["ORAS.CA", "PHDC.CA"],
    "النقل والخدمات": ["DSCW.CA", "SVTS.CA"]
}

# الأسهم المصرية مع قطاعاتها
EGYPT_STOCKS = {
    "🇪🇬 البنك التجاري الدولي (CIB)": {"ticker": "COMI.CA", "sector": "القطاع البنكي"},
    "🇪🇬 طلعت مصطفى القابضة": {"ticker": "TMGH.CA", "sector": "العقارات والتشييد"},
    "🇪🇬 فوري لتكنولوجيا البنوك": {"ticker": "FWRY.CA", "sector": "التكنولوجيا والاتصالات"},
    "🇪🇬 المجموعة المالية هيرميس": {"ticker": "HRHO.CA", "sector": "القطاع البنكي"},
    "🇪🇬 حديد عز": {"ticker": "ESRS.CA", "sector": "العقارات والتشييد"},
    "🇪🇬 جهينة للصناعات الغذائية": {"ticker": "JUFO.CA", "sector": "الغذاء والدواء"},
    "🇪🇬 أبو قير للأسمدة": {"ticker": "ABUK.CA", "sector": "الأسمدة والبتروكيماويات"},
    "🇪🇬 بنك مصر": {"ticker": "BMEL.CA", "sector": "القطاع البنكي"},
    "🇪🇬 المصرية للاتصالات": {"ticker": "ETEL.CA", "sector": "التكنولوجيا والاتصالات"},
    "🇪🇬 العاشر من رمضان للصناعات الدوائية": {"ticker": "RADO.CA", "sector": "الغذاء والدواء"},
}

# الأسهم السعودية
SAUDI_STOCKS = {
    "🇸🇦 أرامكو السعودية": {"ticker": "2222.SR", "sector": "الطاقة"},
    "🇸🇦 بنك الراجحي": {"ticker": "1120.SR", "sector": "القطاع البنكي"},
    "🇸🇦 الاتصالات السعودية (STC)": {"ticker": "7010.SR", "sector": "التكنولوجيا والاتصالات"},
    "🇸🇦 سابك": {"ticker": "2010.SR", "sector": "البتروكيماويات"},
    "🇸🇦 البنك الأهلي السعودي": {"ticker": "1180.SR", "sector": "القطاع البنكي"},
}

# الأسهم الأمريكية
US_STOCKS = {
    "🇺🇸 آبل - Apple": {"ticker": "AAPL", "sector": "التكنولوجيا"},
    "🇺🇸 تسلا - Tesla": {"ticker": "TSLA", "sector": "السيارات"},
    "🇺🇸 مايكروسوفت - Microsoft": {"ticker": "MSFT", "sector": "التكنولوجيا"},
    "🇺🇸 إنفيديا - NVIDIA": {"ticker": "NVDA", "sector": "التكنولوجيا"},
    "🇺🇸 أمازون - Amazon": {"ticker": "AMZN", "sector": "التجارة الإلكترونية"},
    "🇺🇸 جوجل - Google": {"ticker": "GOOGL", "sector": "التكنولوجيا"},
}

# دوال مساعدة للتعامل مع البيانات
def get_ticker(stock):
    """استخراج الرمز من كائن السهم"""
    if isinstance(stock, dict):
        return stock.get("ticker", "")
    return stock

def get_sector(stock):
    """استخراج القطاع من كائن السهم"""
    if isinstance(stock, dict):
        return stock.get("sector", "غير محدد")
    return "غير محدد"

def get_all_tickers():
    """الحصول على جميع الرموز"""
    tickers = []
    for stock in EGYPT_STOCKS.values():
        tickers.append(get_ticker(stock))
    for stock in SAUDI_STOCKS.values():
        tickers.append(get_ticker(stock))
    for stock in US_STOCKS.values():
        tickers.append(get_ticker(stock))
    return tickers

# دالة للحصول على أسهم قطاع معين
def get_sector_stocks(sector_name):
    """الحصول على جميع أسهم قطاع معين"""
    if sector_name in SECTORS:
        return SECTORS[sector_name]
    return []

# إحصاءات
STOCKS_STATS = {
    "egypt": len(EGYPT_STOCKS),
    "saudi": len(SAUDI_STOCKS),
    "us": len(US_STOCKS),
    "total": len(EGYPT_STOCKS) + len(SAUDI_STOCKS) + len(US_STOCKS),
    "sectors": len(SECTORS)
}
