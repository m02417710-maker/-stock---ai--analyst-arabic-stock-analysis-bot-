# 1. انتقل إلى مجلد المشروع (غير المسار حسب موقعك)
cd /path/to/your/project

# 2. احذف الملفات القديمة والمكررة
rm -f engines.py intelligence.py scanner.py run_local_scanner.py clock.py bash yaml

# 3. احذف المجلدات غير المهمة
rm -rf devcontainer database test __pycache__ .streamlit

# 4. احذف الملفات المؤقتة
rm -f *.pyc *.log
