# ============================================================
# ملف: run_local_scanner.py
# للتشغيل المحلي أو على PythonAnywhere/Heroku
# ============================================================

import schedule
import time
from scanner import run_scanner
from datetime import datetime

def main():
    print("🚀 تشغيل الماسح التلقائي محلياً")
    print(f"🕐 بدء التشغيل: {datetime.now()}")
    
    # جدولة التشغيل كل 15 دقيقة
    schedule.every(15).minutes.do(run_scanner)
    
    # تشغيل أول مرة فوراً
    run_scanner()
    
    print("✅ الماسح يعمل في الخلفية...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # انتظر 60 ثانية بين كل فحص

if __name__ == "__main__":
    main()
