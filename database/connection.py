"""
اتصال قاعدة البيانات وإعداداتها
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import streamlit as st
import os
from datetime import datetime
from pathlib import Path

# إنشاء مجلد قاعدة البيانات
DB_PATH = Path("data/stock_analyst.db")
DB_PATH.parent.mkdir(exist_ok=True)

# رابط قاعدة البيانات
DATABASE_URL = f"sqlite:///{DB_PATH}"

# إنشاء المحرك
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# إنشاء جلسة
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# قاعدة النماذج
Base = declarative_base()

def get_db():
    """الحصول على جلسة قاعدة البيانات"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """تهيئة قاعدة البيانات"""
    try:
        # استيراد النماذج هنا لتجنب الـ circular import
        from database.models import User, FavoriteStock, Portfolio, Alert, PriceHistory, Transaction
        
        # إنشاء الجداول
        Base.metadata.create_all(bind=engine)
        
        print(f"✅ قاعدة البيانات تم إنشاؤها بنجاح في: {DB_PATH}")
        
        # إضافة بيانات أولية
        db = SessionLocal()
        try:
            # التحقق من وجود مستخدم افتراضي
            default_user = db.query(User).filter(User.username == "admin").first()
            if not default_user:
                default_user = User(
                    username="admin",
                    email="admin@stockanalyst.com",
                    created_at=datetime.now(),
                    settings={
                        "dark_mode": True,
                        "telegram_alerts": False,
                        "email_alerts": False,
                        "default_period": "6mo"
                    }
                )
                db.add(default_user)
                db.commit()
                print("✅ تم إنشاء المستخدم الافتراضي")
        except Exception as e:
            print(f"⚠️ خطأ في إضافة البيانات الأولية: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    import shutil
    from datetime import datetime
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"stock_analyst_backup_{timestamp}.db"
    
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
        return str(backup_path)
    return None
