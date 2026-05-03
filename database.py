# database.py - قاعدة البيانات الأسطورية
"""
أساطير الأسهم - قاعدة بيانات شاملة لكل أسواق العالم
"""

from typing import Dict, List, Optional
from datetime import datetime

# ====================== الأسواق العالمية المدعومة ======================
MARKETS_DATA = {
    # 🌍 الشرق الأوسط وشمال أفريقيا
    "EGX": {
        "name": "🇪🇬 البورصة المصرية",
        "suffix": ".CA",
        "timezone": "Africa/Cairo",
        "currency": "EGP",
        "market_hours": "10:00 - 14:30",
        "prayer_break": "12:30 - 13:30",
        "index": "^EGX30",
        "stocks": {
            "🏦 البنك التجاري الدولي (CIB)": "COMI.CA",
            "🏦 بنك مصر": "BMEL.CA", 
            "🏦 بنك الإسكندرية": "ALEX.CA",
            "🏦 البنك الأهلي المصري": "NBE.CA",
            "🏦 بنك التعمير والإسكان": "HDBK.CA",
            "🏦 بنك قناة السويس": "CSBK.CA",
            "🏗️ طلعت مصطفى القابضة": "TMGH.CA",
            "🏗️ بالم هيلز للتعمير": "PHDC.CA",
            "🏗️ مدينة نصر للإسكان": "MNHD.CA",
            "⚡ السويدي إليكتريك": "SWDY.CA",
            "📡 تليكوم مصر": "ETEL.CA",
            "💳 فوري لتكنولوجيا البنوك": "FWRY.CA",
            "🚗 جي بي أوتو": "JUFO.CA",
            "💊 المصرية للمستحضرات الطبية": "EGPC.CA",
            "🥤 الشرقية للدخان": "EAST.CA",
            "🌾 أبو قير للأسمدة": "ABUK.CA",
            "🔬 موبكو": "MFPC.CA",
            "🔨 حديد المصريين": "ESRS.CA",
            "🏭 مصر للألومنيوم": "EGAL.CA",
        }
    },
    
    "TADAWUL": {
        "name": "🇸🇦 تداول السعودية",
        "suffix": ".SR", 
        "timezone": "Asia/Riyadh",
        "currency": "SAR",
        "market_hours": "10:00 - 15:00",
        "index": "^TASI",
        "stocks": {
            "🛢️ أرامكو السعودية": "2222.SR",
            "🏦 مصرف الراجحي": "1120.SR",
            "🏦 البنك الأهلي السعودي": "1180.SR",
            "🏦 بنك الرياض": "1010.SR",
            "🏦 بنك الجزيرة": "1020.SR",
            "🏦 بنك البلاد": "1140.SR",
            "🏦 بنك الإنماء": "1150.SR",
            "🏦 بنك ساب": "1060.SR",
            "🧪 سابك": "2010.SR",
            "📡 مجموعة STC": "7010.SR",
            "📱 موبايلي": "7030.SR",
            "📱 زين السعودية": "7020.SR",
            "🛒 أسواق عبد الله العثيم": "4001.SR",
            "🏠 دار الأركان": "4300.SR",
            "⛏️ معادن": "1211.SR",
        }
    },
    
    "ADX": {
        "name": "🇦🇪 سوق أبوظبي",
        "suffix": ".AD",
        "timezone": "Asia/Dubai", 
        "currency": "AED",
        "market_hours": "10:00 - 14:00",
        "index": "^ADI",
        "stocks": {
            "🏦 بنك أبوظبي الأول": "FAB.AD",
            "📡 اتصالات": "EAND.AD",
            "🏦 بنك أبوظبي التجاري": "ADCB.AD",
            "⚡ أبوظبي الوطني للطاقة": "TAQA.AD",
            "🏗️ الدار العقارية": "ALDAR.AD",
        }
    },
    
    "DFM": {
        "name": "🇦🇪 سوق دبي",
        "suffix": ".DU",
        "timezone": "Asia/Dubai",
        "currency": "AED", 
        "market_hours": "10:00 - 14:00",
        "index": "^DFMGI",
        "stocks": {
            "🏗️ إعمار العقارية": "EMAAR.DU",
            "🏦 بنك دبي الإسلامي": "DIB.DU",
            "🏦 سوق دبي المالي": "DFM.DU",
            "🏦 بنك الإمارات دبي الوطني": "ENBD.DU",
        }
    },
    
    "US": {
        "name": "🇺🇸 وول ستريت",
        "suffix": "",
        "timezone": "America/New_York",
        "currency": "USD",
        "market_hours": "09:30 - 16:00",
        "index": "^SPX",
        "stocks": {
            "🍎 Apple Inc.": "AAPL",
            "💻 Microsoft Corp.": "MSFT",
            "🔍 Alphabet (Google)": "GOOGL",
            "📦 Amazon.com": "AMZN",
            "🎮 NVIDIA Corp.": "NVDA",
            "📱 Meta Platforms": "META",
            "🚗 Tesla Inc.": "TSLA",
            "🎬 Netflix Inc.": "NFLX",
            "💳 Visa Inc.": "V",
            "💳 Mastercard Inc.": "MA",
            "🏦 JPMorgan Chase": "JPM",
            "💊 Pfizer Inc.": "PFE",
            "🥤 Coca-Cola": "KO",
            "🍔 McDonald's": "MCD",
            "👟 Nike Inc.": "NKE",
        }
    }
}

# ====================== دوال متقدمة ======================
def get_all_stocks() -> Dict:
    """جلب جميع الأسهم مع معلوماتها"""
    all_stocks = {}
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            full_name = f"{market_data['name']} - {stock_name}"
            all_stocks[full_name] = {
                'ticker': stock_ticker,
                'market': market_key,
                'market_name': market_data['name'],
                'currency': market_data['currency'],
                'suffix': market_data['suffix']
            }
    return all_stocks

def get_market_statistics() -> Dict:
    """إحصائيات متقدمة عن الأسواق"""
    stats = {}
    for market_key, market_data in MARKETS_DATA.items():
        stats[market_key] = {
            'name': market_data['name'],
            'count': len(market_data['stocks']),
            'currency': market_data['currency'],
            'index': market_data.get('index', 'N/A'),
            'hours': market_data['market_hours']
        }
    stats['TOTAL'] = sum(s['count'] for s in stats.values())
    return stats

def search_stock(keyword: str) -> Dict:
    """بحث فوري وسريع"""
    results = {}
    keyword_lower = keyword.lower()
    
    for market_key, market_data in MARKETS_DATA.items():
        for stock_name, stock_ticker in market_data['stocks'].items():
            if (keyword_lower in stock_name.lower() or 
                keyword_lower in stock_ticker.lower() or
                keyword_lower in market_key.lower()):
                full_name = f"{market_data['name']} - {stock_name}"
                results[full_name] = {
                    'ticker': stock_ticker,
                    'market': market_key,
                    'market_name': market_data['name'],
                    'currency': market_data['currency']
                }
    return results

def get_stocks_by_sector(market: str, sector: str = None) -> Dict:
    """تصفية الأسهم حسب القطاع"""
    # يمكن توسيعها حسب الحاجة
    return {}
