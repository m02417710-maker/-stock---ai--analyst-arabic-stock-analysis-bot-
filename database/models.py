"""
نماذج قاعدة البيانات
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime

class User(Base):
    """نموذج المستخدم"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    telegram_chat_id = Column(String(50), nullable=True)
    telegram_token = Column(String(200), nullable=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # العلاقات
    favorite_stocks = relationship("FavoriteStock", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class FavoriteStock(Base):
    """نموذج الأسهم المفضلة"""
    __tablename__ = "favorite_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    added_at = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="favorite_stocks")

class Portfolio(Base):
    """نموذج المحفظة الاستثمارية"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), default="المحفظة الرئيسية")
    cash_balance = Column(Float, default=100000.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # العلاقات
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")

class Holding(Base):
    """نموذج الحيازات في المحفظة"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    shares = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    bought_at = Column(DateTime, default=datetime.now)
    
    # العلاقات
    portfolio = relationship("Portfolio", back_populates="holdings")

class Transaction(Base):
    """نموذج المعاملات"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    type = Column(String(10), nullable=False)  # BUY or SELL
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="transactions")

class Alert(Base):
    """نموذج التنبيهات"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    alert_type = Column(String(20), nullable=False)  # price, rsi, volume
    condition = Column(String(10), nullable=False)  # above, below, cross
    target_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    triggered_at = Column(DateTime, nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="alerts")

class PriceHistory(Base):
    """نموذج تاريخ الأسعار"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    rsi = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    macd = Column(Float)
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

class StockAnalysis(Base):
    """نموذج تحليلات الأسهم"""
    __tablename__ = "stock_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False)
    analysis_date = Column(DateTime, default=datetime.now)
    recommendation = Column(String(20))
    confidence = Column(Float)
    target_price = Column(Float)
    stop_loss = Column(Float)
    risk_reward_ratio = Column(Float)
    analysis_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
