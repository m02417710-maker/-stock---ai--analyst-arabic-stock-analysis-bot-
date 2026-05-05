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
            "البنك الزراعي المصري": "ABZU.CA",
            "بنك الإسكندرية": "ALEX.CA",
            "بنك التعمير والإسكان": "HDBK.CA",
            "بنك قناة السويس": "CSBK.CA",
            
            # العقارات والإنشاءات
            "طلعت مصطفى القابضة": "TMGH.CA",
            "بالم هيلز للتعمير": "PHDC.CA",
            "السادس من أكتوبر للتنمية": "OCDI.CA",
            "مدينة نصر للإسكان": "MNHD.CA",
            "العربية للاستثمار والتطوير": "AIND.CA",
            "القاهرة الجديدة للإسكان": "NCAD.CA",
            "الإسكندرية للإنشاءات": "ALEX.CA",
            
            # المواد الغذائية والزراعة
            "الشرقية للدخان (إيسترن)": "EAST.CA",
            "أبو قير للأسمدة": "ABUK.CA",
            "مصر لإنتاج الأسمدة (موبكو)": "MFPC.CA",
            "سكر الحدود": "SUGR.CA",
            "القلعة للصناعات": "CCAP.CA",
            "النيل للأغذية": "NILE.CA",
            "المصرية للأغذية": "FOOD.CA",
            
            # الاتصالات وتكنولوجيا المعلومات
            "تليكوم مصر": "ETEL.CA",
            "المصرية للاتصالات": "ETEL.CA",
            "فوري لتكنولوجيا البنوك": "FWRY.CA",
            "Raya Holding": "RAYA.CA",
            
            # الصناعة
            "السويدي إليكتريك": "SWDY.CA",
            "مصر للألومنيوم": "EGAL.CA",
            "الحديد والصلب المصرية": "IRON.CA",
            "الإسكندرية للحديد والصلب": "ALEX.CA",
            "النصر للكيماويات": "NCCM.CA",
            "سيدبك": "SKPC.CA",
            
            # السياحة والخدمات
            "أوراسكوم للإنشاءات": "ORAS.CA",
            "أوراسكوم للفنادق": "ORHD.CA",
            "الشرقية للسياحة": "ESTC.CA",
            
            # السيارات والنقل
            "جي بي أوتو": "JUFO.CA",
            "النقل والهندسة": "NTHE.CA",
            
            # الأدوية
            "المصرية للمستحضرات الطبية": "EGPC.CA",
            "أكتوفيرم": "ACTO.CA",
            
            # الورق والطباعة
            "الورق والصناعات": "WPPC.CA",
            
            # الخدمات المالية
            "البنك الهولندي": "HRHO.CA",
            "بلتون المالية": "BTFH.CA",
            "هيرميس القابضة": "HRHO.CA",
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
            "بنك البلاد": "1140.SR",
            "الإنماء": "1150.SR",
            "بنك ساب": "1060.SR",
            "الاستثمار": "1030.SR",
            
            # البتروكيماويات
            "سابك": "2010.SR",
            "التصنيع الوطنية": "2060.SR",
            "الكيميائية": "2001.SR",
            "المتقدمة": "2120.SR",
            
            # الاتصالات
            "مجموعة STC": "7010.SR",
            "موبايلي": "7030.SR",
            "زين السعودية": "7020.SR",
            
            # التجزئة والاستهلاك
            "أسواق عبد الله العثيم": "4001.SR",
            "بن داود": "4007.SR",
            "المواساة للخدمات": "4002.SR",
            
            # العقار
            "دار الأركان": "4300.SR",
            "جبلة": "4320.SR",
            
            # التأمين
            "التعاونية": "8010.SR",
            "الراجحي للتأمين": "8230.SR",
            
            # النقل والخدمات اللوجستية
            "البحري": "4030.SR",
            
            # الأدوية
            "الدوائية": "2070.SR",
            
            # المعادن والصناعة
            "معادن": "1211.SR",
            "أسمنت العربية": "3030.SR",
            "أسمنت ينبع": "3060.SR",
        }
    },
    
    # ========== سوق أبوظبي للأوراق المالية (ADX) ==========
    "ADX": {
        "label": "🇦🇪 سوق أبوظبي للأوراق المالية",
        "suffix": ".AD",
        "timezone": "Asia/Dubai",
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "stocks": {
            "بنك أبوظبي الأول": "FAB.AD",
            "الاتحاد للاتصالات (اتصالات)": "EAND.AD",
            "أبوظبي التجاري": "ADCB.AD",
            "أبوظبي الوطني للطاقة": "TAQA.AD",
            "القابضة (ADQ)": "ADQ.AD",
            "ملتيبلاي": "MULTIPLY.AD",
        }
    },
    
    # ========== سوق دبي المالي (DFM) ==========
    "DFM": {
        "label": "🇦🇪 سوق دبي المالي",
        "suffix": ".DU",
        "timezone": "Asia/Dubai",
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "stocks": {
            "إعمار العقارية": "EMAAR.DU",
            "بنك دبي الإسلامي": "DIB.DU",
            "الاتحاد العقارية": "UNION.DU",
            "سوق دبي المالي": "DFM.DU",
            "طيران الإمارات": "EMIRATES.DU",
        }
    },
    
    # ========== الأسهم الأمريكية (NASDAQ & NYSE) ==========
    "US": {
        "label": "🇺🇸 الأسهم الأمريكية",
        "suffix": "",
        "timezone": "America/New_York",
        "currency": "USD",
        "market_hours": "09:30 - 16:00",
        "stocks": {
            # التكنولوجيا
            "Apple Inc.": "AAPL",
            "Microsoft Corp.": "MSFT",
            "Alphabet (Google)": "GOOGL",
            "Amazon.com": "AMZN",
            "NVIDIA Corp.": "NVDA",
            "Meta Platforms (Facebook)": "META",
            "Netflix Inc.": "NFLX",
            "Tesla Inc.": "TSLA",
            "Intel Corp.": "INTC",
            "Advanced Micro Devices": "AMD",
            "Cisco Systems": "CSCO",
            "Oracle Corp.": "ORCL",
            "Salesforce Inc.": "CRM",
            "Adobe Inc.": "ADBE",
            "PayPal Holdings": "PYPL",
            
            # البنوك والمالية
            "JPMorgan Chase": "JPM",
            "Bank of America": "BAC",
            "Wells Fargo": "WFC",
            "Goldman Sachs": "GS",
            "Morgan Stanley": "MS",
            "Visa Inc.": "V",
            "Mastercard Inc.": "MA",
            
            # الرعاية الصحية
            "Johnson & Johnson": "JNJ",
            "Pfizer Inc.": "PFE",
            "Moderna Inc.": "MRNA",
            "UnitedHealth Group": "UNH",
            
            # الاستهلاك
            "The Walt Disney Company": "DIS",
            "McDonald's Corp.": "MCD",
            "Coca-Cola Co.": "KO",
            "PepsiCo Inc.": "PEP",
            "Nike Inc.": "NKE",
            "Starbucks Corp.": "SBUX",
            
            # الصناعة والطاقة
            "Boeing Co.": "BA",
            "Caterpillar Inc.": "CAT",
            "Exxon Mobil": "XOM",
            "Chevron Corp.": "CVX",
        }
    }
}

# ====================== دوال مساعدة متقدمة ======================
def get_all_stocks() -> dict:
    """جلب جميع الأسهم من جميع الأسواق"""
    all_stocks = {}
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            # إضافة اسم السوق للمساعدة في التصنيف
            full_name = f"{market_data['label']} - {stock_name}"
            all_stocks[full_name] = {
                'ticker': stock_ticker,
                'market': market_key,
                'suffix': market_data['suffix'],
                'currency': market_data['currency']
            }
    return all_stocks

def get_stocks_by_market(market_key: str) -> dict:
    """جلب أسهم سوق معين"""
    if market_key in MARKETS_DATA:
        stocks = {}
        for name, ticker in MARKETS_DATA[market_key]['stocks'].items():
            stocks[f"{MARKETS_DATA[market_key]['label']} - {name}"] = ticker
        return stocks
    return {}

def search_stock(keyword: str) -> dict:
    """البحث عن سهم باستخدام كلمة مفتاحية"""
    results = {}
    keyword_lower = keyword.lower()
    
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            if keyword_lower in stock_name.lower() or keyword_lower in stock_ticker.lower():
                full_name = f"{market_data['label']} - {stock_name}"
                results[full_name] = {
                    'ticker': stock_ticker,
                    'market': market_key,
                    'currency': market_data['currency']
                }
    return results

def get_market_info(market_key: str) -> dict:
    """جلب معلومات عن سوق معين"""
    if market_key in MARKETS_DATA:
        return MARKETS_DATA[market_key]
    return None

def get_market_statistics() -> dict:
    """إحصائيات عن عدد الأسهم في كل سوق"""
    stats = {}
    for market_key, market_data in MARKETS_DATA.items():
        stats[market_key] = {
            'name': market_data['label'],
            'count': len(market_data['stocks']),
            'currency': market_data['currency']
        }
    stats['TOTAL'] = sum(s['count'] for s in stats.values())
    return stats

# اختبار عند التحميل
if __name__ == "__main__":
    print(f"📊 تم تحميل {get_market_statistics()['TOTAL']} سهماً")
    for market, stats in get_market_statistics().items():
        if market != 'TOTAL':
            print(f"   {stats['name']}: {stats['count']} سهماً")
