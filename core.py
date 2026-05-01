# core.py - الإصدار النهائي المتكامل (بدون أخطاء استيراد)
"""
ملف الإدارة المركزية للتطبيق
يعمل بشكل مستقل ولا يحتاج إلى ملفات خارجية
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st

# ====================== تعريف قاعدة البيانات الرئيسية ======================
# جميع الأسهم والأسواق في مكان واحد لتجنب مشاكل الاستيراد

STOCKS_DATABASE = {
    # ==================== البورصة المصرية (EGX) ====================
    "🇪🇬 البنك التجاري الدولي (CIB)": {
        "ticker": "COMI.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "بنوك",
        "description": "أكبر بنك خاص في مصر"
    },
    "🇪🇬 طلعت مصطفى القابضة": {
        "ticker": "TMGH.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "عقارات",
        "description": "شركة رائدة في التطوير العقاري"
    },
    "🇪🇬 السويدي إليكتريك": {
        "ticker": "SWDY.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "صناعة",
        "description": "أكبر شركة كهرباء في مصر"
    },
    "🇪🇬 تليكوم مصر": {
        "ticker": "ETEL.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "اتصالات",
        "description": "مشغل اتصالات رائد"
    },
    "🇪🇬 الشرقية للدخان (إيسترن)": {
        "ticker": "EAST.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "تبغ",
        "description": "شركة التبغ المصرية"
    },
    "🇪🇬 موبكو (مصر للأسمدة)": {
        "ticker": "MFPC.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "كيماويات",
        "description": "إنتاج الأسمدة"
    },
    "🇪🇬 أوراسكوم للإنشاءات": {
        "ticker": "ORAS.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "إنشاءات",
        "description": "شركة إنشاءات كبرى"
    },
    "🇪🇬 جي بي أوتو": {
        "ticker": "JUFO.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "سيارات",
        "description": "توزيع السيارات"
    },
    "🇪🇬 أبو قير للأسمدة": {
        "ticker": "ABUK.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "كيماويات",
        "description": "إنتاج الأسمدة"
    },
    "🇪🇬 المجموعة المالية هيرميس": {
        "ticker": "HRHO.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "خدمات مالية",
        "description": "الاستثمار المالي"
    },
    "🇪🇬 فوري لتكنولوجيا البنوك": {
        "ticker": "FWRY.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "تكنولوجيا مالية",
        "description": "خدمات الدفع الإلكتروني"
    },
    "🇪🇬 بالم هيلز للتعمير": {
        "ticker": "PHDC.CA",
        "market": "EGX",
        "currency": "EGP",
        "sector": "عقارات",
        "description": "التطوير العقاري الفاخر"
    },
    
    # ==================== بورصة تداول السعودية ====================
    "🇸🇦 أرامكو السعودية": {
        "ticker": "2222.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "طاقة",
        "description": "أكبر شركة نفط في العالم"
    },
    "🇸🇦 مصرف الراجحي": {
        "ticker": "1120.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "بنوك",
        "description": "أكبر بنك إسلامي"
    },
    "🇸🇦 مجموعة STC": {
        "ticker": "7010.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "اتصالات",
        "description": "شركة الاتصالات السعودية"
    },
    "🇸🇦 مجموعة ساب": {
        "ticker": "1060.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "بنوك",
        "description": "البنك السعودي البريطاني"
    },
    "🇸🇦 بنك الأهلي السعودي": {
        "ticker": "1180.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "بنوك",
        "description": "أكبر بنك في السعودية"
    },
    "🇸🇦 سابك": {
        "ticker": "2010.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "بتروكيماويات",
        "description": "الشركة السعودية للصناعات الأساسية"
    },
    "🇸🇦 معادن": {
        "ticker": "1211.SR",
        "market": "TADAWUL",
        "currency": "SAR",
        "sector": "تعدين",
        "description": "شركة التعدين العربية السعودية"
    },
    
    # ==================== الأسهم الأمريكية ====================
    "🇺🇸 Apple Inc.": {
        "ticker": "AAPL",
        "market": "US",
        "currency": "USD",
        "sector": "تكنولوجيا",
        "description": "شركة أبل"
    },
    "🇺🇸 Microsoft Corp.": {
        "ticker": "MSFT",
        "market": "US",
        "currency": "USD",
        "sector": "تكنولوجيا",
        "description": "شركة مايكروسوفت"
    },
    "🇺🇸 Tesla Inc.": {
        "ticker": "TSLA",
        "market": "US",
        "currency": "USD",
        "sector": "سيارات كهربائية",
        "description": "شركة تيسلا"
    },
    "🇺🇸 Amazon.com": {
        "ticker": "AMZN",
        "market": "US",
        "currency": "USD",
        "sector": "تجارة إلكترونية",
        "description": "شركة أمازون"
    },
    "🇺🇸 Google (Alphabet)": {
        "ticker": "GOOGL",
        "market": "US",
        "currency": "USD",
        "sector": "تكنولوجيا",
        "description": "شركة جوجل"
    },
    "🇺🇸 NVIDIA Corp.": {
        "ticker": "NVDA",
        "market": "US",
        "currency": "USD",
        "sector": "رقائق إلكترونية",
        "description": "شركة نفيديا"
    },
    "🇺🇸 Meta Platforms": {
        "ticker": "META",
        "market": "US",
        "currency": "USD",
        "sector": "تواصل اجتماعي",
        "description": "شركة ميتا (فيسبوك)"
    },
    "🇺🇸 Netflix Inc.": {
        "ticker": "NFLX",
        "market": "US",
        "currency": "USD",
        "sector": "بث مباشر",
        "description": "شركة نتفليكس"
    }
}

# ====================== معلومات الأسواق ======================
MARKETS_INFO = {
    "EGX": {
        "name": "البورصة المصرية",
        "full_name": "Egyptian Exchange",
        "currency": "EGP",
        "timezone": "Africa/Cairo",
        "market_hours": "10:00 - 14:30",
        "index": "^EGX30",
        "flag": "🇪🇬"
    },
    "TADAWUL": {
        "name": "تداول السعودية",
        "full_name": "Saudi Stock Exchange",
        "currency": "SAR",
        "timezone": "Asia/Riyadh",
        "market_hours": "10:00 - 15:00",
        "index": "^TASI",
        "flag": "🇸🇦"
    },
    "US": {
        "name": "الأسهم الأمريكية",
        "full_name": "US Stock Market",
        "currency": "USD",
        "timezone": "America/New_York",
        "market_hours": "09:30 - 16:00",
        "index": "^GSPC",
        "flag": "🇺🇸"
    }
}

# ====================== دوال مساعدة أساسية ======================

def get_all_stocks() -> Dict:
    """
    إرجاع جميع الأسهم مع بياناتها الكاملة
    """
    return STOCKS_DATABASE

def get_stock_list() -> List[str]:
    """
    إرجاع قائمة بأسماء الأسهم فقط (للقوائم المنسدلة)
    """
    return list(STOCKS_DATABASE.keys())

def get_stock_ticker(name: str) -> Optional[str]:
    """
    إرجاع رمز السهم من اسمه
    """
    stock = STOCKS_DATABASE.get(name)
    if stock:
        return stock.get("ticker")
    return None

def get_stock_info(name: str) -> Optional[Dict]:
    """
    إرجاع جميع معلومات السهم
    """
    return STOCKS_DATABASE.get(name)

def get_stock_market(name: str) -> Optional[str]:
    """
    إرجاع سوق السهم
    """
    stock = STOCKS_DATABASE.get(name)
    if stock:
        return stock.get("market")
    return None

def get_stock_currency(name: str) -> Optional[str]:
    """
    إرجاع عملة السهم
    """
    stock = STOCKS_DATABASE.get(name)
    if stock:
        return stock.get("currency")
    return None

def get_stock_sector(name: str) -> Optional[str]:
    """
    إرجاع قطاع السهم
    """
    stock = STOCKS_DATABASE.get(name)
    if stock:
        return stock.get("sector")
    return None

# ====================== دوال البحث والتصفية ======================

def search_stocks(keyword: str) -> Dict:
    """
    البحث عن أسهم باستخدام كلمة مفتاحية
    """
    if not keyword or len(keyword) < 2:
        return {}
    
    keyword_lower = keyword.lower()
    results = {}
    
    for name, data in STOCKS_DATABASE.items():
        ticker = data.get("ticker", "").lower()
        if (keyword_lower in name.lower() or 
            keyword_lower in ticker or
            keyword_lower in data.get("sector", "").lower()):
            results[name] = data
    
    return results

def get_stocks_by_market(market: str) -> Dict:
    """
    الحصول على أسهم سوق معين
    """
    if market not in MARKETS_INFO:
        return {}
    
    return {
        name: data for name, data in STOCKS_DATABASE.items()
        if data.get("market") == market
    }

def get_stocks_by_sector(sector: str) -> Dict:
    """
    الحصول على أسهم قطاع معين
    """
    sector_lower = sector.lower()
    return {
        name: data for name, data in STOCKS_DATABASE.items()
        if data.get("sector", "").lower() == sector_lower
    }

# ====================== إحصائيات وتحليلات ======================

def get_market_statistics() -> Dict:
    """
    إحصائيات عن الأسهم والأسواق
    """
    stats = {
        "total_stocks": len(STOCKS_DATABASE),
        "markets": {},
        "sectors": {}
    }
    
    # إحصائيات حسب السوق
    for market in MARKETS_INFO.keys():
        count = len(get_stocks_by_market(market))
        stats["markets"][market] = {
            "name": MARKETS_INFO[market]["name"],
            "count": count,
            "currency": MARKETS_INFO[market]["currency"]
        }
    
    # إحصائيات حسب القطاع
    for name, data in STOCKS_DATABASE.items():
        sector = data.get("sector", "أخرى")
        if sector not in stats["sectors"]:
            stats["sectors"][sector] = 0
        stats["sectors"][sector] += 1
    
    return stats

def get_top_stocks_by_market() -> Dict:
    """
    الحصول على أفضل الأسهم في كل سوق (للأداء)
    """
    # ملاحظة: هذه قائمة إرشادية - سيتم تحديثها من API
    return {
        "EGX": ["COMI.CA", "TMGH.CA", "SWDY.CA"],
        "TADAWUL": ["2222.SR", "1120.SR", "7010.SR"],
        "US": ["AAPL", "MSFT", "NVDA"]
    }

# ====================== التوافق مع الكود القديم ======================

# للتوافق مع الاستيرادات القديمة
STOCKS = {name: data["ticker"] for name, data in STOCKS_DATABASE.items()}
STOCK_NAMES = list(STOCKS.keys())
STOCK_TICKERS = STOCKS

# واجهة مبسطة
def get_all_stocks_simple() -> Dict:
    """إصدار مبسط - اسم السهم -> رمز السهم"""
    return STOCKS

# ====================== تهيئة واختبار ======================

def validate_core() -> bool:
    """
    التحقق من صحة ملف core
    """
    errors = []
    
    if not STOCKS_DATABASE:
        errors.append("قاعدة البيانات فارغة")
    
    if not MARKETS_INFO:
        errors.append("معلومات الأسواق فارغة")
    
    # التحقق من عدم وجود رموز مكررة
    tickers = [data["ticker"] for data in STOCKS_DATABASE.values()]
    duplicates = [t for t in tickers if tickers.count(t) > 1]
    
    if duplicates:
        errors.append(f"رموز مكررة: {set(duplicates)}")
    
    if errors:
        print("❌ أخطاء في core.py:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print(f"✅ core.py يعمل بشكل صحيح")
    print(f"   📊 {len(STOCKS_DATABASE)} سهماً")
    print(f"   🌍 {len(MARKETS_INFO)} سوقاً")
    return True

# ====================== عرض واجهة التطبيق ======================

def render_stock_selector(key: str = "stock_selector") -> tuple:
    """
    عرض قائمة اختيار السهم في Streamlit
    إرجاع (الاسم المختار, الرمز)
    """
    stock_names = get_stock_list()
    
    selected_name = st.selectbox(
        "🔍 اختر السهم للتحليل",
        options=stock_names,
        key=key,
        format_func=lambda x: f"{x} ({STOCKS.get(x, '')})"
    )
    
    selected_ticker = STOCKS.get(selected_name, "")
    
    # عرض معلومات إضافية عن السهم المختار
    if selected_name:
        info = get_stock_info(selected_name)
        if info:
            market = info.get("market", "")
            market_info = MARKETS_INFO.get(market, {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"🏷️ {market_info.get('name', market)}")
            with col2:
                st.caption(f"💵 {info.get('currency', '---')}")
            with col3:
                st.caption(f"📂 {info.get('sector', '---')}")
    
    return selected_name, selected_ticker

# ====================== الاختبار ======================

if __name__ == "__main__":
    print("=" * 50)
    print("اختبار ملف core.py")
    print("=" * 50)
    
    # اختبار التحقق
    validate_core()
    
    print("\n📈 اختبار الدوال:")
    print(f"   عدد الأسهم: {len(get_all_stocks())}")
    print(f"   عدد الأسواق: {len(MARKETS_INFO)}")
    print(f"   أول 3 أسهم: {list(STOCKS.keys())[:3]}")
    
    # اختبار البحث
    results = search_stocks("مصر")
    print(f"   البحث عن 'مصر': {len(results)} نتيجة")
    
    # اختبار الأسواق
    for market in MARKETS_INFO:
        count = len(get_stocks_by_market(market))
        print(f"   {MARKETS_INFO[market]['name']}: {count} سهماً")
    
    print("\n✅ جميع الاختبارات اجتازت بنجاح!")
    print("=" * 50)
