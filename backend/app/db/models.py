from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class WatchlistSnapshot(Base):
    """장전/장중 스캔된 후보 종목 스냅샷"""
    __tablename__ = 'watchlist_snapshots'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, index=True)
    name = Column(String)
    gap_pct = Column(Float)
    avg_volume = Column(Integer)
    ai_bias = Column(String) # allow, watch, avoid
    ai_commentary = Column(String)
    raw_data = Column(JSON)

class Order(Base):
    """주문 기록"""
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, index=True)
    order_type = Column(String) # BUY, SELL
    price = Column(Integer)
    quantity = Column(Integer)
    status = Column(String) # PENDING, FILLED, CANCELLED, REJECTED
    kis_ord_no = Column(String, unique=True) # KIS 주문번호
    strategy_id = Column(String)

class Position(Base):
    """현재 보유 포지션 (실시간 인벤토리)"""
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True)
    entry_price = Column(Float)
    quantity = Column(Integer)
    current_price = Column(Float)
    pnl_pct = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyPnL(Base):
    """일별 성과 기록"""
    __tablename__ = 'daily_pnl'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    total_pnl_amt = Column(Integer)
    total_pnl_pct = Column(Float)
    trade_count = Column(Integer)
    win_rate = Column(Float)

class RiskEvent(Base):
    """리스크 위반 또는 특이사항 기록"""
    __tablename__ = 'risk_events'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String) # DAILY_LOSS_LIMIT, VI_BLOCK, EMERGENCY_STOP
    symbol = Column(Optional(String))
    reason = Column(String)
    severity = Column(String) # INFO, WARNING, CRITICAL
