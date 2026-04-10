from typing import Dict, Optional
import uuid
from app.brokers.kis.client import kis_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ExecutionManager:
    """
    주문 집행 및 체결 추적 모듈.
    중복 주문 방지(Deduplication)와 미체결 관리를 담당함.
    """
    def __init__(self):
        self.order_history: Dict[str, Dict] = {} # strategy_id -> order_details
        self.unfilled_orders: Dict[str, Dict] = {} # kis_ord_no -> details

    async def submit_order(self, symbol: str, order_type: str, qty: int, price: int = 0) -> Optional[str]:
        """
        주문 제출.
        idempotency_key를 생성하여 중복 제출 방지.
        """
        idempotency_key = f"{settings.STRATEGY_ID}_{symbol}_{order_type}_{uuid.uuid4().hex[:8]}"
        
        # 1. 중복 체크
        if idempotency_key in self.order_history:
            logger.warning(f"Duplicate order detected: {idempotency_key}")
            return None

        # 2. 실전 주문 최종 보호 스위치
        if settings.IS_REAL_TRADING and not settings.CONFIRM_LIVE_ORDERS:
            logger.critical("FORBIDDEN: Real trading attempted without explicit confirmation.")
            return None

        # KIS 주문 API (v2 신규 TR ID 적용)
        # [공식 문서 확인포인트] 
        # 실전: https://apiportal.koreainvestment.com/apis/domestic-stock/stock-order (TTTC0012U / TTTC0001U)
        # 모의: https://apiportal.koreainvestment.com/apis/domestic-stock/stock-order-virtual (VTTC0012U / VTTC0001U)
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        tr_id = "TTTC0012U" if settings.IS_REAL_TRADING else "VTTC0012U" # 매수 (신규)
        if order_type == "SELL":
            tr_id = "TTTC0001U" if settings.IS_REAL_TRADING else "VTTC0001U" # 매도 (신규)

        payload = {
            "CANO": settings.KIS_ACCOUNT_NO[:8],
            "ACNT_PRDT_CD": settings.KIS_ACCOUNT_NO[8:],
            "PDNO": symbol,
            "ORD_DVSN": "01", # 01: 시장가, 00: 지정가
            "ORD_QTY": str(qty),
            "ORD_UNPR": str(price) if price > 0 else "0",
        }

        try:
            resp = await kis_client.request("POST", path, tr_id, json_data=payload)
            if resp.get("rt_cd") == "0":
                ord_no = resp["output"]["ODNO"]
                self.order_history[idempotency_key] = resp
                logger.info(f"Order Succeed: {symbol} {order_type} {qty} (No: {ord_no})")
                return ord_no
            else:
                logger.error(f"Order Failed: {resp.get('msg1')}")
                return None
        except Exception as e:
            logger.error(f"Execution Error: {str(e)}")
            return None

    async def cancel_all_unfilled(self):
        """장마감 전 미체결 주문 일괄 취소"""
        # KIS 취소 API 연동 로직
        pass

execution_manager = ExecutionManager()
