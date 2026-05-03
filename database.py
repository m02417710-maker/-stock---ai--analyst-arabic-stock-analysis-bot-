# database.py - المركز اللوجستي للبيانات (The Core Hub)
"""
هذا الملف هو المحرك الذي يغذي التطبيق ببيانات جميع الأسهم والأسواق.
تم تنظيمه ليسهل جلب البيانات التاريخية والتحليل اللحظي.
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
        "stocks": {
            # البنوك والتمويل
            "التجاري الدولي (CIB)": "COMI",
            "بنك مصر": "BMEL",
            "بنك التعمير والإسكان": "HDBK",
            "بنك قناة السويس": "CSBK",
            "فوري للتمويل": "FWRY",
            "بلتون المالية": "BTFH",
            "هيرميس القابضة": "HRHO",
            
            # العقارات والإنشاءات
            "طلعت مصطفى": "TMGH",
            "بالم هيلز": "PHDC",
            "مدينة مصر (الإسكان سابقاً)": "MNHD",
            "أوراسكوم للتنمية": "ORHD",
            "أوراسكوم للإنشاء": "ORAS",
            
            # الصناعة والطاقة
            "أبو قير للأسمدة": "ABUK",
            "السويدي إليكتريك": "SWDY",
            "سيدبك": "SKPC",
            "موبكو للأسمدة": "MFPC",
            "مصر للألومنيوم": "EGAL",
            "إيسترن كومباني": "EAST",
            
            # الاتصالات والتكنولوجيا
            "المصرية للاتصالات": "ETEL",
            "راية القابضة": "RAYA",
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
            "أرامكو السعودية": "2222",
            "مصرف الراجحي": "1120",
            "البنك الأهلي السعودي": "1180",
            "سابك": "2010",
            "مجموعة إس تي سي": "7010",
            "معادن": "1211",
            "دار الأركان": "4300",
            "مصرف الإنماء": "1150",
            "زين السعودية": "7020",
            "موبايلي": "7030",
        }
    },

    # ========== الأسهم الأمريكية (US Stocks) ==========
    "US": {
        "label": "🇺🇸 الأسهم الأمريكية",
        "suffix": "",
        "timezone": "America/New_York",
        "currency": "USD",
        "market_hours": "09:30 - 16:00",
        "stocks": {
            "Apple (أبل)": "AAPL",
            "Microsoft (مايكروسوفت)": "MSFT",
            "NVIDIA (إنفيديا)": "NVDA",
            "Alphabet (جوجل)": "GOOGL",
            "Amazon (أمازون)": "AMZN",
            "Meta (فيسبوك)": "META",
            "Tesla (تسلا)": "TSLA",
            "Netflix (نتفليكس)": "NFLX",
        }
    }
}

# ====================== دوال المعالجة الذكية ======================

def get_ticker_full(symbol: str, market_key: str) -> str:
    """تحويل الرمز المختصر إلى رمز كامل لـ yfinance"""
    suffix = MARKETS_DATA.get(market_key, {}).get('suffix', '')
    if suffix and not symbol.endswith(suffix):
        return f"{symbol}{suffix}"
    return symbol

def get_all_stocks_flat() -> dict:
    """تحويل الهيكل المعقد إلى قائمة بسيطة للاستخدام في القوائم المنسدلة"""
    flat_list = {}
    for m_key, m_data in MARKETS_DATA.items():
        for name, symbol in m_data['stocks'].items():
            full_display = f"{m_data['label']} | {name} ({symbol})"
            flat_list[full_display] = {
                "symbol": symbol,
                "market": m_key,
                "ticker": get_ticker_full(symbol, m_key),
                "currency": m_data['currency']
            }
    return flat_list

def search_stock(query: str):
    """البحث السريع عن سهم"""
    all_stocks = get_all_stocks_flat()
    results = {k: v for k, v in all_stocks.items() if query.lower() in k.lower()}
    return results

def get_market_stats():
    """إحصائيات سريعة للواجهة"""
    stats = {m: len(data['stocks']) for m, data in MARKETS_DATA.items()}
    stats['TOTAL'] = sum(stats.values())
    return stats

# ====================== تهيئة قاعدة البيانات المحلية ======================
import sqlite3
import pandas as pd
from pathlib import Path

# تحديد مسار قاعدة البيانات ليعمل على Streamlit و GitHub
DB_PATH = Path(__file__).parent / "data" / "boursagi.db"
DB_PATH.parent.mkdir(exist_ok=True)

def init_local_db():
    """إنشاء الجداول اللازمة للمفكرة والتحليلات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # جدول الصفقات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            market TEXT,
            entry_price REAL,
            target_price REAL,
            stop_loss REAL,
            quantity INTEGER,
            date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    conn.commit()
    conn.close()

# تنفيذ التهيئة عند استدعاء الملف
init_local_db()

if __name__ == "__main__":
    print(f"✅ تم تحميل قاعدة البيانات بنجاح.")
    print(f"📊 إجمالي الأسهم المدعومة: {get_market_stats()['TOTAL']}")
