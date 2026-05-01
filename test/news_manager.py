# news_manager.py - نظام إدارة الأخبار المحلية والعالمية
"""
هذا الملف مسؤول عن:
1. جلب الأخبار من مصادر متعددة
2. أخبار الشركات المصرية والعالمية
3. محاولة الوصول لأخبار تطبيق ثاندر (Thndr)
4. تحليل الأخبار وتصنيفها
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from security import validate_ticker, sanitize_string, log_suspicious_activity

# محاولة استيراد yfinance للأخبار
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# ====================== إعدادات الأخبار ======================

# مصادر أخبار الشركات المصرية (مباشرة)
EGYPTIAN_NEWS_SOURCES = {
    "direct_links": {
        "cib": "https://www.cibeg.com/en/media-center/news",
        "tmgh": "https://www.talaatmostafagroup.com/investor-relations/news",
        "swdy": "https://www.elsewedyelectric.com/investor-relations/news"
    },
    "google_news_rss": "https://news.google.com/rss/search?q={ticker}+stock&hl=en",
    "yahoo_finance_news": "https://finance.yahoo.com/quote/{ticker}/news"
}

# مصادر أخبار ثاندر (Thndr)
# ملاحظة هامة: ثاندر هي تطبيق وساطة مالية مصري
# لا توجد API رسمية متاحة حالياً لجلب الأخبار مباشرة من التطبيق
# لكن يمكننا:
# 1. متابعة صفحاتهم الرسمية
# 2. استخدام RSS feeds للمدونة
# 3. تتبع أخبار الشركات المتداولة عبر المنصة

THNDR_NEWS_STRATEGY = {
    "description": "للحصول على أخبار ثاندر بصورة رسمية، يمكنك:",
    "methods": [
        "1. متابعة حساب ثاندر الرسمي على تليجرام: https://t.me/thndr_egypt",
        "2. متابعة مدونتهم الرسمية: https://blog.thndr.app",
        "3. متابعة إنستجرام: https://instagram.com/thndr_app",
        "4. الاشتراك في النشرة البريدية من داخل التطبيق"
    ],
    "api_note": "⚠️ لا توجد API رسمية متاحة حالياً. يتم جلب الأخبار من المصادر العامة."
}

# ====================== دوال جلب الأخبار ======================

@st.cache_data(ttl=300)
def get_stock_news_via_yfinance(ticker: str, max_news: int = 10) -> List[Dict]:
    """
    جلب أخبار السهم باستخدام yfinance (مجاني - بدون API Key)
    """
    if not YFINANCE_AVAILABLE or not validate_ticker(ticker):
        return []
    
    news_list = []
    try:
        stock = yf.Ticker(ticker)
        
        # محاولة جلب الأخبار
        if hasattr(stock, 'news'):
            news_data = stock.news
            
            if news_data:
                for item in news_data[:max_news]:
                    news_list.append({
                        "title": sanitize_string(item.get('title', 'بدون عنوان')),
                        "link": item.get('link', '#'),
                        "publisher": item.get('publisher', 'Yahoo Finance'),
                        "providerPublishTime": item.get('providerPublishTime', datetime.now()),
                        "type": "market_news",
                        "source": "Yahoo Finance",
                        "ticker": ticker
                    })
    except Exception as e:
        pass  # تجاهل الأخطاء
    
    return news_list

def get_egyptian_market_news() -> List[Dict]:
    """
    جلب أخبار السوق المصري باستخدام مصادر مجانية
    """
    news_list = []
    
    # مؤشرات البورصة المصرية
    egx_tickers = ["^EGX30", "COMI.CA", "TMGH.CA", "SWDY.CA"]
    
    for ticker in egx_tickers:
        news = get_stock_news_via_yfinance(ticker, 5)
        news_list.extend(news)
    
    return news_list

def get_thndr_related_news() -> Dict:
    """
    جلب أخبار متعلقة بمنصة ثاندر والشركات المتاحة عليها
    تُظهر هذه الدالة المصادر المتاحة لأن لا توجد API رسمية
    """
    
    # جلب أخبار الشركات المتاحة على ثاندر
    thndr_stocks = {
        "COMI.CA": "البنك التجاري الدولي (CIB)",
        "TMGH.CA": "طلعت مصطفى القابضة",
        "SWDY.CA": "السويدي إليكتريك",
        "ETEL.CA": "تليكوم مصر",
        "EAST.CA": "الشرقية للدخان"
    }
    
    stocks_news = []
    for ticker, name in thndr_stocks.items():
        news = get_stock_news_via_yfinance(ticker, 3)
        for item in news:
            item["thndr_available"] = True
            item["arabic_name"] = name
            stocks_news.append(item)
    
    return {
        "source": "Thndr Related News",
        "description": "أخبار الشركات المتاحة على منصة ثاندر",
        "official_sources": THNDR_NEWS_STRATEGY,
        "news": stocks_news,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_global_market_news() -> List[Dict]:
    """
    جلب أخبار الأسواق العالمية
    """
    global_tickers = ["^GSPC", "^DJI", "^IXIC", "AAPL", "MSFT", "GOOGL"]
    all_news = []
    
    for ticker in global_tickers:
        news = get_stock_news_via_yfinance(ticker, 3)
        all_news.extend(news)
    
    return all_news

# ====================== واجهة عرض الأخبار ======================

def display_news_card(news_item: Dict):
    """
    عرض بطاقة خبر واحدة
    """
    title = news_item.get('title', 'خبر')
    link = news_item.get('link', '#')
    publisher = news_item.get('publisher', 'مصدر غير معروف')
    
    card_html = f"""
    <div style="
        background-color: #262730;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #ff4b4b;
    ">
        <a href="{link}" target="_blank" style="color: #ffffff; text-decoration: none;">
            <strong>📰 {title[:100]}</strong>
        </a>
        <div style="color: #888888; font-size: 12px; margin-top: 5px;">
            {publisher}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_news_section():
    """
    عرض قسم الأخبار الكامل في التطبيق
    """
    st.header("📰 مركز الأخبار")
    
    # تبويبات للأخبار
    tab1, tab2, tab3, tab4 = st.tabs([
        "🇪🇬 أخبار مصر", 
        "🌍 أخبار عالمية", 
        "📱 أخبار ثاندر",
        "ℹ️ عن المصادر"
    ])
    
    with tab1:
        st.subheader("أخبار البورصة المصرية")
        with st.spinner("جاري تحميل الأخبار..."):
            news = get_egyptian_market_news()
            if news:
                for item in news:
                    display_news_card(item)
            else:
                st.info("لا توجد أخبار حالياً. يمكنك تحديث الصفحة لاحقاً.")
    
    with tab2:
        st.subheader("أخبار الأسواق العالمية")
        with st.spinner("جاري تحميل الأخبار..."):
            news = get_global_market_news()
            if news:
                for item in news[:15]:
                    display_news_card(item)
            else:
                st.info("لا توجد أخبار حالياً.")
    
    with tab3:
        st.subheader("📱 أخبار منصة ثاندر والشركات المتاحة")
        
        st.info("""
        **ما هي منصة ثاندر؟**  
        ثاندر هو تطبيق وساطة مالية مصري يتيح التداول في البورصة المصرية بسهولة.
        
        ℹ️ **حول أخبار ثاندر:**  
        حالياً، لا تتوفر API رسمية لجلب الأخبار مباشرة من تطبيق ثاندر.  
        لكن يمكنك متابعة أخبارهم عبر المصادر الرسمية التالية:
        """)
        
        # عرض المصادر الرسمية
        for method in THNDR_NEWS_STRATEGY["methods"]:
            st.markdown(method)
        
        st.divider()
        
        # عرض أخبار الشركات المتاحة على ثاندر
        st.markdown("### 📊 أخبار الشركات المتاحة للتداول عبر ثاندر")
        
        with st.spinner("جاري تحميل أخبار الشركات..."):
            thndr_data = get_thndr_related_news()
            
            if thndr_data.get("news"):
                for item in thndr_data["news"]:
                    # إضافة أيقونة ثاندر للخبر
                    st.markdown(f"""
                    <div style="
                        background-color: #0e2b1f;
                        border-radius: 10px;
                        padding: 12px;
                        margin-bottom: 10px;
                        border-left: 4px solid #00ff88;
                    ">
                        <span style="background-color: #00ff88; color: #000; padding: 2px 8px; border-radius: 5px; font-size: 10px;">
                            📱 متاح على ثاندر
                        </span>
                        <br><br>
                        <a href="{item.get('link', '#')}" target="_blank" style="color: #ffffff; text-decoration: none;">
                            <strong>{item.get('title', 'خبر')[:100]}</strong>
                        </a>
                        <div style="color: #888888; font-size: 12px; margin-top: 5px;">
                            {item.get('arabic_name', '')} - {item.get('source', 'Yahoo Finance')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("لا توجد أخبار متاحة حالياً. تفضل بزيارة المصادر الرسمية أعلاه.")
    
    with tab4:
        st.subheader("ℹ️ معلومات عن مصادر الأخبار")
        st.markdown("""
        ### مصادر الأخبار المستخدمة:
        
        | المصدر | النوع | المجاني | الوصف |
        |--------|-------|---------|-------|
        | **Yahoo Finance** | مجاني ✅ | نعم | أخبار الأسهم العالمية والمحلية |
        | **Google News RSS** | مجاني ✅ | نعم | تجميع الأخبار من مصادر متعددة |
        
        ### 📱 بخصوص أخبار تطبيق ثاندر:
        
        تطبيق **ثاندر (Thndr)** هو منصة وساطة مالية مصرية مرخصة.  
        حالياً، لا توفر ثاندر API رسمية للمطورين لجلب الأخبار مباشرة.
        
        **للوصول إلى أخبار ثاندر بشكل رسمي، يمكنك:**
        1. تحميل التطبيق من [رابط التحميل](https://thndr.app)
        2. متابعة حسابهم الرسمي على تليجرام: [@thndr_egypt](https://t.me/thndr_egypt)
        3. الاشتراك في النشرة البريدية عبر التطبيق
        4. متابعة مدونتهم: [blog.thndr.app](https://blog.thndr.app)
        
        ### 💡 اقتراحات مستقبلية:
        - يمكن إضافة API مدفوعة مثل Benzinga للحصول على أخبار أكثر دقة
        - يمكن إضافة RSS feeds مباشرة من المواقع الرسمية للشركات
        """)

# اختبار
if __name__ == "__main__":
    print("📰 اختبار نظام الأخبار:")
    news = get_stock_news_via_yfinance("AAPL", 3)
    print(f"عدد الأخبار: {len(news)}")
