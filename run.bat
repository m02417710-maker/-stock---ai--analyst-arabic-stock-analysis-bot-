@echo off
echo 🚀 تشغيل البورصجي AI...
cd /d "%~dp0"

if not exist "venv" (
    echo 📦 إنشاء البيئة الافتراضية...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

mkdir data 2>nul
mkdir logs 2>nul
mkdir reports 2>nul

streamlit run app.py --server.port=8501
