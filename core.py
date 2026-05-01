# core.py - الإصدار المعماري المتكامل
"""
ملف الإدارة المركزية - يتعامل مع قاعدة البيانات ويوفر واجهة موحدة
"""

from typing import Dict, List, Optional
from database import (
    MARKETS_DATA, 
    get_all_stocks, 
    get_stocks_by_market,
    search_stock,
    get_market_info,
    get_market_statistics
)

# ====================== تجهيز البيانات ======================
# جلب جميع الأسهم تلقائياً من قاعدة البيانات
ALL_STOCKS_DATA = get_all_stocks()

# قائمة الأسماء المعروضة للمستخدم (لـ selectbox)
STOCK_NAMES = list(ALL_STOCKS_DATA.keys())

# قاموس الرموز (الاسم -> رمز السهم)
STOCK_TICKERS = {name: data['ticker'] for name, data in ALL_STOCKS_DATA.items()}

# قاموس معلومات إضافية عن كل سهم
STOCK_METADATA = {name: {
    'market': data['market'],
    'currency': data['currency'],
    'suffix': data['suffix']
} for name, data in ALL_STOCKS_DATA.items()}

# ====================== دوال مساعدة ======================
def get_stock_ticker(name: str) -> Optional[str]:
    """إرجاع رمز السهم من الاسم"""
    return STOCK_TICKERS.get(name)

def get_stock_market(name: str) -> Optional[str]:
    """إرجاع سوق السهم"""
    return STOCK_METADATA.get(name, {}).get('market')

def get_stock_currency(name: str) -> Optional[str]:
    """إرجاع عملة السهم"""
    return STOCK_METADATA.get(name, {}).get('currency')

def search_stocks_by_keyword(keyword: str) -> Dict:
    """البحث عن أسهم بكلمة مفتاحية"""
    return search_stock(keyword)

def get_grouped_stocks() -> Dict:
    """تجميع الأسهم حسب الأسواق للعرض المنسق"""
    grouped = {}
    for market_key in MARKETS_DATA.keys():
        grouped[market_key] = get_stocks_by_market(market_key)
    return grouped

def validate_stocks() -> bool:
    """التحقق من صحة البيانات"""
    if not STOCK_NAMES:
        print("❌ خطأ: لا توجد أسهم في قاعدة البيانات")
        return False
    
    # التحقق من عدم وجود تكرار في الرموز
    tickers = list(STOCK_TICKERS.values())
    duplicates = [t for t in tickers if tickers.count(t) > 1]
    
    if duplicates:
        print(f"⚠️ تحذير: تكرار في الرموز: {set(duplicates)}")
    
    print(f"✅ تم تحميل {len(STOCK_NAMES)} سهماً بنجاح")
    print(f"📊 الأسواق المدعومة: {list(MARKETS_DATA.keys())}")
    return True

# اختبار عند التحميل
if __name__ == "__main__":
    validate_stocks()
    print(get_market_statistics())
