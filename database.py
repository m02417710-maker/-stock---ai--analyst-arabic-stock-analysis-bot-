# database.py - الإصدار المتكامل مع جميع الدوال
"""
قاعدة البيانات المركزية لجميع الأسهم
"""

from typing import Dict, List, Optional

# ====================== الأسواق العالمية المدعومة ======================
MARKETS_DATA = {
    "EGX": {
        "name": "🇪🇬 البورصة المصرية",
        "label": "🇪🇬 البورصة المصرية",  # إضافة label للتطابق
        "suffix": ".CA",
        "timezone": "Africa/Cairo",
        "currency": "EGP",
        "market_hours": "10:00 - 14:30",
        "stocks": {
            "البنك التجاري الدولي (CIB)": "COMI.CA",
            "طلعت مصطفى القابضة": "TMGH.CA",
            "السويدي إليكتريك": "SWDY.CA",
            "تليكوم مصر": "ETEL.CA",
            "الشرقية للدخان": "EAST.CA",
            "مصر للألومنيوم": "EGAL.CA",
            "موبكو": "MFPC.CA",
            "أوراسكوم للإنشاءات": "ORAS.CA",
            "جي بي أوتو": "JUFO.CA",
            "أبو قير للأسمدة": "ABUK.CA",
            "البنك الهولندي": "HRHO.CA",
        }
    },
    
    "TADAWUL": {
        "name": "🇸🇦 تداول السعودية",
        "label": "🇸🇦 تداول السعودية",  # إضافة label للتطابق
        "suffix": ".SR",
        "timezone": "Asia/Riyadh",
        "currency": "SAR",
        "market_hours": "10:00 - 15:00",
        "stocks": {
            "أرامكو السعودية": "2222.SR",
            "مصرف الراجحي": "1120.SR",
            "البنك الأهلي السعودي": "1180.SR",
            "مجموعة STC": "7010.SR",
            "سابك": "2010.SR",
        }
    },
    
    "ADX": {
        "name": "🇦🇪 سوق أبوظبي",
        "label": "🇦🇪 سوق أبوظبي",  # إضافة label للتطابق
        "suffix": ".AD",
        "timezone": "Asia/Dubai",
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "stocks": {
            "بنك أبوظبي الأول": "FAB.AD",
            "اتصالات": "EAND.AD",
        }
    },
    
    "DFM": {
        "name": "🇦🇪 سوق دبي",
        "label": "🇦🇪 سوق دبي",  # إضافة label للتطابق
        "suffix": ".DU",
        "timezone": "Asia/Dubai",
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "stocks": {
            "إعمار العقارية": "EMAAR.DU",
            "بنك دبي الإسلامي": "DIB.DU",
        }
    },
    
    "US": {
        "name": "🇺🇸 الأسهم الأمريكية",
        "label": "🇺🇸 الأسهم الأمريكية",  # إضافة label للتطابق
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
        }
    }
}

# ====================== الدوال الأساسية ======================
def get_all_stocks() -> Dict:
    """جلب جميع الأسهم"""
    all_stocks = {}
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            full_name = f"{market_data['name']} - {stock_name}"
            all_stocks[full_name] = {
                'ticker': stock_ticker,
                'market': market_key,
                'currency': market_data['currency']
            }
    return all_stocks

def get_market_statistics() -> Dict:
    """إحصائيات الأسواق"""
    stats = {}
    for market_key, market_data in MARKETS_DATA.items():
        stats[market_key] = {
            'name': market_data['name'],
            'count': len(market_data['stocks']),
            'currency': market_data['currency']
        }
    stats['TOTAL'] = sum(s['count'] for s in stats.values())
    return stats

def get_market_info(market: str) -> Optional[Dict]:
    """جلب معلومات السوق - هذه الدالة كانت مفقودة!"""
    market_upper = market.upper()
    
    # محاولة إيجاد السوق بالاسم الكامل أو المختصر
    for market_key, market_data in MARKETS_DATA.items():
        if market_key == market_upper or market_data['name'] == market or market_data.get('label') == market:
            return {
                'name': market_data['name'],
                'market_hours': market_data.get('market_hours', 'غير محدد'),
                'currency': market_data['currency'],
                'timezone': market_data.get('timezone', 'غير محدد'),
                'suffix': market_data.get('suffix', ''),
                'stocks_count': len(market_data['stocks'])
            }
    
    # إذا لم يتم العثور على السوق, نرجع معلومات افتراضية
    return {
        'name': market if market else 'سوق عام',
        'market_hours': 'يختلف حسب السوق',
        'currency': 'محلي',
        'timezone': 'محلي',
        'suffix': '',
        'stocks_count': 0
    }

def get_market_info_by_ticker(ticker: str) -> Optional[Dict]:
    """جلب معلومات السوق بناءً على رمز السهم"""
    for market_data in MARKETS_DATA.values():
        suffix = market_data.get('suffix', '')
        if suffix and ticker.endswith(suffix):
            return get_market_info(market_data['name'])
        elif not suffix and ticker in market_data['stocks'].values():
            return get_market_info(market_data['name'])
    return None

def search_stock(keyword: str) -> Dict:
    """البحث عن سهم"""
    results = {}
    keyword_lower = keyword.lower()
    
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            if (keyword_lower in stock_name.lower() or 
                keyword_lower in stock_ticker.lower()):
                full_name = f"{market_data['name']} - {stock_name}"
                results[full_name] = {
                    'ticker': stock_ticker,
                    'market': market_key,
                    'currency': market_data['currency']
                }
    return results

# للتوافق مع الكود القديم
def get_stocks_by_market(market_key: str) -> Dict:
    """جلب أسهم سوق معين"""
    if market_key in MARKETS_DATA:
        stocks = {}
        for name, ticker in MARKETS_DATA[market_key]['stocks'].items():
            stocks[f"{MARKETS_DATA[market_key]['name']} - {name}"] = ticker
        return stocks
    return {}
