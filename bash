#!/bin/bash

# =============================================================================
# البورصجي AI - منصة التداول الذكية
# Bash Script للتشغيل الآلي وإدارة البيئة
# الإصدار: 5.0.0
# =============================================================================

# الألوان للإخراج الجميل
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# =============================================================================
# دوال مساعدة
# =============================================================================

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                    ║"
    echo "║     🧠  البورصجي AI - منصة التداول الذكية  🧠                      ║"
    echo "║                  العقل المدبر لإدارة المخاطر                       ║"
    echo "║                                                                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_step() {
    echo -e "${MAGENTA}📌 $1${NC}"
}

# =============================================================================
# التحقق من وجود Python
# =============================================================================

check_python() {
    print_step "التحقق من تثبيت Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python موجود: $PYTHON_VERSION"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version)
        print_success "Python موجود: $PYTHON_VERSION"
        return 0
    else
        print_error "Python غير مثبت. يرجى تثبيت Python 3.8 أو أحدث"
        exit 1
    fi
}

# =============================================================================
# إنشاء البيئة الافتراضية
# =============================================================================

setup_venv() {
    print_step "إعداد البيئة الافتراضية..."
    
    if [ ! -d "venv" ]; then
        print_info "إنشاء بيئة افتراضية جديدة..."
        python3 -m venv venv
        print_success "تم إنشاء البيئة الافتراضية"
    else
        print_success "البيئة الافتراضية موجودة بالفعل"
    fi
    
    # تفعيل البيئة الافتراضية
    source venv/bin/activate
    print_success "تم تفعيل البيئة الافتراضية"
}

# =============================================================================
# تثبيت المتطلبات
# =============================================================================

install_requirements() {
    print_step "تثبيت المتطلبات..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "تم تثبيت جميع المتطلبات"
    else
        print_warning "ملف requirements.txt غير موجود، يتم إنشاؤه..."
        cat > requirements.txt << EOF
streamlit==1.32.0
yfinance==0.2.38
pandas==2.2.1
plotly==5.19.0
numpy==1.26.4
requests==2.31.0
EOF
        pip install -r requirements.txt
        print_success "تم تثبيت المتطلبات"
    fi
}

# =============================================================================
# إنشاء المجلدات اللازمة
# =============================================================================

create_directories() {
    print_step "إنشاء المجلدات اللازمة..."
    
    mkdir -p data
    mkdir -p logs
    mkdir -p reports
    mkdir -p .streamlit
    
    print_success "تم إنشاء المجلدات"
}

# =============================================================================
# إعداد ملفات التهيئة
# =============================================================================

setup_config_files() {
    print_step "إعداد ملفات التهيئة..."
    
    # إعداد config.py إذا لم يكن موجوداً
    if [ ! -f "config.py" ]; then
        print_info "إنشاء ملف config.py..."
        cat > config.py << 'EOF'
# config.py - الإعدادات المركزية
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

for dir_path in [DATA_DIR, LOGS_DIR, REPORTS_DIR]:
    dir_path.mkdir(exist_ok=True)

APP_CONFIG = {
    "name": "البورصجي AI",
    "version": "5.0.0",
    "description": "منصة التداول الذكية المتكاملة",
    "default_period": "1y",
    "refresh_seconds": 60
}

RISK_CONFIG = {
    "default_risk_percent": 2.0,
    "min_risk_reward_ratio": 1.5,
    "trailing_stop_default": 5.0
}
EOF
        print_success "تم إنشاء config.py"
    fi
    
    # إعداد secrets.toml إذا لم يكن موجوداً
    if [ ! -f ".streamlit/secrets.toml" ]; then
        print_info "إنشاء ملف secrets.toml..."
        cat > .streamlit/secrets.toml << EOF
# مفاتيح API - يرجى إضافة مفاتيحك الخاصة
# GEMINI_API_KEY = "your_key_here"
# TELEGRAM_BOT_TOKEN = "your_token_here"
# TELEGRAM_CHAT_ID = "your_chat_id_here"
EOF
        print_success "تم إنشاء .streamlit/secrets.toml"
        print_warning "يرجى إضافة مفاتيح API الخاصة بك في .streamlit/secrets.toml"
    fi
}

# =============================================================================
# تشغيل التطبيق
# =============================================================================

run_app() {
    print_step "تشغيل البورصجي AI..."
    
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 جاري تشغيل المنصة... 🚀                       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0
}

# =============================================================================
# التحديث الآلي للأسعار (وضع الخلفية)
# =============================================================================

run_scanner() {
    print_step "تشغيل الماسح الآلي..."
    
    while true; do
        echo -e "${BLUE}🔄 ${NC}جاري مسح الأسواق... $(date '+%Y-%m-%d %H:%M:%S')"
        
        # تشغيل الماسح عبر Python
        python3 -c "
import yfinance as yf
import pandas as pd

stocks = ['COMI.CA', 'TMGH.CA', 'SWDY.CA', 'AAPL', 'MSFT', 'NVDA']
results = []
for ticker in stocks:
    try:
        df = yf.Ticker(ticker).history(period='2mo')
        if not df.empty:
            current = df['Close'].iloc[-1]
            results.append(f'{ticker}: {current:.2f}')
    except:
        pass
print(' | '.join(results))
"
        
        sleep 300  # انتظار 5 دقائق
    done
}

# =============================================================================
# عرض حالة النظام
# =============================================================================

show_status() {
    print_step "حالة النظام:"
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # عدد الصفقات
    if [ -f "data/boursagi.db" ]; then
        TRADES_COUNT=$(sqlite3 data/boursagi.db "SELECT COUNT(*) FROM trades;" 2>/dev/null || echo "0")
        echo -e "📊 عدد الصفقات: ${GREEN}${TRADES_COUNT}${NC}"
    else
        echo -e "📊 عدد الصفقات: ${YELLOW}0${NC}"
    fi
    
    # حالة البيئة
    if [ -d "venv" ]; then
        echo -e "🐍 البيئة الافتراضية: ${GREEN}موجودة✓${NC}"
    else
        echo -e "🐍 البيئة الافتراضية: ${RED}غير موجودة✗${NC}"
    fi
    
    # حالة المجلدات
    for dir in data logs reports; do
        if [ -d "$dir" ]; then
            echo -e "📁 مجلد $dir: ${GREEN}موجود✓${NC}"
        else
            echo -e "📁 مجلد $dir: ${RED}غير موجود✗${NC}"
        fi
    done
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# =============================================================================
# النسخ الاحتياطي للبيانات
# =============================================================================

backup_data() {
    print_step "إنشاء نسخة احتياطية..."
    
    BACKUP_DIR="backups_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "data/boursagi.db" ]; then
        cp data/boursagi.db "$BACKUP_DIR/"
        print_success "تم نسخ قاعدة البيانات"
    fi
    
    if [ -f ".streamlit/secrets.toml" ]; then
        cp .streamlit/secrets.toml "$BACKUP_DIR/"
        print_success "تم نسخ ملف secrets"
    fi
    
    tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
    rm -rf "$BACKUP_DIR"
    
    print_success "تم إنشاء النسخة الاحتياطية: ${BACKUP_DIR}.tar.gz"
}

# =============================================================================
# تنظيف الملفات المؤقتة
# =============================================================================

cleanup() {
    print_step "تنظيف الملفات المؤقتة..."
    
    # حذف ملفات Python المؤقتة
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete 2>/dev/null
    
    # حذف مجلدات cache
    rm -rf .cache 2>/dev/null
    rm -rf __pycache__ 2>/dev/null
    
    print_success "تم التنظيف"
}

# =============================================================================
# تثبيت التطبيق كخدمة (Systemd)
# =============================================================================

install_service() {
    print_step "تثبيت التطبيق كخدمة..."
    
    SERVICE_FILE="/etc/systemd/system/boursagi.service"
    
    if [ "$EUID" -ne 0 ]; then
        print_error "هذا الأمر يتطلب صلاحيات الجذر (sudo)"
        exit 1
    fi
    
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(who am i | awk '{print $1}')
    
    cat > $SERVICE_FILE << EOF
[Unit]
Description=البورصجي AI - منصة التداول الذكية
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    print_success "تم تثبيت الخدمة"
    print_info "لتشغيل الخدمة: sudo systemctl start boursagi"
    print_info "لتمكين التشغيل التلقائي: sudo systemctl enable boursagi"
}

# =============================================================================
# عرض المساعدة
# =============================================================================

show_help() {
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                    🧠 البورصجي AI - المساعدة 🧠                      ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${GREEN}الاستخدام:${NC}"
    echo "  ./run.sh [command]"
    echo ""
    echo -e "${GREEN}الأوامر المتاحة:${NC}"
    echo "  (بدون أمر)    - تشغيل التطبيق"
    echo "  start         - تشغيل التطبيق"
    echo "  install       - تثبيت المتطلبات وإعداد البيئة"
    echo "  status        - عرض حالة النظام"
    echo "  backup        - إنشاء نسخة احتياطية"
    echo "  cleanup       - تنظيف الملفات المؤقتة"
    echo "  service       - تثبيت التطبيق كخدمة نظام"
    echo "  scanner       - تشغيل الماسح الآلي فقط"
    echo "  help          - عرض هذه المساعدة"
    echo ""
    echo -e "${GREEN}أمثلة:${NC}"
    echo "  ./run.sh install    # التثبيت الأول"
    echo "  ./run.sh start      # تشغيل التطبيق"
    echo "  ./run.sh backup     # نسخ احتياطي"
    echo "  ./run.sh status     # حالة النظام"
}

# =============================================================================
# التثبيت الكامل
# =============================================================================

full_install() {
    print_header
    print_info "بدء التثبيت الكامل للبورصجي AI..."
    echo ""
    
    check_python
    setup_venv
    install_requirements
    create_directories
    setup_config_files
    
    echo ""
    print_success "اكتمل التثبيت بنجاح!"
    echo ""
    print_info "لتشغيل التطبيق: ./run.sh start"
}

# =============================================================================
# الدالة الرئيسية
# =============================================================================

main() {
    case "${1:-start}" in
        start|run|""
# =============================================================================
# بناء الصورة
# =============================================================================

# بناء الصورة الأساسية
docker build -t boursagi-ai:latest .

# بناء الصورة بدون cache
docker build --no-cache -t boursagi-ai:latest .

# بناء الصورة مع اسم محدد
docker build -t boursagi-ai:v5.0.0 .

# =============================================================================
# تشغيل الحاوية
# =============================================================================

# التشغيل الأساسي
docker run -d \
  --name boursagi-ai \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  boursagi-ai:latest

# التشغيل مع متغيرات البيئة
docker run -d \
  --name boursagi-ai \
  -p 8501:8501 \
  -e TZ=Africa/Cairo \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.streamlit:/app/.streamlit \
  --restart unless-stopped \
  boursagi-ai:latest

# =============================================================================
# تشغيل باستخدام Docker Compose
# =============================================================================

# التشغيل الأساسي
docker-compose up -d

# التشغيل مع إعادة البناء
docker-compose up -d --build

# التشغيل مع الميزات المتقدمة (PostgreSQL + Redis)
docker-compose --profile advanced up -d

# إيقاف الخدمات
docker-compose down

# إيقاف وإزالة وحدات التخزين
docker-compose down -v

# عرض السجلات
docker-compose logs -f boursagi-app

# =============================================================================
# إدارة الحاويات
# =============================================================================

# عرض الحاويات العاملة
docker ps

# عرض جميع الحاويات
docker ps -a

# إيقاف الحاوية
docker stop boursagi-ai

# تشغيل الحاوية المتوقفة
docker start boursagi-ai

# إعادة تشغيل الحاوية
docker restart boursagi-ai

# الدخول إلى الحاوية
docker exec -it boursagi-ai /bin/bash

# عرض سجلات الحاوية
docker logs boursagi-ai

# متابعة السجلات الحية
docker logs -f boursagi-ai

# =============================================================================
# تنظيف Docker
# =============================================================================

# حذف الحاوية
docker rm boursagi-ai

# حذف الصورة
docker rmi boursagi-ai:latest

# حذف الحاويات غير المستخدمة
docker container prune

# حذف الصور غير المستخدمة
docker image prune

# تنظيف شامل
docker system prune -a --volumes
# 1. بناء الصورة
docker build -t boursagi-ai .

# 2. تشغيل الحاوية
docker run -d -p 8501:8501 --name boursagi-ai boursagi-ai

# 3. فتح المتصفح
open http://localhost:8501
