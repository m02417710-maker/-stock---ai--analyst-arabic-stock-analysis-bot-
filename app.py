
**النماذج المتاحة:**
- Gemini 1.5 Flash (سريع)
- Gemini Pro (متوازن)
""")

if auto_analyze or analyze_clicked:
with st.spinner("🧠 جاري التحليل الذكي..."):
# محاولة الحصول على تحليل من Gemini
gemini_analysis = get_gemini_analysis(
    st.session_state.selected_name,
    st.session_state.selected_ticker,
    curr_price,
    rsi,
    change_pct
)

if gemini_analysis:
    st.markdown("### 🤖 تحليل Gemini AI")
    st.success(gemini_analysis)
else:
    # استخدام التحليل الأساسي البديل
    st.markdown("### 📊 التحليل الفني الأساسي")
    basic_analysis = basic_technical_analysis(rsi, change_pct, curr_price, st.session_state.selected_name)
    st.info(basic_analysis)
    st.caption("💡 نصيحة: قم بإضافة مفتاح Gemini API للحصول على تحليل ذكي متقدم")

return True
else:
st.error("❌ تعذر جلب بيانات السهم")
return True

# ====================== عرض زر السهم ======================
def display_stock_card(name: str, ticker: str, signal_data: tuple, unique_id: int = 0):
"""عرض زر سهم مع مفتاح فريد"""

signal, rsi, change_pct, price = signal_data

if signal == "buy":
emoji = "🟢"
signal_text = "شراء"
elif signal == "sell":
emoji = "🔴"
signal_text = "بيع"
else:
emoji = "🟡"
signal_text = "مراقبة"

change_symbol = "▲" if change_pct >= 0 else "▼"

# نص الزر
button_text = f"{emoji} {name[:40]} | 💰{price:.2f} | {change_symbol}{abs(change_pct):.1f}% | 📊RSI:{rsi:.0f} | {signal_text}"

# مفتاح فريد
unique_key = f"stock_btn_{ticker}_{unique_id}"

if st.button(button_text, key=unique_key, use_container_width=True):
select_stock(ticker, name)

# ====================== بقية التوابع (مختصرة للاختصار) ======================
# stock_analysis_tab, sectors_tab, news_tab, show_stats_bar, main
# ... (الباقي كما هو في الكود السابق مع الحفاظ على نفس المنطق)

# ====================== الدالة الرئيسية ======================
def main():
"""التطبيق الرئيسي"""

st.markdown("""
<div class="main-header">
<h1>🇪🇬 منصة تحليل البورصة المصرية</h1>
<p>تحليل فني متقدم | إشارات ذكية | أخبار فورية | ذكاء اصطناعي</p>
</div>
""", unsafe_allow_html=True)

# إحصائيات سريعة
stats = get_market_statistics()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📈 إجمالي الأسهم", stats['total_stocks'])
col2.metric("🏢 عدد القطاعات", stats['sectors'])
col3.metric("💰 العملة", stats['currency'])
col4.metric("⏰ وقت التداول", stats['trading_hours'])

# حالة Gemini
has_gemini = init_gemini() is not None
col5.metric("🤖 Gemini AI", "🟢 متصل" if has_gemini else "🔴 غير متصل")

st.markdown("---")

if st.session_state.selected_ticker is not None:
display_technical_analysis()
else:
# تبويبات رئيسية مختصرة
from database import get_all_egyptian_stocks

st.markdown("### 📋 أسهم البورصة المصرية")

all_stocks = get_all_egyptian_stocks()
filtered_stocks = all_stocks

# عرض الأسهم
buy_list = []
sell_list = []
neutral_list = []

with st.spinner("جاري تحليل الأسهم..."):
for name, ticker in list(filtered_stocks.items())[:50]:  # عرض أول 50 سهم للسرعة
signal_data = get_stock_signal(ticker)
signal = signal_data[0]

if signal == "buy":
    buy_list.append((name, ticker, signal_data))
elif signal == "sell":
    sell_list.append((name, ticker, signal_data))
else:
    neutral_list.append((name, ticker, signal_data))

if sell_list:
st.markdown("## 🔴 أسهم يوصى ببيعها")
for idx, (name, ticker, sig_data) in enumerate(sell_list):
display_stock_card(name, ticker, sig_data, idx)

if buy_list:
st.markdown("## 🟢 أسهم يوصى بشرائها")
for idx, (name, ticker, sig_data) in enumerate(buy_list):
display_stock_card(name, ticker, sig_data, idx + 100)

if neutral_list:
st.markdown("## 🟡 أسهم للمراقبة")
for idx, (name, ticker, sig_data) in enumerate(neutral_list):
display_stock_card(name, ticker, sig_data, idx + 200)

st.markdown("---")
st.caption("🇪🇬 **البورصة المصرية (EGX)** | البيانات من Yahoo Finance | الإشارات مبنية على مؤشر RSI")

if __name__ == "__main__":
main()
