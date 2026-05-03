# database.py - النسخة الشاملة لكل ما يخص البورصة المصرية
from typing import Dict, List, Optional

# -------------------------------------------------------------------
# 1. الأسهم العادية (أسهم الشركات)
# -------------------------------------------------------------------
REGULAR_STOCKS = {
    # البنوك
    "البنك التجاري الدولي (CIB)": "COMI.CA",
    "بنك مصر": "BMEL.CA",
    "البنك الأهلي المصري": "NBE.CA",
    # ... أضف باقي الأسهم هنا كما في الكود الأصلي ...
}

# -------------------------------------------------------------------
# 2. صناديق الاستثمار المصرية (Egyptian Investment Funds)
# -------------------------------------------------------------------
INVESTMENT_FUNDS = {
    "بلتون أويل آند گاز": "BTFH.CA",
    "بلتون ميم": "BTFH.CA",
    "بلتون تارجت": "BTFH.CA",
    "هيرمس للصناديق": "HRHO.CA",
    "برايم القابضة": "PRMH.CA",
    "القلعة القابضة": "CCAP.CA",
    "AZ آرابيا أكتوبر": "AZNO.CA",
    "آي دي إف (صندوق مصر للاستثمار)": "IDF.CA",
}

# -------------------------------------------------------------------
# 3. صناديق المؤشرات المتداولة (ETFs) المصرية والعربية
# -------------------------------------------------------------------
ETFS = {
    "صندوق المؤشر الأول للبورصة المصرية": "XHD.CA",
    "صندوق إي إم آي إيه للأسهم القيادية": "EMIA.CA",
    "صندوق مصر للأسهم القيادية": "XHD.CA",
    "صندوق النفط والطاقة": "OILE.CA",
}

# -------------------------------------------------------------------
# 4. أسهم قطاع التعدين والبترول (Mining & Petroleum)
# -------------------------------------------------------------------
MINING_PETROLEUM_STOCKS = {
    # تعدين
    "مصر للألومنيوم": "EGAL.CA",
    "الحديد والصلب المصرية": "IRON.CA",
    "الإسكندرية للحديد والصلب": "ALEX.CA",
    "سيدبك للتعدين": "SKPC.CA",
    "النصر للتعدين": "NMDC.CA",
    "المصرية للثروات التعدينية": "EMC.CA",
    
    # بترول وطاقة
    "الإسكندرية للبترول": "APC.CA",
    "مصر للطيران القابضة": "EGAL.CA",
    "بترول أسوان": "APC.CA",
    "القاهرة لتكرير البترول": "CORC.CA",
    "الشرقية للبترول": "EPC.CA",
    "ميدور لتكرير البترول": "MIDC.CA",
    "طاقة عربية": "TAGI.CA",
    "طاقة مصر (Egypt Gas)": "EGAS.CA",
    "الإسكندرية للزيوت المعدنية": "AMOC.CA",
}

# -------------------------------------------------------------------
# 5. العملات الأجنبية والفوركس (Forex) للسياق المحلي
# -------------------------------------------------------------------
FOREX_PAIRS = {
    "الدولار / الجنيه المصري": "EGP=X",
    "اليورو / الجنيه المصري": "EURUSD=X",
    "الجنيه الإسترليني / الجنيه المصري": "GBPUSD=X",
    "الريال السعودي / الجنيه المصري": "SAR=X",
    "الدرهم الإماراتي / الجنيه المصري": "AED=X",
    
    "اليورو مقابل الدولار": "EURUSD=X",
    "الجنيه الإسترليني مقابل الدولار": "GBPUSD=X",
    "الدولار مقابل الين الياباني": "JPY=X",
}

# -------------------------------------------------------------------
# 6. السلع الأساسية والمعادن الثمينة (Commodities)
# -------------------------------------------------------------------
COMMODITIES = {
    # المعادن الثمينة
    "الذهب (أونصة)": "GC=F",
    "الفضة (أونصة)": "SI=F",
    "البلاتين (أونصة)": "PL=F",
    "النحاس": "HG=F",
    
    # الطاقة
    "خام برنت": "BZ=F",
    "خام غرب تكساس (WTI)": "CL=F",
    "الغاز الطبيعي": "NG=F",
    
    # الزراعة
    "الذرة": "C=F",
    "الخام الأمريكي": "ZW=F",
    "فول الصويا": "ZS=F",
    "القطن": "CT=F",
    
    # الغذاء
    "السكر": "SB=F",
    "البن": "KC=F",
    "الكاكاو": "CC=F",
}

# -------------------------------------------------------------------
# دمج كل شيء في قاموس واحد شامل
# -------------------------------------------------------------------
ALL_INSTRUMENTS = {}

# دمج الأسهم
for name, ticker in REGULAR_STOCKS.items():
    ALL_INSTRUMENTS[f"🇪🇬 {name}"] = {"ticker": ticker, "type": "stock"}

# دمج صناديق الاستثمار
for name, ticker in INVESTMENT_FUNDS.items():
    ALL_INSTRUMENTS[f"💰 {name} (صندوق استثمار)"] = {"ticker": ticker, "type": "fund"}

# دمج صناديق المؤشرات ETF
for name, ticker in ETFS.items():
    ALL_INSTRUMENTS[f"📊 {name} (ETF)"] = {"ticker": ticker, "type": "etf"}

# دمج أسهم البترول والتعدين
for name, ticker in MINING_PETROLEUM_STOCKS.items():
    ALL_INSTRUMENTS[f"⛏️ {name}"] = {"ticker": ticker, "type": "commodity_stock"}

# دمج الفوركس
for name, ticker in FOREX_PAIRS.items():
    ALL_INSTRUMENTS[f"💱 {name}"] = {"ticker": ticker, "type": "forex"}

# دمج السلع
for name, ticker in COMMODITIES.items():
    ALL_INSTRUMENTS[f"🏆 {name}"] = {"ticker": ticker, "type": "commodity"}

# للحفاظ على التوافق مع كود app.py القديم (حيث يتوقع وجود EGYPTIAN_STOCKS)
EGYPTIAN_STOCKS = REGULAR_STOCKS

# -------------------------------------------------------------------
# دوال مساعدة محسنة للبحث في كل شيء
# -------------------------------------------------------------------
def get_all_stocks() -> Dict:
    """إرجاع جميع الأدوات (للتوافق مع الكود القديم)"""
    return ALL_INSTRUMENTS

def search_stock(keyword: str) -> Dict:
    """البحث في الأسهم، الصناديق، السلع، والعملات"""
    results = {}
    keyword_lower = keyword.lower()
    
    for display_name, data in ALL_INSTRUMENTS.items():
        ticker = data['ticker']
        if (keyword_lower in display_name.lower() or 
            keyword_lower in ticker.lower() or
            keyword_lower in ticker.replace('.CA', '').lower()):
            results[display_name] = {
                'ticker': ticker,
                'type': data['type'],
                'name': display_name
            }
    
    return results

def get_market_statistics() -> Dict:
    """احصائيات شاملة عن كل القطاعات"""
    return {
        "total_stocks": len(REGULAR_STOCKS),
        "total_funds": len(INVESTMENT_FUNDS),
        "total_etfs": len(ETFS),
        "total_mining": len(MINING_PETROLEUM_STOCKS),
        "total_forex": len(FOREX_PAIRS),
        "total_commodities": len(COMMODITIES),
        "sectors": ["بنوك", "عقارات", "طاقة", "اتصالات", "بترول", "تعدين", "صناديق", "سلع"],
        "currency": "EGP",
        "trading_hours": "10:00 - 14:30"
    }

# باقي الدوال (get_market_info, get_all_sectors, ...) تبقى كما هي أو يمكن تحديثها حسب الحاجة.
