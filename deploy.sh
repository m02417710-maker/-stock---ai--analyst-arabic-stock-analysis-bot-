#!/bin/bash
# ============================================================
# deploy.sh - سكريبت نشر التطبيق
# ============================================================

echo "🚀 بدء نشر تطبيق المحلل المالي..."

# بناء الحاوية
echo "📦 بناء حاوية Docker..."
docker build -t stock-analyzer-pro .

# إيقاف الحاوية القديمة إن وجدت
echo "🛑 إيقاف الحاوية القديمة..."
docker stop stock-analyzer-pro 2>/dev/null || true
docker rm stock-analyzer-pro 2>/dev/null || true

# تشغيل الحاوية الجديدة
echo "▶️ تشغيل الحاوية..."
docker run -d \
    --name stock-analyzer-pro \
    -p 8501:8501 \
    --restart unless-stopped \
    stock-analyzer-pro

echo "✅ تم النشر بنجاح!"
echo "🌐 افتح المتصفح على: http://localhost:8501"
