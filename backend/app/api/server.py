from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.strategy.engine import strategy_engine, StrategyState
from app.risk.manager import risk_manager
from app.brokers.kis.client import kis_client
from typing import Dict, List

app = FastAPI(title="KAOM Trading System API")

# CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """시스템 시작 시 백그라운드로 전략 엔진 실행"""
    import asyncio
    asyncio.create_task(strategy_engine.run_loop())
    logger.info("KAOM System Started.")

@app.get("/status")
async def get_status():
    return {
        "state": strategy_engine.state.value,
        "is_real_trading": settings.IS_REAL_TRADING,
        "emergency_stop": risk_manager.emergency_stop,
        "daily_loss_limit_hit": risk_manager.daily_loss_limit_hit,
        "api_health": "healthy" # Check logic needed
    }

@app.get("/positions")
async def get_positions():
    return list(strategy_engine.active_positions.values())

@app.post("/emergency-stop")
async def trigger_stop():
    risk_manager.trigger_emergency_stop()
    return {"message": "Emergency Stop Triggered."}

@app.get("/account")
async def get_account_balance():
    # KIS 잔고 조회 API 연동
    return {"balance": 10000000, "withdrawable": 5000000}

import logging
logger = logging.getLogger("uvicorn")
