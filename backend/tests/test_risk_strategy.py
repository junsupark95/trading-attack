import pytest
from app.risk.manager import RiskManager
from app.strategy.engine import KAOMStrategy, StrategyState
from app.core.config import settings

def test_risk_daily_loss_limit():
    rm = RiskManager()
    rm.update_daily_pnl(-5.1) # 5% 한도 초과
    
    violated, reason = rm.check_order_violation(
        symbol="005930",
        order_type="BUY",
        price=70000,
        quantity=10,
        current_positions_count=0,
        per_symbol_pnl_pct=0.0
    )
    assert violated is True
    assert reason == "DAILY_LOSS_LIMIT_EXCEEDED"

def test_risk_max_positions():
    rm = RiskManager()
    # 종목 수 3개 제한 시 (settings.MAX_POSITIONS=3)
    violated, reason = rm.check_order_violation(
        symbol="000660",
        order_type="BUY",
        price=120000,
        quantity=5,
        current_positions_count=3,
        per_symbol_pnl_pct=0.0
    )
    assert violated is True
    assert reason == "MAX_POSITIONS_EXCEEDED"

def test_strategy_state_transition():
    strategy = KAOMStrategy()
    assert strategy.state == StrategyState.IDLE
    
    strategy.transition(StrategyState.SCANNING)
    assert strategy.state == StrategyState.SCANNING

def test_live_trading_protection():
    rm = RiskManager()
    # IS_REAL_TRADING=True 이나 CONFIRM_LIVE_ORDERS=False 인 경우
    # Note: 이 테스트를 위해 settings를 mocking하거나 별도 인스턴스화 필요
    pass 
