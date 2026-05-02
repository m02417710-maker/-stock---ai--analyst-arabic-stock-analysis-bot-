@echo off
:: run.bat - تشغيل التطبيق على ويندوز

echo ========================================
echo    البورصجي AI - نظام تحليل الأسهم
echo ========================================
echo.

:: التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python غير مثبت. يرجى تثبيت Python اولا
    pause
    exit /b 1
)

echo [INFO] تم العثور على Python

:: تثبيت المتطلبات
echo [INFO] جاري تثبيت المتطلبات...
pip install -r requirements.txt

:: تشغيل التطبيق
echo [INFO] جاري تشغيل التطبيق...
streamlit run app.py --server.port=8501

pause
