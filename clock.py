import yfinance as yf
import requests
import os

# هذه البيانات يتم جلبها من إعدادات GitHub Secrets
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

# قائمة الأسهم التي تريد مراقبتها تلقائياً كل صباح
WATCHLIST = ["COMI.CA", "TMGH.CA", "2222.SR", "NVDA"]

def run_automation():
    report = "🔔 *تقرير البورصة الصباحي التلقائي* 🔔\n\n"
    for ticker in WATCHLIST:
        data = yf.Ticker(ticker).history(period="2d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            emoji = "🟢" if change >= 0 else "🔴"
            report += f"{emoji} `{ticker}`: {price:.2f} ({change:.2f}%)\n"
    
    report += "\n🚀 تم التحديث من خلال *GitHub Actions*"
    send_msg(report)

if __name__ == "__main__":
    run_automation()
