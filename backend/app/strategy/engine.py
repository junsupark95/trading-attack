import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from app.core.config import settings
from app.brokers.kis.client import kis_client
from app.risk.manager import risk_manager
from app.ai.scanner import ai_scanner
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class StrategyState(Enum):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    WATCHING = "WATCHING"
    READY_TO_BUY = "READY_TO_BUY"
    BUY_ORDER_SENT = "BUY_ORDER_SENT"
    POSITION_OPEN = "POSITION_OPEN"
    SELL_ORDER_SENT = "SELL_ORDER_SENT"
    CLOSED = "CLOSED"
    HALTED = "HALTED"
    ERROR = "ERROR"

class KAOMStrategy:
    """
    Korean Aggressive Opening Momentum (KAOM) Strategy Core.
    모든 상태 전이는 로그로 기록되며, 리스크 관리자의 승인 없이는 주문이 불가함.
    """
    def __init__(self):
        self.state = StrategyState.IDLE
        self.watchlist: List[str] = []
        self.candidates: Dict[str, Dict] = {} # symbol -> candidate_data
        self.orb_range: Dict[str, Dict] = {}  # symbol -> {high, low}
        self.active_positions: Dict[str, Dict] = {}

    def transition(self, next_state: StrategyState, symbol: Optional[str] = None):
        """구조화된 로그와 함께 상태 전이"""
        old_state = self.state
        self.state = next_state
        logger.info(f"[STATE_TRANSITION] {symbol or 'SYSTEM'}: {old_state.value} -> {next_state.value}")

    async def run_loop(self):
        """주 루프: 시간대별 상태 제어"""
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # 1. 장전 준비 (08:40 ~ 08:59)
            if "08:40" <= current_time < "09:00" and self.state == StrategyState.IDLE:
                self.transition(StrategyState.SCANNING)
                await self.prepare_watchlist()

            # 2. 장초반 관찰 (09:00 ~ 09:05)
            elif "09:00" <= current_time < "09:05" and self.state == StrategyState.SCANNING:
                self.transition(StrategyState.WATCHING)
                await self.set_orb_ranges()

            # 3. 전략 실행 (09:05 ~ 10:30)
            elif settings.ENTRY_WINDOW_START <= current_time < settings.ENTRY_WINDOW_END:
                if self.state in [StrategyState.WATCHING, StrategyState.POSITION_OPEN]:
                    await self.check_signals()

            # 4. 강제 청산 및 종료 준비 (15:10 ~)
            elif current_time >= settings.TIME_EXIT_START:
                await self.handle_eod_exit()
                if current_time >= "15:35":
                    self.transition(StrategyState.IDLE)
                    break
            
            await asyncio.sleep(1) # 1초 주기로 체크 (실제로는 웹소켓 핸들러와 병행)

    async def prepare_watchlist(self):
        """전일 거래대금 상위 + 상승률 상위 종목 스캔 (Simulation)"""
        # 실제 구현에서는 KIS '거래대금순위' API 호출
        logger.info("Scanning for gap-up candidates...")
        # Mock Candidates for Starter
        mock_candidates = ["005930", "000660", "035720"] 
        self.watchlist = mock_candidates
        
        # AI 분석 요청 (상위 3개)
        for symbol in self.watchlist[:settings.AI_CANDIDATE_LIMIT_PER_SCAN]:
            ai_result = await ai_scanner.analyze_candidate(symbol, "MockName", {"gap": 4.5, "vol": 250})
            self.candidates[symbol] = {"ai": ai_result, "state": "WATCHING"}

    async def check_signals(self):
        """ORB 돌파 및 리스크 검증 후 진입"""
        for symbol, data in self.candidates.items():
            if data.get("ai", {}).get("action_bias") != "allow":
                continue
            
            # 시뮬레이션: 현재가가 ORB 고점 돌파 시
            if self.is_orb_breakout(symbol):
                # 리스크 관리자 승인 요청
                violated, reason = risk_manager.check_order_violation(
                    symbol=symbol,
                    order_type="BUY",
                    price=10000, # Mock price
                    quantity=10,
                    current_positions_count=len(self.active_positions),
                    per_symbol_pnl_pct=0.0
                )
                
                if not violated:
                    await self.execute_buy(symbol)
                else:
                    logger.warning(f"Order Blocked for {symbol}: {reason}")

    async def execute_buy(self, symbol: str):
        self.transition(StrategyState.BUY_ORDER_SENT, symbol)
        # KIS 주문 API 호출 로직 (execution_manager에서 처리)
        # ...
        self.active_positions[symbol] = {"entry_price": 10000, "qty": 10}
        self.transition(StrategyState.POSITION_OPEN, symbol)

    def is_orb_breakout(self, symbol: str) -> bool:
        # 5분 ORB 고점 돌파 여부 확인 로직 (Mock)
        return True

    async def handle_eod_exit(self):
        """장마감 전 전량 청산"""
        if self.active_positions:
            logger.info("Market closing soon. Executing EOD exit...")
            for symbol in list(self.active_positions.keys()):
                # Sell orders...
                del self.active_positions[symbol]
                self.transition(StrategyState.CLOSED, symbol)

    async def set_orb_ranges(self):
        """09:00 ~ 09:05 사이의 고가/저가 기록"""
        pass

strategy_engine = KAOMStrategy()
