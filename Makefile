# =============================================================================
# Makefile - أتمتة أوامر البورصجي AI
# =============================================================================

.PHONY: help build run stop clean logs shell backup test install dev status

# المتغيرات
APP_NAME = boursagi-ai
APP_VERSION = 5.0.0
PORT = 8501
PYTHON = python3
PIP = pip3

# الألوان
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m

help: ## عرض المساعدة
	@echo "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
	@echo "${GREEN}║         البورصجي AI - نظام تحليل الأسهم الذكي            ║${NC}"
	@echo "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
	@echo ""
	@echo "${GREEN}📋 الأوامر المتاحة:${NC}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${BLUE}%-18s${NC} %s\n", $$1, $$2}'
	@echo ""
	@echo "${YELLOW}مثال: make install && make run${NC}"

init: ## تهيئة المشروع (إنشاء المجلدات)
	@echo "${GREEN}📁 تهيئة هيكل المشروع...${NC}"
	@mkdir -p data logs reports cache backups .streamlit
	@mkdir -p output/images output/reports
	@echo "${GREEN}✅ تم إنشاء المجلدات${NC}"

install: ## تثبيت المتطلبات
	@echo "${GREEN}📦 تثبيت المتطلبات...${NC}"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "${GREEN}✅ تم تثبيت جميع المتطلبات${NC}"

install-dev: ## تثبيت متطلبات التطوير
	@echo "${GREEN}🔧 تثبيت متطلبات التطوير...${NC}"
	$(PIP) install -r requirements-dev.txt || true
	@echo "${GREEN}✅ تم التثبيت${NC}"

run: ## تشغيل التطبيق محلياً
	@echo "${GREEN}🚀 تشغيل البورصجي AI...${NC}"
	streamlit run app.py --server.port=$(PORT) --server.address=localhost

run-prod: ## تشغيل للإنتاج
	@echo "${GREEN}🚀 تشغيل للإنتاج...${NC}"
	streamlit run app.py --server.port=$(PORT) --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false

dev: ## تشغيل وضع التطوير (مع إعادة تحميل تلقائي)
	@echo "${GREEN}💻 تشغيل وضع التطوير...${NC}"
	streamlit run app.py --server.port=$(PORT) --server.runOnSave=true

build: ## بناء صورة Docker
	@echo "${GREEN}🔨 بناء صورة Docker...${NC}"
	docker build -t $(APP_NAME):$(APP_VERSION) -t $(APP_NAME):latest .
	@echo "${GREEN}✅ اكتمل البناء${NC}"

docker-run: ## تشغيل الحاوية (Docker)
	@echo "${GREEN}🐳 تشغيل الحاوية...${NC}"
	docker run -d \
		--name $(APP_NAME) \
		-p $(PORT):8501 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/reports:/app/reports \
		-v $(PWD)/cache:/app/cache \
		--restart unless-stopped \
		$(APP_NAME):latest
	@echo "${GREEN}✅ التطبيق يعمل على http://localhost:$(PORT)${NC}"

docker-stop: ## إيقاف الحاوية
	@echo "${YELLOW}🛑 إيقاف الحاوية...${NC}"
	docker stop $(APP_NAME) 2>/dev/null || true
	docker rm $(APP_NAME) 2>/dev/null || true
	@echo "${GREEN}✅ تم الإيقاف${NC}"

docker-restart: docker-stop docker-run ## إعادة تشغيل الحاوية

docker-logs: ## عرض سجلات الحاوية
	docker logs -f $(APP_NAME) 2>/dev/null || echo "${RED}الحاوية غير قيد التشغيل${NC}"

docker-shell: ## الدخول إلى shell الحاوية
	docker exec -it $(APP_NAME) /bin/bash 2>/dev/null || echo "${RED}الحاوية غير قيد التشغيل${NC}"

docker-clean: ## تنظيف Docker
	@echo "${YELLOW}🧹 تنظيف Docker...${NC}"
	docker stop $(APP_NAME) 2>/dev/null || true
	docker rm $(APP_NAME) 2>/dev/null || true
	docker rmi $(APP_NAME):latest 2>/dev/null || true
	docker system prune -f
	@echo "${GREEN}✅ تم التنظيف${NC}"

backup: ## إنشاء نسخة احتياطية
	@echo "${GREEN}💾 إنشاء نسخة احتياطية...${NC}"
	@mkdir -p backups
	@BACKUP_FILE="backups/boursagi_backup_$$(date +%Y%m%d_%H%M%S).tar.gz"
	@tar -czf "$$BACKUP_FILE" data/ logs/ reports/ cache/ .streamlit/ 2>/dev/null || true
	@echo "${GREEN}✅ تم إنشاء: $$BACKUP_FILE${NC}"

restore: ## استعادة نسخة احتياطية (اخر نسخة)
	@echo "${YELLOW}📀 استعادة النسخة الاحتياطية...${NC}"
	@LAST_BACKUP=$$(ls -t backups/*.tar.gz 2>/dev/null | head -1); \
	if [ -n "$$LAST_BACKUP" ]; then \
		tar -xzf "$$LAST_BACKUP"; \
		echo "${GREEN}✅ تم الاستعادة من: $$LAST_BACKUP${NC}"; \
	else \
		echo "${RED}❌ لا توجد نسخ احتياطية${NC}"; \
	fi

status: ## حالة التطبيق
	@echo "${GREEN}📊 حالة التطبيق:${NC}"
	@echo ""
	@echo "${BLUE}🔍 الحاوية:${NC}"
	@docker ps --filter "name=$(APP_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "   Docker غير متاح"
	@echo ""
	@echo "${BLUE}🌐 الوصول:${NC}"
	@curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://localhost:$(PORT) 2>/dev/null || echo "   ⚠️ التطبيق لا يستجيب"
	@echo ""
	@echo "${BLUE}📁 المجلدات:${NC}"
	@for dir in data logs reports cache; do \
		if [ -d "$$dir" ]; then \
			count=$$(ls -1 $$dir 2>/dev/null | wc -l); \
			echo "   📂 $$dir: $$count ملف(ات)"; \
		else \
			echo "   ❌ $$dir: غير موجود"; \
		fi \
	done

clean: ## تنظيف الملفات المؤقتة
	@echo "${YELLOW}🧹 تنظيف الملفات المؤقتة...${NC}"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .coverage 2>/dev/null || true
	@rm -rf cache/* 2>/dev/null || true
	@echo "${GREEN}✅ تم التنظيف${NC}"

full-clean: clean docker-clean ## تنظيف كامل
	@echo "${GREEN}✅ التنظيف الكامل اكتمل${NC}"

test: ## تشغيل الاختبارات
	@echo "${GREEN}🧪 تشغيل الاختبارات...${NC}"
	$(PYTHON) -m pytest tests/ -v --tb=short 2>/dev/null || echo "${YELLOW}⚠️ لا توجد اختبارات${NC}"

scan: ## تشغيل ماسح السوق
	@echo "${GREEN}🔍 تشغيل ماسح السوق...${NC}"
	$(PYTHON) auto_worker.py --scan

report: ## إنشاء تقرير
	@echo "${GREEN}📊 إنشاء تقرير...${NC}"
	$(PYTHON) report_generator.py

update: ## تحديث الأسهم (جلب بيانات جديدة)
	@echo "${GREEN}🔄 تحديث بيانات الأسهم...${NC}"
	$(PYTHON) -c "from market_scanner import MarketScanner; print('جاري التحديث...')"

logs-app: ## عرض سجلات التطبيق
	@tail -f logs/app.log 2>/dev/null || echo "${RED}لا توجد سجلات${NC}"

info: ## عرض معلومات المشروع
	@echo "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
	@echo "${GREEN}║                    معلومات المشروع                        ║${NC}"
	@echo "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
	@echo ""
	@echo "  ${BLUE}الاسم:${NC} $(APP_NAME)"
	@echo "  ${BLUE}الإصدار:${NC} $(APP_VERSION)"
	@echo "  ${BLUE}المنفذ:${NC} $(PORT)"
	@echo "  ${BLUE}Python:${NC} $$($(PYTHON) --version 2>/dev/null || echo 'غير مثبت')"
	@echo "  ${BLUE}المجلد الحالي:${NC} $$(pwd)"
	@echo ""

# =============================================================================
# أوامر سريعة
# =============================================================================
up: install run ## تثبيت وتشغيل (اختصار)

all: init install run ## تهيئة وتثبيت وتشغيل

reset: clean init install run ## إعادة ضبط كاملة

deploy: build docker-run ## بناء ونشر عبر Docker

# =============================================================================
# نهاية الملف
# =============================================================================
