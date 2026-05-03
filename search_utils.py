# search_utils.py - وحدة البحث من Google و SerpAPI
"""
هذه الوحدة مسؤولة عن البحث في Google وجلب الأخبار
"""

import streamlit as st
from typing import List, Dict, Optional
import requests
from datetime import datetime

# ====================== Google Custom Search ======================
def init_google_search():
    """تهيئة بحث Google"""
    try:
        if "GOOGLE_API_KEY" in st.secrets and "GOOGLE_SEARCH_ENGINE_ID" in st.secrets:
            return {
                "api_key": st.secrets["GOOGLE_API_KEY"],
                "search_engine_id": st.secrets["GOOGLE_SEARCH_ENGINE_ID"]
            }
    except Exception as e:
        st.error(f"خطأ في تهيئة بحث Google: {e}")
    return None

def search_google(query: str, num_results: int = 10, language: str = "ar") -> List[Dict]:
    """البحث في Google باستخدام Custom Search API"""
    config = init_google_search()
    
    if not config:
        return []
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": config["api_key"],
            "cx": config["search_engine_id"],
            "q": query,
            "num": min(num_results, 10),
            "hl": language,
            "gl": "eg" if language == "ar" else "us"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        search_results = []
        
        if "items" in data:
            for item in data["items"]:
                search_results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'source': 'Google',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        return search_results
        
    except Exception as e:
        st.error(f"خطأ في البحث: {e}")
        return []

# ====================== SerpAPI البحث ======================
def search_with_serpapi(query: str, num_results: int = 10) -> List[Dict]:
    """البحث باستخدام SerpAPI"""
    try:
        if "SERPAPI_API_KEY" not in st.secrets:
            return []
        
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": st.secrets["SERPAPI_API_KEY"],
            "num": num_results,
            "hl": "ar",
            "gl": "eg"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        search_results = []
        
        if "organic_results" in data:
            for item in data["organic_results"][:num_results]:
                search_results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayed_link', ''),
                    'source': 'SerpAPI',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        
        return search_results
        
    except Exception as e:
        st.error(f"خطأ في SerpAPI: {e}")
        return []

# ====================== أخبار متخصصة بالبورصة ======================
def search_stock_news(stock_name: str, stock_ticker: str = None) -> List[Dict]:
    """البحث عن أخبار خاصة بسهم معين"""
    
    queries = [
        f"أخبار {stock_name} البورصة المصرية",
        f"{stock_name} أرباح",
        f"{stock_name} توصيات",
        f"{stock_name} سهم"
    ]
    
    if stock_ticker:
        queries.append(f"{stock_ticker} مصر EGX")
    
    all_results = []
    
    for query in queries[:3]:  # نجرب 3 استعلامات مختلفة
        results = search_google(query, num_results=3)
        all_results.extend(results)
    
    # إزالة التكرارات
    unique_results = []
    seen_links = set()
    
    for result in all_results:
        if result['link'] not in seen_links:
            seen_links.add(result['link'])
            unique_results.append(result)
    
    return unique_results[:10]

def search_market_news() -> List[Dict]:
    """البحث عن أخبار عامة عن السوق"""
    
    queries = [
        "آخر أخبار البورصة المصرية اليوم",
        "EGX30 البورصة المصرية",
        "اقتصاد مصر سوق الأسهم",
        "قرارات البنك المركزي المصري"
    ]
    
    all_results = []
    
    for query in queries:
        results = search_google(query, num_results=3)
        all_results.extend(results)
    
    # إزالة التكرارات
    unique_results = []
    seen_links = set()
    
    for result in all_results:
        if result['link'] not in seen_links:
            seen_links.add(result['link'])
            unique_results.append(result)
    
    return unique_results[:15]

def search_commodity_news(commodity: str) -> List[Dict]:
    """البحث عن أخبار السلع (ذهب، نفط، الخ)"""
    
    queries = [
        f"سعر {commodity} اليوم",
        f"أخبار {commodity} العالمية",
        f"توقعات {commodity}"
    ]
    
    all_results = []
    
    for query in queries:
        results = search_google(query, num_results=3)
        all_results.extend(results)
    
    return all_results[:8]

# ====================== دالة البحث الرئيسية ======================
def smart_search(query: str, category: str = "عام") -> List[Dict]:
    """بحث ذكي حسب الفئة"""
    
    if category == "أسهم":
        enhanced_query = f"{query} سهم البورصة المصرية أرباح توصيات"
    elif category == "سلع":
        enhanced_query = f"{query} سعر اليوم توقعات السوق"
    elif category == "اقتصاد":
        enhanced_query = f"{query} مصر الاقتصاد قرارات البنك المركزي"
    else:
        enhanced_query = query
    
    # محاولة البحث أولاً بـ SerpAPI إذا كان متاحاً
    if "SERPAPI_API_KEY" in st.secrets:
        results = search_with_serpapi(enhanced_query, num_results=10)
        if results:
            return results
    
    # الرجوع إلى Google Custom Search
    return search_google(enhanced_query, num_results=10)

# ====================== دالة لتحليل الأخبار بـ Gemini ======================
def analyze_news_with_gemini(news_text: str, stock_name: str = None) -> str:
    """تحليل الخبر باستخدام الذكاء الاصطناعي"""
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            return "⚠️ يرجى إضافة مفتاح Gemini API لتفعيل تحليل الأخبار"
        
        import google.generativeai as genai
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        context = f"الخبر متعلق بـ {stock_name}" if stock_name else "الخبر متعلق بالبورصة المصرية"
        
        prompt = f"""
        أنت خبير تحليل مالي. قم بتحليل هذا الخبر الاقتصادي:
        
        {context}
        
        نص الخبر:
        {news_text}
        
        قم بتحليل:
        1. تأثير الخبر على السوق (إيجابي/سلبي/محايد)
        2. القطاعات المتأثرة
        3. توصية مختصرة للمستثمر
        
        الرد بالعربية بشكل مختصر وواضح.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"خطأ في التحليل: {e}"
