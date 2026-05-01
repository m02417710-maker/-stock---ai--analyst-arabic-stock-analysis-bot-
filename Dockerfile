# ============================================================
# Dockerfile - الإصدار المحسن للنشر الاحترافي
# ============================================================

# استخدام نسخة نحيفة ومستقرة من بايثون
FROM python:3.10-slim

# منع بايثون من إنشاء ملفات .pyc وتخزين الذاكرة المؤقتة (لتقليل حجم الحاوية)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# تثبيت الأدوات الأساسية للنظام (مهم لبعض مكتبات بايثون العلمية)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# تثبيت المكتبات أولاً للاستفادة من الـ Cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# فتح المنفذ الخاص بـ Streamlit
EXPOSE 8501

# إضافة فحص الحالة (Healthcheck) للتأكد من أن الحاوية تعمل
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# تشغيل التطبيق
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
