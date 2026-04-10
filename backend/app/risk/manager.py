from typing import Dict, Optional, Tuple
from app.core.config import settings
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskState(Enum):
    SAFE = "SAFE"
    BLOCKED = "BLOCKED"
    HALTED = "HALTED"

class RiskManager:
    """
    고정 안전 레일 (Safety Rails) 구현 모듈.
    어떤 전략 신호도 이 모듈의 하드 룰을 우회할 수 없음.
    """
    def __init__(self):
        self.emergency_stop = settings.EMERGENCY_STOP
        self.daily_loss_limit_hit = False
        self.current_daily_pnl_pct = 0.0

    def check_order_violation(self, 
                               symbol: str, 
                               order_type: str, 
                               price: int, 
                               quantity: int,
                               current_positions_count: int,
                               per_symbol_pnl_pct: float) -> Tuple[bool, Optional[str]]:
        """
        주문 전 최종 리스크 검사.
        Returns: (is_violated, reason)
        """
        # 1. 긴급 정지 플래그 확인
        if self.emergency_stop:
            return True, "EMERGENCY_STOP_ACTIVE"

        # 2. 일일 손실 한도 확인
        if self.daily_loss_limit_hit:
            return True, "DAILY_LOSS_LIMIT_EXCEEDED"

        # 3. 최대 동시 보유 종목 수 제한
        if order_type == "BUY" and current_positions_count >= settings.MAX_POSITIONS:
            return True, "MAX_POSITIONS_EXCEEDED"

        # 4. 종목당 손실 한도 확인 (진입 후 감시용이지만 주문 레벨에서도 체크)
        if per_symbol_pnl_pct <= -settings.SYMBOL_LOSS_LIMIT_PCT:
            return True, "SYMBOL_LOSS_LIMIT_REACHED"

        # 5. 실전 주문 명시적 승인 확인 (Safety Switch)
        if settings.IS_REAL_TRADING and not settings.CONFIRM_LIVE_ORDERS:
            return True, "LIVE_ORDER_PROTECTION_ENABLED"

        return False, None

    def update_daily_pnl(self, total_pnl_pct: float):
        """일일 PnL 업데이트 및 한도 초과 시 락업"""
        self.current_daily_pnl_pct = total_pnl_pct
        if total_pnl_pct <= -settings.DAILY_LOSS_LIMIT_PCT:
            self.daily_loss_limit_hit = True
            logger.critical(f"DAILY LOSS LIMIT HIT: {total_pnl_pct}%. SYSTEM HALTED.")

    def trigger_emergency_stop(self):
        self.emergency_stop = True
        logger.warning("EMERGENCY STOP TRIGGERED EXTERNALLY.")

risk_manager = RiskManager()
