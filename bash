# ============================================
# الأوامر الكاملة لتشغيل المشروع
# ============================================

# 1. إنشاء المشروع
mkdir egypt-stock-analyst
cd egypt-stock-analyst

# 2. إنشاء مجلد البيانات
mkdir -p data

# 3. إنشاء ملف المتطلبات
cat > requirements.txt << 'EOF'
streamlit>=1.28.0
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
EOF

# 4. تثبيت المكتبات
pip install streamlit yfinance pandas numpy plotly

# 5. إنشاء ملف التطبيق (انسخ كود app.py أعلاه)
# استخدم محرر النصوص لإنشاء الملف

# 6. تشغيل التطبيق
streamlit run app.py

# 7. إذا واجهت مشكلة، جرب التثبيت القسري
pip install --upgrade streamlit yfinance pandas numpy plotly

# 8. تشغيل مع تنظيف الكاش
streamlit run app.py --server.runOnSave false
