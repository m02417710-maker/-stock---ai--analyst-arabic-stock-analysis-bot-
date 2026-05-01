# 1. إنشاء مجلد جديد
mkdir stock_analyzer_final
cd stock_analyzer_final

# 2. إنشاء الملفات المذكورة أعلاه

# 3. تثبيت المكتبات
pip install -r requirements.txt

# 4. تشغيل التطبيق
streamlit run app.py
# داخل مجلد المشروع
rm -f engines.py intelligence.py scanner.py run_local_scanner.py clock.py bash yaml
rm -rf devcontainer database test
# 1. حذف الملفات المكررة
rm -f engines.py intelligence.py scanner.py run_local_scanner.py clock.py bash yaml
rm -rf devcontainer database test

# 2. تحديث git
git add .
git commit -m "Clean up project structure - remove duplicate files"
git push origin main

# 3. التشغيل محلياً
pip install -r requirements.txt
streamlit run app.py
# منح صلاحية التنفيذ
chmod +x deploy.sh

# تشغيل السكريبت
./deploy.sh

# أو التشغيل المباشر
docker build -t stock-analyzer-pro .
docker run -d -p 8501:8501 --name stock-analyzer-pro stock-analyzer-pro

# عرض السجلات
docker logs stock-analyzer-pro

# إيقاف الحاوية
docker stop stock-analyzer-pro

# بدء الحاوية
docker start stock-analyzer-pro
