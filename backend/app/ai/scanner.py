import google.generativeai as genai
from app.core.config import settings
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class AIScanner:
    """
    Gemini 2.5 Flash Lite 기반 종목 분석기.
    공격형 전략의 필터링 보조 역할을 수행하며, 주문 결정권은 없음.
    """
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite') # Latest Flash Lite
        self.system_prompt = """
        당신은 대한민국 주식시장의 시니어 퀀트 분석가입니다. 
        제공된 종목 정보를 바탕으로 '장초반 모멘텀' 전략에 적합한지 분석하십시오.
        응답은 반드시 아래 JSON 스키마를 엄격히 따라야 합니다. 다른 텍스트는 포함하지 마십시오.
        {
          "symbol": "string",
          "action_bias": "allow|watch|avoid",
          "entry_score": 0.0 to 10.0,
          "risk_flags": ["string"],
          "reason_codes": ["string"],
          "commentary": "string"
        }
        """

    async def analyze_candidate(self, symbol: str, name: str, snapshot_data: Dict[str, Any]) -> Dict[str, Any]:
        """단일 종목 심층 분석"""
        prompt = f"""
        종목명: {name} ({symbol})
        데이터 스냅샷: {json.dumps(snapshot_data, ensure_ascii=False)}
        
        최근 뉴스/공시와 호가 잔량, 거래대금을 고려할 때 추격 매수의 위험이 있는지, 
        혹은 강력한 테마의 대장주인지 판단하여 action_bias를 결정하십시오.
        """
        
        try:
            # Note: genai library is typically synchronous or has specific async wrappers.
            # Using synchronous call for simplicity in this starter, wrapper recommended.
            response = self.model.generate_content([self.system_prompt, prompt])
            
            # JSON 클린업 및 파싱
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(text)
            logger.info(f"AI Analysis for {symbol}: {result.get('action_bias')} (Score: {result.get('entry_score')})")
            return result
        except Exception as e:
            logger.error(f"AI Analysis Failed for {symbol}: {str(e)}")
            # AI 장애 시 'watch' 단계로 안전하게 반환하여 규칙 엔진만 작동하게 함
            return {
                "symbol": symbol,
                "action_bias": "watch",
                "entry_score": 0.0,
                "risk_flags": ["AI_ERROR"],
                "reason_codes": ["SYSTEM_FAILURE"],
                "commentary": "AI 분석 실패. 규칙 기반 엔진만 활용하십시오."
            }

ai_scanner = AIScanner()
