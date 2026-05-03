# database.py - قاعدة البيانات المركزية لجميع الأسهم
"""
هذا الملف يحتوي على جميع بيانات الأسهم والأسواق
يمكنك إضافة آلاف الأسهم هنا دون التأثير على سرعة التطبيق
"""

# ====================== تعريف الأسواق والأسهم ======================
MARKETS_DATA = {
    # ========== البورصة المصرية (EGX) ==========
    "EGX": {
        "label": "🇪🇬 البورصة المصرية",
        "suffix": ".CA",
        "timezone": "Africa/Cairo",
        "currency": "EGP",
        "market_hours": "10:00 - 14:30",
        "prayer_break": "12:30 - 13:30",
        "stocks": {
            # البنوك
            "البنك التجاري الدولي (CIB)": "COMI.CA",
            "بنك مصر": "BMEL.CA",
            "البنك الأهلي المصري": "ALEX.CA",
            "بنك الإسكندرية": "ALEX.CA",
            "بنك التعمير والإسكان": "HDBK.CA",
            "بنك قناة السويس": "CSBK.CA",
            
            # العقارات والإنشاءات
            "طلعت مصطفى القابضة": "TMGH.CA",
            "بالم هيلز للتعمير": "PHDC.CA",
            "السادس من أكتوبر للتنمية": "OCDI.CA",
            "مدينة نصر للإسكان": "MNHD.CA",
            
            # المواد الغذائية والزراعة
            "الشرقية للدخان (إيسترن)": "EAST.CA",
            "أبو قير للأسمدة": "ABUK.CA",
            "مصر لإنتاج الأسمدة (موبكو)": "MFPC.CA",
            "سكر الحدود": "SUGR.CA",
            
            # الاتصالات وتكنولوجيا المعلومات
            "تليكوم مصر": "ETEL.CA",
            "فوري لتكنولوجيا البنوك": "FWRY.CA",
            "Raya Holding": "RAYA.CA",
            
            # الصناعة
            "السويدي إليكتريك": "SWDY.CA",
            "مصر للألومنيوم": "EGAL.CA",
            "سيدبك": "SKPC.CA",
            
            # السياحة والخدمات
            "أوراسكوم للإنشاءات": "ORAS.CA",
            "أوراسكوم للفنادق": "ORHD.CA",
            
            # السيارات والنقل
            "جي بي أوتو": "JUFO.CA",
            
            # الخدمات المالية
            "البنك الهولندي": "HRHO.CA",
            "بلتون المالية": "BTFH.CA",
        }
    },
    
    # ========== تداول السعودية (Tadawul) ==========
    "TADAWUL": {
        "label": "🇸🇦 تداول السعودية",
        "suffix": ".SR",
        "timezone": "Asia/Riyadh",
        "currency": "SAR",
        "market_hours": "10:00 - 15:00",
        "stocks": {
            # الطاقة
            "أرامكو السعودية": "2222.SR",
            
            # البنوك
            "مصرف الراجحي": "1120.SR",
            "البنك الأهلي السعودي": "1180.SR",
            "بنك الرياض": "1010.SR",
            "بنك الجزيرة": "1020.SR",
            "الإنماء": "1150.SR",
            "بنك ساب": "1060.SR",
            
            # البتروكيماويات
            "سابك": "2010.SR",
            "التصنيع الوطنية": "2060.SR",
            
            # الاتصالات
            "مجموعة STC": "7010.SR",
            "موبايلي": "7030.SR",
            "زين السعودية": "7020.SR",
            
            # التجزئة
            "أسواق عبد الله العثيم": "4001.SR",
            
            # العقار
            "دار الأركان": "4300.SR",
            
            # المعادن
            "معادن": "1211.SR",
        }
    },
    
    # ========== سوق أبوظبي (ADX) ==========
    "ADX": {
        "label": "🇦🇪 سوق أبوظبي",
        "suffix": ".AD",
        "timezone": "Asia/Dubai",
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "stocks": {
            "بنك أبوظبي الأول": "FAB.AD",
            "اتصالات": "EAND.AD",
            "أبوظبي التجاري": "ADCB.AD",
            "أبوظبي الوطني للطاقة": "TAQA.AD",
        }
    },
    
    # ========== سوق دبي (DFM) ==========
    "DFM": {
        "label": "🇦🇪 سوق دبي",
        "suffix": ".DU",
        "timezone": "Asia/Dubai",
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "stocks": {
            "إعمار العقارية": "EMAAR.DU",
            "بنك دبي الإسلامي": "DIB.DU",
            "سوق دبي المالي": "DFM.DU",
        }
    },
    
    # ========== الأسهم الأمريكية ==========
    "US": {
        "label": "🇺🇸 الأسهم الأمريكية",
        "suffix": "",
        "timezone": "America/New_York",
        "currency": "USD",
        "market_hours": "09:30 - 16:00",
        "stocks": {
            "Apple Inc.": "AAPL",
            "Microsoft Corp.": "MSFT",
            "Alphabet (Google)": "GOOGL",
            "Amazon.com": "AMZN",
            "NVIDIA Corp.": "NVDA",
            "Meta Platforms": "META",
            "Tesla Inc.": "TSLA",
            "Netflix Inc.": "NFLX",
        }
    }
}

# ====================== دوال مساعدة ======================
def get_all_stocks() -> dict:
    """جلب جميع الأسهم من جميع الأسواق"""
    all_stocks = {}
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            full_name = f"{market_data['label']} - {stock_name}"
            all_stocks[full_name] = {
                'ticker': stock_ticker,
                'market': market_key,
                'currency': market_data['currency']
            }
    return all_stocks

def get_market_statistics() -> dict:
    """إحصائيات عن عدد الأسهم"""
    stats = {}
    for market_key, market_data in MARKETS_DATA.items():
        stats[market_key] = {
            'name': market_data['label'],
            'count': len(market_data['stocks']),
            'currency': market_data['currency']
        }
    stats['TOTAL'] = sum(s['count'] for s in stats.values())
    return stats

def search_stock(keyword: str) -> dict:
    """البحث عن سهم"""
    results = {}
    keyword_lower = keyword.lower()
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            if keyword_lower in stock_name.lower() or keyword_lower in stock_ticker.lower():
                full_name = f"{market_data['label']} - {stock_name}"
                results[full_name] = {
                    'ticker': stock_ticker,
                    'market': market_key
                }
    return results
