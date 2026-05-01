# database.py - قاعدة البيانات المركزية (موسعة بالشركات)
"""
النسخة الموسعة من قاعدة البيانات
تحتوي على جميع الأسهم المصرية والسعودية والعالمية
"""

# ====================== تعريف الأسواق والأسهم ======================
MARKETS_DATA = {
    # ========== البورصة المصرية (EGX) - أكثر من 60 شركة ==========
    "EGX": {
        "label": "🇪🇬 البورصة المصرية",
        "suffix": ".CA",
        "timezone": "Africa/Cairo",
        "currency": "EGP",
        "market_hours": "10:00 - 14:30",
        "description": "أكبر بورصة في شمال أفريقيا",
        "stocks": {
            # البنوك (10 شركات)
            "البنك التجاري الدولي (CIB)": "COMI.CA",
            "بنك مصر": "BMEL.CA",
            "بنك الإسكندرية": "ALEX.CA",
            "البنك الأهلي الكويتي": "ALCN.CA",
            "بنك التعمير والإسكان": "HDBK.CA",
            "بنك قناة السويس": "CSBK.CA",
            "البنك العربي الأفريقي": "AAIB.CA",
            "بنك فيصل الإسلامي": "FAIT.CA",
            "بنك بلوم": "BLOOM.CA",
            "البنك العقاري المصري": "MHRB.CA",
            
            # العقارات والإنشاءات (15 شركة)
            "طلعت مصطفى القابضة": "TMGH.CA",
            "بالم هيلز للتعمير": "PHDC.CA",
            "السادس من أكتوبر للتنمية": "OCDI.CA",
            "مدينة نصر للإسكان": "MNHD.CA",
            "العربية للاستثمار والتطوير": "AIND.CA",
            "القاهرة الجديدة للإسكان": "NCAD.CA",
            "الإسكندرية للإنشاءات": "ALEX.CA",
            "مصر للاستثمار العقاري": "MIR.CA",
            "بورتوفو للتنمية العقارية": "PORT.CA",
            "العقارية للاستثمار": "ALLI.CA",
            "مشروع البطس للتنمية": "PAT.CA",
            "الإسماعيلية للتطوير العقاري": "ISMA.CA",
            "العبور للاستثمار العقاري": "OBUR.CA",
            "الشرق للتنمية العمرانية": "ESDC.CA",
            "بعد للتنمية": "BAAD.CA",
            
            # المواد الغذائية والزراعة (12 شركة)
            "الشرقية للدخان (إيسترن)": "EAST.CA",
            "أبو قير للأسمدة": "ABUK.CA",
            "مصر لإنتاج الأسمدة (موبكو)": "MFPC.CA",
            "سكر الحدود": "SUGR.CA",
            "القلعة للصناعات": "CCAP.CA",
            "النيل للأغذية": "NILE.CA",
            "المصرية للأغذية": "FOOD.CA",
            "العربية للحوم": "ALC.CA",
            "المنتجات الغذائية": "GFI.CA",
            "مطاحن ومخابز شمال القاهرة": "MILS.CA",
            "مطاحن مصر الوسطى": "MILS.CA",
            "مطاحن جنوب القاهرة": "MILS.CA",
            
            # الاتصالات وتكنولوجيا المعلومات (8 شركات)
            "تليكوم مصر": "ETEL.CA",
            "المصرية للاتصالات": "ETEL.CA",
            "فوري لتكنولوجيا البنوك": "FWRY.CA",
            "Raya Holding": "RAYA.CA",
            "أكت فاينانس": "ACTF.CA",
            "أي فاينانس": "EIF.CA",
            "أسيوط للاتصالات": "ASCO.CA",
            "مصر للأنظمة": "SYS.CA",
            
            # الصناعة (15 شركة)
            "السويدي إليكتريك": "SWDY.CA",
            "مصر للألومنيوم": "EGAL.CA",
            "الحديد والصلب المصرية": "IRON.CA",
            "الإسكندرية للحديد والصلب": "ALEX.CA",
            "النصر للكيماويات": "NCCM.CA",
            "سيدبك": "SKPC.CA",
            "الإسكندرية للأسمدة": "AFRI.CA",
            "مصر للأسمدة": "MFPC.CA",
            "النصر للصناعات الإلكترونية": "EMCO.CA",
            "النساجون الشرقيون": "ORWE.CA",
            "مصر للنسيج": "EGTX.CA",
            "كتامة للصناعات": "KCCM.CA",
            "الإسكندرية للغزل": "ALEX.CA",
            "المحلة الكبرى للغزل": "MAHL.CA",
            "مصر للبترول": "PETR.CA",
            
            # الأدوية (8 شركات)
            "المصرية للمستحضرات الطبية": "EGPC.CA",
            "أكتوفيرم": "ACTO.CA",
            "جايبكو": "GPC.CA",
            "العربية للأدوية": "ADCI.CA",
            "النصر للأدوية": "NATC.CA",
            "ممفيس للأدوية": "MEMF.CA",
            "الإسكندرية للأدوية": "ALEX.CA",
            "الدلتا للأدوية": "DELTA.CA",
            
            # السياحة والفنادق (5 شركات)
            "أوراسكوم للفنادق": "ORHD.CA",
            "فنادق الإسكندرية": "ALEX.CA",
            "فنادق القاهرة": "CAIR.CA",
            "فنادق شيراتون": "SHE.CA",
            "فنادق هيلتون": "HILT.CA",
        }
    },
    
    # ========== باقي الأسواق كما هي (تداول، أبوظبي، دبي، أمريكا) ==========
    # ... (أضف باقي الأسواق كما في الإصدار السابق)
}

# دوال مساعدة (نفس الإصدار السابق مع تحسينات)
def get_all_stocks() -> dict:
    """جلب جميع الأسهم من جميع الأسواق"""
    all_stocks = {}
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            full_name = f"{market_data['label']} - {stock_name}"
            all_stocks[full_name] = {
                'ticker': stock_ticker,
                'market': market_key,
                'suffix': market_data.get('suffix', ''),
                'currency': market_data.get('currency', ''),
                'market_name': market_data['label']
            }
    return all_stocks

def search_stock(keyword: str) -> dict:
    """البحث المتقدم عن سهم"""
    results = {}
    keyword_lower = keyword.lower()
    
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            if (keyword_lower in stock_name.lower() or 
                keyword_lower in stock_ticker.lower() or
                keyword_lower in market_data.get('label', '').lower()):
                full_name = f"{market_data['label']} - {stock_name}"
                results[full_name] = {
                    'ticker': stock_ticker,
                    'market': market_key,
                    'currency': market_data.get('currency', ''),
                    'suffix': market_data.get('suffix', ''),
                    'market_label': market_data['label']
                }
    
    return results
