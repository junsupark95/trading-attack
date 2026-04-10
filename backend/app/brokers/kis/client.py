import asyncio
import time
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """KIS API Rate Limiter to prevent 429 Too Many Requests."""
    def __init__(self, requests_per_sec: float):
        self.delay = 1.0 / requests_per_sec
        self.last_call = 0.0

    async def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_call = time.time()

class KISClient:
    """
    한국투자증권 Open API Client (REST + WebSocket)
    
    [공식 문서 확인 포인트]
    - 인증(토큰): https://apiportal.koreainvestment.com/apis/oauth2/token
    - 인증(해시키): https://apiportal.koreainvestment.com/apis/oauth2/hashkey
    - 인증(웹소켓): https://apiportal.koreainvestment.com/apis/oauth2/websocket
    - 호출제한(Rate Limit): 실전 20회/초, 모의 2회/초 (보수적 운영 권장)
    """
    def __init__(self):
        self.base_url = (
            "https://openapi.koreainvestment.com:9443" 
            if settings.IS_REAL_TRADING else 
            "https://openapivts.koreainvestment.com:29443"
        )
        self.ws_url = (
            "ws://ops.koreainvestment.com:21000" 
            if settings.IS_REAL_TRADING else 
            "ws://ops.koreainvestment.com:31000"
        )
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        # 모의투자 기준(2건/s)보다 보수적인 1.5건/s 설정
        self.limiter = RateLimiter(1.5 if not settings.IS_REAL_TRADING else 15)

    async def get_access_token(self) -> str:
        """액세스 토큰 발급 및 자동 갱신"""
        if self.access_token and time.time() < self.token_expiry - 600:
            return self.access_token

        url = f"{self.base_url}/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": settings.KIS_APP_KEY,
            "secretkey": settings.KIS_APP_SECRET
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            data = resp.json()
            if resp.status_code == 200:
                self.access_token = data["access_token"]
                # 유효시간(seconds) 반영, 여유있게 1시간 차감
                self.token_expiry = time.time() + int(data["expires_in"])
                logger.info("KIS Access Token refreshed successfully.")
                return self.access_token
            else:
                logger.error(f"Failed to get KIS token: {data}")
                raise Exception("Authentication Failed")

    async def _get_headers(self, tr_id: str, continuous: bool = False) -> Dict[str, str]:
        token = await self.get_access_token()
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": settings.KIS_APP_KEY,
            "appsecret": settings.KIS_APP_SECRET,
            "tr_id": tr_id,
        }
        if settings.IS_REAL_TRADING:
            headers["custtype"] = "P" # 개인
        return headers

    async def get_hashkey(self, body: Dict[str, Any]) -> str:
        """
        [공식 가이드] POST 요청 시 데이터 무결성 검증을 위한 Hashkey 발급
        URL: /uapi/hashkey
        """
        url = f"{self.base_url}/uapi/hashkey"
        headers = {
            "content-type": "application/json",
            "appkey": settings.KIS_APP_KEY,
            "appsecret": settings.KIS_APP_SECRET,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            return resp.json()["HASH"]

    async def request(self, method: str, path: str, tr_id: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generic REST request with rate limiting and hashkey support"""
        await self.limiter.wait()
        url = f"{self.base_url}{path}"
        headers = await self._get_headers(tr_id)
        
        # POST/PUT 요청 시 공식 문서에 따라 Hashkey 필수 포함
        if method.upper() in ["POST", "PUT"] and json_data:
            headers["hashkey"] = await self.get_hashkey(json_data)
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    resp = await client.get(url, headers=headers, params=params)
                else:
                    resp = await client.post(url, headers=headers, json=json_data)
                
                resp.raise_for_status()
                data = resp.json()
                
                # KIS 특정 에러 코드 처리 가능 (RT_CD != '0')
                if data.get("rt_cd") and data.get("rt_cd") != "0":
                    logger.warning(f"KIS API Error [{tr_id}]: {data.get('msg1')}")
                
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
                if e.response.status_code == 429:
                    await asyncio.sleep(1) # Backoff
                raise

    async def get_approval_key(self) -> str:
        """
        웹소켓 접속을 위한 approval_key 발급
        [확인포인트] https://apiportal.koreainvestment.com/apis/oauth2/websocket
        """
        url = f"{self.base_url}/oauth2/Approval"
        payload = {
            "grant_type": "client_credentials",
            "appkey": settings.KIS_APP_KEY,
            "secretkey": settings.KIS_APP_SECRET
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()["approval_key"]

kis_client = KISClient()
