# =============================================================================
# البورصجي AI - منصة التداول الذكية
# Dockerfile - الإصدار النهائي المتكامل
# =============================================================================

# ==== المرحلة 1: بناء الصورة الأساسية ====
FROM python:3.11-slim AS builder

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# تثبيت الاعتماديات الأساسية للنظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات أولاً (للاستفادة من الـ Cache)
COPY requirements.txt .

# تثبيت متطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# ==== المرحلة 2: الصورة النهائية ====
FROM python:3.11-slim

# تعيين متغيرات البيئة للتشغيل
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10

# تثبيت الاعتماديات الأساسية فقط
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash boursagi

# إنشاء مجلدات التطبيق
WORKDIR /app

# نسخ التبعيات من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# نسخ ملفات المشروع
COPY . .

# إنشاء المجلدات اللازمة
RUN mkdir -p /app/data \
    /app/logs \
    /app/reports \
    /app/cache \
    /app/.streamlit \
    && chown -R boursagi:boursagi /app

# إعداد ملف تكوين Streamlit
RUN echo "\
[server]\n\
port = 8501\n\
address = \"0.0.0.0\"\n\
maxUploadSize = 10\n\
enableCORS = true\n\
enableXsrfProtection = true\n\
\n\
[theme]\n\
base = \"dark\"\n\
primaryColor = \"#00ffcc\"\n\
backgroundColor = \"#0e1117\"\n\
secondaryBackgroundColor = \"#262730\"\n\
textColor = \"#fafafa\"\n\
font = \"sans serif\"\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > /app/.streamlit/config.toml

# إعداد ملف إدخال (entrypoint)
RUN echo '#!/bin/bash\n\
echo "╔════════════════════════════════════════════════════════════════════╗"\n\
echo "║                    🧠 البورصجي AI - منصة التداول الذكية 🧠          ║"\n\
echo "║                    العقل المدبر لإدارة المخاطر                      ║"\n\
echo "╚════════════════════════════════════════════════════════════════════╝"\n\
echo ""\n\
echo "📅 التاريخ: $(date)"\n\
echo "🐍 Python: $(python --version)"\n\
echo "📊 Streamlit: $(streamlit --version)"\n\
echo ""\n\
echo "🚀 جاري تشغيل المنصة..."\n\
echo "🌐 الوصول عبر: http://localhost:8501"\n\
echo ""\n\
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# تغيير مالك الملفات
RUN chown -R boursagi:boursagi /app
USER boursagi

# فتح المنفذ
EXPOSE 8501

# نقطة الدخول
ENTRYPOINT ["/app/entrypoint.sh"]
