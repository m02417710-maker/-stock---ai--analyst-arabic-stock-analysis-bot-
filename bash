# إضافة الملفات الجديدة
git add database.py core.py app.py

# الالتزام
git commit -m "Enterprise Architecture: Added database.py for 100+ stocks across EGX, TADAWUL, ADX, DFM, US markets"

# الرفع
git push origin main
# 1. انتقل إلى مجلد المشروع (غير المسار حسب موقعك)
cd /path/to/your/project

# 2. احذف الملفات القديمة والمكررة
rm -f engines.py intelligence.py scanner.py run_local_scanner.py clock.py bash yaml

# 3. احذف المجلدات غير المهمة
rm -rf devcontainer database test __pycache__ .streamlit

# 4. احذف الملفات المؤقتة
rm -f *.pyc *.log
