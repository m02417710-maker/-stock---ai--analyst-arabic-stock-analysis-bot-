# =============================================================================
# Makefile - أتمتة أوامر البورصجي AI
# =============================================================================

.PHONY: help build run stop clean logs shell backup test

# المتغيرات
APP_NAME = boursagi-ai
APP_VERSION = 5.0.0
PORT = 8501

# الألوان
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

help: ## عرض المساعدة
	@echo "${GREEN}البورصجي AI - الأوامر المتاحة:${NC}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}'
	@echo ""

build: ## بناء صورة Docker
	@echo "${GREEN}🔨 بناء صورة Docker...${NC}"
	docker build -t $(APP_NAME):$(APP_VERSION) .
	docker tag $(APP_NAME):$(APP_VERSION) $(APP_NAME):latest
	@echo "${GREEN}✅ اكتمل البناء${NC}"

run: ## تشغيل الحاوية
	@echo "${GREEN}🚀 تشغيل الحاوية...${NC}"
	docker run -d \
		--name $(APP_NAME) \
		-p $(PORT):8501 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/reports:/app/reports \
		--restart unless-stopped \
		$(APP_NAME):latest
	@echo "${GREEN}✅ التطبيق يعمل على http://localhost:$(PORT)${NC}"

stop: ## إيقاف الحاوية
	@echo "${YELLOW}🛑 إيقاف الحاوية...${NC}"
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true
	@echo "${GREEN}✅ تم الإيقاف${NC}"

restart: stop run ## إعادة تشغيل الحاوية

logs: ## عرض سجلات الحاوية
	docker logs -f $(APP_NAME)

shell: ## الدخول إلى shell الحاوية
	docker exec -it $(APP_NAME) /bin/bash

clean: ## تنظيف Docker
	@echo "${YELLOW}🧹 تنظيف...${NC}"
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true
	docker rmi $(APP_NAME):latest || true
	docker system prune -f
	@echo "${GREEN}✅ تم التنظيف${NC}"

backup: ## إنشاء نسخة احتياطية
	@echo "${GREEN}💾 إنشاء نسخة احتياطية...${NC}"
	@mkdir -p backups
	@tar -czf "backups/boursagi_backup_$$(date +%Y%m%d_%H%M%S).tar.gz" data/ logs/ reports/ .streamlit/ 2>/dev/null || true
	@echo "${GREEN}✅ تم إنشاء النسخة الاحتياطية${NC}"

up: build run ## بناء وتشغيل (اختصار)

status: ## حالة التطبيق
	@echo "${GREEN}📊 حالة التطبيق:${NC}"
	@docker ps --filter "name=$(APP_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@curl -s -o /dev/null -w "🌐 الوصول: %{http_code}\n" http://localhost:$(PORT) || echo "⚠️ التطبيق لا يستجيب"
