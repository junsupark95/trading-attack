from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 1. KIS API Config (Environment Switch)
    IS_REAL_TRADING: bool = False
    
    # Real Trading (PROD)
    PROD_KIS_APP_KEY: str = ""
    PROD_KIS_APP_SECRET: str = ""
    PROD_KIS_ACCOUNT_NO: str = ""
    
    # Paper Trading (PAPER)
    PAPER_KIS_APP_KEY: str = ""
    PAPER_KIS_APP_SECRET: str = ""
    PAPER_KIS_ACCOUNT_NO: str = ""

    @property
    def KIS_APP_KEY(self) -> str:
        return self.PROD_KIS_APP_KEY if self.IS_REAL_TRADING else self.PAPER_KIS_APP_KEY

    @property
    def KIS_APP_SECRET(self) -> str:
        return self.PROD_KIS_APP_SECRET if self.IS_REAL_TRADING else self.PAPER_KIS_APP_SECRET

    @property
    def KIS_ACCOUNT_NO(self) -> str:
        return self.PROD_KIS_ACCOUNT_NO if self.IS_REAL_TRADING else self.PAPER_KIS_ACCOUNT_NO
    
    # 2. AI Config (Gemini 2.5 Flash Lite)
    GEMINI_API_KEY: str
    AI_SCAN_LIMIT_PER_DAY: int = 500
    AI_CANDIDATE_LIMIT_PER_SCAN: int = 3
    
    # 3. Strategy Config (KAOM)
    STRATEGY_ID: str = "KAOM_V1"
    MAX_POSITIONS: int = 3
    DAILY_LOSS_LIMIT_PCT: float = 5.0
    SYMBOL_LOSS_LIMIT_PCT: float = 2.0
    ENTRY_WINDOW_START: str = "09:05"
    ENTRY_WINDOW_END: str = "10:30"
    TIME_EXIT_START: str = "15:10"
    
    # 4. DB Config
    DATABASE_URL: str  # Supabase or PostgreSQL URL
    
    # 5. Operational Safety
    CONFIRM_LIVE_ORDERS: bool = False  # 실전 주문 명시적 승인 여부
    EMERGENCY_STOP: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
