"""
عمليات CRUD على قاعدة البيانات
"""

from sqlalchemy.orm import Session
from database.models import User, FavoriteStock, Portfolio, Holding, Transaction, Alert, PriceHistory, StockAnalysis
from datetime import datetime
from typing import List, Optional, Dict
import streamlit as st

# ============= عمليات المستخدم =============
def get_user(db: Session, user_id: int):
    """الحصول على مستخدم"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """الحصول على مستخدم حسب الاسم"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, email: str = None, settings: Dict = None):
    """إنشاء مستخدم جديد"""
    user = User(
        username=username,
        email=email,
        settings=settings or {},
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_settings(db: Session, user_id: int, settings: Dict):
    """تحديث إعدادات المستخدم"""
    user = get_user(db, user_id)
    if user:
        user.settings.update(settings)
        db.commit()
        db.refresh(user)
    return user

# ============= عمليات الأسهم المفضلة =============
def add_favorite_stock(db: Session, user_id: int, ticker: str, notes: str = None):
    """إضافة سهم للمفضلة"""
    # التحقق من عدم التكرار
    existing = db.query(FavoriteStock).filter(
        FavoriteStock.user_id == user_id,
        FavoriteStock.ticker == ticker
    ).first()
    
    if existing:
        return existing
    
    favorite = FavoriteStock(
        user_id=user_id,
        ticker=ticker,
        notes=notes,
        added_at=datetime.now()
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

def remove_favorite_stock(db: Session, user_id: int, ticker: str):
    """حذف سهم من المفضلة"""
    favorite = db.query(FavoriteStock).filter(
        FavoriteStock.user_id == user_id,
        FavoriteStock.ticker == ticker
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
        return True
    return False

def get_favorite_stocks(db: Session, user_id: int):
    """الحصول على قائمة الأسهم المفضلة"""
    return db.query(FavoriteStock).filter(FavoriteStock.user_id == user_id).all()

# ============= عمليات المحفظة =============
def get_or_create_portfolio(db: Session, user_id: int, name: str = "المحفظة الرئيسية"):
    """الحصول على أو إنشاء محفظة"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.name == name
    ).first()
    
    if not portfolio:
        portfolio = Portfolio(
            user_id=user_id,
            name=name,
            cash_balance=100000.0,
            created_at=datetime.now()
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    return portfolio

def add_holding(db: Session, portfolio_id: int, ticker: str, shares: float, price: float):
    """إضافة حيازة جديدة"""
    # التحقق من وجود الحيازة
    holding = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id,
        Holding.ticker == ticker
    ).first()
    
    if holding:
        # تحديث الحيازة الحالية
        total_shares = holding.shares + shares
        total_cost = (holding.shares * holding.avg_price) + (shares * price)
        holding.avg_price = total_cost / total_shares
        holding.shares = total_shares
    else:
        # إنشاء حيازة جديدة
        holding = Holding(
            portfolio_id=portfolio_id,
            ticker=ticker,
            shares=shares,
            avg_price=price,
            bought_at=datetime.now()
        )
        db.add(holding)
    
    # تحديث الرصيد النقدي
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        portfolio.cash_balance -= shares * price
    
    db.commit()
    db.refresh(holding)
    return holding

def remove_holding(db: Session, portfolio_id: int, ticker: str, shares: float, price: float):
    """بيع أسهم من الحيازة"""
    holding = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id,
        Holding.ticker == ticker
    ).first()
    
    if holding and holding.shares >= shares:
        holding.shares -= shares
        
        # تحديث الرصيد النقدي
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio:
            portfolio.cash_balance += shares * price
        
        # حذف الحيازة إذا أصبحت صفراً
        if holding.shares == 0:
            db.delete(holding)
        
        db.commit()
        return True
    
    return False

def get_portfolio_summary(db: Session, user_id: int):
    """الحصول على ملخص المحفظة"""
    portfolio = get_or_create_portfolio(db, user_id)
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    
    summary = {
        'total_cash': portfolio.cash_balance,
        'holdings': [],
        'total_value': portfolio.cash_balance
    }
    
    for holding in holdings:
        summary['holdings'].append({
            'ticker': holding.ticker,
            'shares': holding.shares,
            'avg_price': holding.avg_price,
            'total_cost': holding.shares * holding.avg_price
        })
        summary['total_value'] += holding.shares * holding.avg_price
    
    return summary

# ============= عمليات التنبيهات =============
def create_alert(db: Session, user_id: int, ticker: str, alert_type: str, condition: str, target_value: float):
    """إنشاء تنبيه جديد"""
    alert = Alert(
        user_id=user_id,
        ticker=ticker,
        alert_type=alert_type,
        condition=condition,
        target_value=target_value,
        is_active=True,
        triggered=False,
        created_at=datetime.now()
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def get_active_alerts(db: Session, user_id: int):
    """الحصول على التنبيهات النشطة"""
    return db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_active == True,
        Alert.triggered == False
    ).all()

def trigger_alert(db: Session, alert_id: int):
    """تفعيل تنبيه"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.triggered = True
        alert.triggered_at = datetime.now()
        db.commit()
        return True
    return False

# ============= عمليات التحليل =============
def save_analysis(db: Session, analysis_data: Dict):
    """حفظ تحليل سهم"""
    analysis = StockAnalysis(**analysis_data)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def get_latest_analysis(db: Session, ticker: str):
    """الحصول على آخر تحليل لسهم"""
    return db.query(StockAnalysis).filter(
        StockAnalysis.ticker == ticker
    ).order_by(StockAnalysis.created_at.desc()).first()
