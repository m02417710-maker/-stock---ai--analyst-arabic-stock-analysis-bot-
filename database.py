# database.py - النسخة الشاملة لكل ما يخص البورصة المصرية
"""
هذا الملف يحتوي على جميع أسهم البورصة المصرية + صناديق الاستثمار + الفوركس + السلع
"""

from typing import Dict, List, Optional

# ====================== 1. جميع أسهم البورصة المصرية ======================
EGYPTIAN_STOCKS = {
    # ========== قطاع البنوك ==========
    "البنك التجاري الدولي (CIB)": "COMI.CA",
    "بنك مصر": "BMEL.CA",
    "البنك الأهلي المصري": "NBE.CA",
    "بنك الإسكندرية": "ALEX.CA",
    "بنك قطر الوطني الأهلي": "QNBE.CA",
    "البنك العربي الأفريقي الدولي": "AAIB.CA",
    "بنك التعمير والإسكان": "HDBK.CA",
    "بنك القاهرة": "BANQ.CA",
    "بنك كريدي أجريكول مصر": "CIEB.CA",
    "بنك فيصل الإسلامي المصري": "FAIT.CA",
    "المصرف المتحد": "UBE.CA",
    "بنك الاستثمار العربي": "AIBC.CA",
    "البنك المصري لتنمية الصادرات": "EBE.CA",
    "بنك التنمية الصناعية": "IDB.CA",
    "البنك العقاري المصري": "MHBK.CA",
    
    # ========== قطاع العقارات والإنشاءات ==========
    "طلعت مصطفى القابضة": "TMGH.CA",
    "بالم هيلز للتعمير": "PHDC.CA",
    "مدينة نصر للإسكان": "MNHD.CA",
    "السادس من أكتوبر للتنمية": "OCDI.CA",
    "العربية للاستثمار والتطوير العقاري": "AIND.CA",
    "القاهرة الجديدة للإسكان": "NCAD.CA",
    "الإسكندرية للإنشاءات": "ALEX.CA",
    "مصر الجديدة للإسكان": "HELI.CA",
    "بورسعيد للتنمية": "PSDC.CA",
    "روابي للاستثمار العقاري": "RABI.CA",
    
    # ========== قطاع المواد الغذائية والزراعة ==========
    "الشرقية للدخان (إيسترن كومباني)": "EAST.CA",
    "أبو قير للأسمدة والصناعات الكيماوية": "ABUK.CA",
    "مصر لإنتاج الأسمدة (موبكو)": "MFPC.CA",
    "سكر الحدود": "SUGR.CA",
    "النيل للأغذية (نيلو)": "NILE.CA",
    "المصرية للأغذية (ميفود)": "FOOD.CA",
    "العربية لألبان": "ALBN.CA",
    "المنتجات الغذائية": "EFPC.CA",
    "المتحدة للإنتاج الزراعي": "UPAC.CA",
    
    # ========== قطاع الاتصالات وتكنولوجيا المعلومات ==========
    "المصرية للاتصالات": "ETEL.CA",
    "تليكوم مصر": "ETEL.CA",
    "فوري لتكنولوجيا البنوك": "FWRY.CA",
    "Raya Holding": "RAYA.CA",
    "العالمية للتكنولوجيا": "GTC.CA",
    
    # ========== قطاع الصناعة ==========
    "السويدي إليكتريك": "SWDY.CA",
    "مصر للألومنيوم": "EGAL.CA",
    "الحديد والصلب المصرية": "IRON.CA",
    "الإسكندرية للحديد والصلب": "ALEX.CA",
    "مصر للأسمنت قنا": "MCQE.CA",
    "أسمنت طرة": "TORA.CA",
    "أسمنت حلوان": "HELI.CA",
    "السويس للأسمنت": "SUCE.CA",
    "النصر للكيماويات": "NCCM.CA",
    "الكيماويات الحديثة": "MICH.CA",
    "سيدبك": "SKPC.CA",
    "الإسكندرية للزيوت": "ALEZ.CA",
    
    # ========== قطاع السياحة والفنادق ==========
    "أوراسكوم للإنشاءات": "ORAS.CA",
    "أوراسكوم للفنادق": "ORHD.CA",
    "الشرقية للسياحة": "ESTC.CA",
    "مصر للسياحة": "EFIC.CA",
    
    # ========== قطاع السيارات والنقل ==========
    "جي بي أوتو": "JUFO.CA",
    "النقل والهندسة": "NTHE.CA",
    "القاهرة للنقل": "CCTP.CA",
    
    # ========== قطاع الأدوية ==========
    "المصرية للمستحضرات الطبية": "EGPC.CA",
    "أكتوفيرم": "ACTO.CA",
    "إيبيكو": "EPCO.CA",
    "العربية للأدوية": "ADCI.CA",
    
    # ========== قطاع الطاقة والتعدين والبترول ==========
    "القلعة القابضة": "CCAP.CA",
    "الإسكندرية للبترول": "APC.CA",
    "مصر للطيران القابضة": "EGAL.CA",
    "القاهرة لتكرير البترول": "CORC.CA",
    "الشرقية للبترول": "EPC.CA",
    "طاقة مصر (Egypt Gas)": "EGAS.CA",
    "الإسكندرية للزيوت المعدنية": "AMOC.CA",
    "النصر للتعدين": "NMDC.CA",
    
    # ========== قطاع الخدمات المالية وصناديق الاستثمار ==========
    "البنك الهولندي": "HRHO.CA",
    "بلتون المالية": "BTFH.CA",
    "هيرميس القابضة": "HRHO.CA",
    "بايونيرز القابضة": "PIOH.CA",
    "برايم القابضة": "PRMH.CA",
    "بلتون أويل آند غاز": "BTFH.CA",
    
    # ========== قطاع المنسوجات ==========
    "النسيج المصري": "EGTX.CA",
    "الملابس الجاهزة": "RGMK.CA",
    
    # ========== صناديق المؤشرات المتداولة (ETFs) ==========
    "صندوق المؤشر الأول للبورصة المصرية": "XHD.CA",
    "صندوق إي إم آي إيه للأسهم القيادية": "EMIA.CA",
}

# ====================== 2. السلع والمعادن ======================
COMMODITIES = {
    "الذهب (أونصة)": "GC=F",
    "الفضة (أونصة)": "SI=F",
    "البلاتين (أونصة)": "PL=F",
    "النحاس": "HG=F",
    "خام برنت": "BZ=F",
    "خام غرب تكساس (WTI)": "CL=F",
    "الغاز الطبيعي": "NG=F",
    "الذرة": "C=F",
    "فول الصويا": "ZS=F",
    "القطن": "CT=F",
    "السكر": "SB=F",
}

# ====================== 3. أسواق العملات (فوركس) ======================
FOREX = {
    "الدولار / الجنيه المصري": "EGP=X",
    "اليورو / الجنيه المصري": "EURUSD=X",
    "الجنيه الإسترليني / الجنيه المصري": "GBPUSD=X",
    "الريال السعودي / الجنيه المصري": "SAR=X",
    "اليورو مقابل الدولار": "EURUSD=X",
    "الجنيه الإسترليني مقابل الدولار": "GBPUSD=X",
}

# ====================== دمج كل شيء للبحث الشامل ======================
ALL_INSTRUMENTS = {}

# دمج الأسهم
for name, ticker in EGYPTIAN_STOCKS.items():
    ALL_INSTRUMENTS[f"🇪🇬 {name}"] = {"ticker": ticker, "type": "stock"}

# دمج السلع
for name, ticker in COMMODITIES.items():
    ALL_INSTRUMENTS[f"🏆 {name}"] = {"ticker": ticker, "type": "commodity"}

# دمج الفوركس
for name, ticker in FOREX.items():
    ALL_INSTRUMENTS[f"💱 {name}"] = {"ticker": ticker, "type": "forex"}

# ====================== تقسيم الأسهم حسب القطاعات ======================
SECTORS = {
    "البنوك": ["البنك التجاري الدولي (CIB)", "بنك مصر", "البنك الأهلي المصري", "بنك الإسكندرية"],
    "العقارات": ["طلعت مصطفى القابضة", "بالم هيلز للتعمير", "مدينة نصر للإسكان"],
    "المواد الغذائية": ["الشرقية للدخان (إيسترن كومباني)", "أبو قير للأسمدة", "مصر لإنتاج الأسمدة (موبكو)"],
    "الاتصالات": ["المصرية للاتصالات", "تليكوم مصر", "فوري لتكنولوجيا البنوك"],
    "الصناعة": ["السويدي إليكتريك", "مصر للألومنيوم", "الحديد والصلب المصرية"],
    "السياحة": ["أوراسكوم للإنشاءات", "أوراسكوم للفنادق"],
    "السيارات": ["جي بي أوتو"],
    "الأدوية": ["المصرية للمستحضرات الطبية", "أكتوفيرم"],
    "الخدمات المالية": ["البنك الهولندي", "بلتون المالية"],
    "الطاقة والبترول": ["القلعة القابضة", "الإسكندرية للبترول", "طاقة مصر (Egypt Gas)"],
    "التعدين": ["مصر للألومنيوم", "سيدبك", "النصر للتعدين"],
}

# ====================== معلومات البورصة المصرية ======================
EGX_INFO = {
    "name": "البورصة المصرية",
    "code": "EGX",
    "suffix": ".CA",
    "timezone": "Africa/Cairo",
    "currency": "EGP",
    "market_hours": "10:00 - 14:30",
    "prayer_break": "12:30 - 13:30",
    "index": "^EGX30",
    "index_name": "EGX30",
    "total_stocks": len(EGYPTIAN_STOCKS),
    "sectors_count": len(SECTORS),
    "established": "1903",
}

# ====================== الدوال المطلوبة ======================
def get_all_egyptian_stocks() -> Dict:
    """إرجاع جميع أسهم البورصة المصرية"""
    return EGYPTIAN_STOCKS

def get_stock_ticker(stock_name: str) -> Optional[str]:
    """إرجاع رمز السهم من الاسم"""
    return EGYPTIAN_STOCKS.get(stock_name)

def get_stocks_by_sector(sector: str) -> Dict:
    """إرجاع أسهم قطاع معين"""
    if sector in SECTORS:
        return {name: EGYPTIAN_STOCKS[name] for name in SECTORS[sector] if name in EGYPTIAN_STOCKS}
    return {}

def get_all_sectors() -> List[str]:
    """إرجاع قائمة بجميع القطاعات"""
    return list(SECTORS.keys())

def get_market_statistics() -> Dict:
    """إحصائيات السوق كاملة"""
    stats = {
        "total_stocks": len(EGYPTIAN_STOCKS),
        "sectors": len(SECTORS),
        "trading_hours": EGX_INFO["market_hours"],
        "currency": EGX_INFO["currency"],
        "index": EGX_INFO["index"],
        "commodities": len(COMMODITIES),
        "forex_pairs": len(FOREX)
    }
    
    # إحصائيات القطاعات
    sector_stats = {}
    for sector, stocks in SECTORS.items():
        sector_stats[sector] = len(stocks)
    stats["sectors_stats"] = sector_stats
    
    return stats

def search_stock(keyword: str) -> Dict:
    """البحث في الأسهم والسلع والفوركس"""
    results = {}
    keyword_lower = keyword.lower()
    
    # البحث في الأسهم
    for stock_name, stock_ticker in EGYPTIAN_STOCKS.items():
        if (keyword_lower in stock_name.lower() or 
            keyword_lower in stock_ticker.lower() or
            keyword_lower in stock_ticker.replace('.CA', '').lower()):
            results[stock_name] = {
                'ticker': stock_ticker,
                'name': stock_name,
                'type': 'stock'
            }
    
    # البحث في السلع
    for commodity_name, commodity_ticker in COMMODITIES.items():
        if keyword_lower in commodity_name.lower() or keyword_lower in commodity_ticker.lower():
            results[commodity_name] = {
                'ticker': commodity_ticker,
                'name': commodity_name,
                'type': 'commodity'
            }
    
    # البحث في الفوركس
    for forex_name, forex_ticker in FOREX.items():
        if keyword_lower in forex_name.lower() or keyword_lower in forex_ticker.lower():
            results[forex_name] = {
                'ticker': forex_ticker,
                'name': forex_name,
                'type': 'forex'
            }
    
    return results

def get_market_info(market: str = None) -> Dict:
    """إرجاع معلومات البورصة المصرية"""
    if market is None:
        return EGX_INFO
    return EGX_INFO

def get_market_info_by_ticker(ticker: str) -> Optional[Dict]:
    """جلب معلومات السوق بناءً على الرمز"""
    return EGX_INFO

def get_all_instruments() -> Dict:
    """إرجاع جميع الأدوات (أسهم + سلع + فوركس)"""
    return ALL_INSTRUMENTS

# ====================== اختبار سريع ======================
if __name__ == "__main__":
    print(f"✅ تم تحميل {len(EGYPTIAN_STOCKS)} سهماً من البورصة المصرية")
    print(f"🏆 تم تحميل {len(COMMODITIES)} سلعة")
    print(f"💱 تم تحميل {len(FOREX)} زوج عملات")
    print(f"📊 عدد القطاعات: {len(SECTORS)}")
    print("\n📈 القطاعات المتاحة:")
    for sector in SECTORS.keys():
        print(f"   - {sector}: {len(SECTORS[sector])} شركة")
