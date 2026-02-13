from groq import Groq
from app.config import settings
import logging
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AIUsageLog, User, Match
import asyncio
import time

logger = logging.getLogger(__name__)

class AIService:
    """Service for Groq/Llama integration"""
    
    def __init__(self):
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def get_match_suggestion(
        self,
        match: Match,
        user_history: Dict = None,
        style: str = "balanced",
        db: Session = None,
        user_id: int = None,
        ip_address: str = None,
    ) -> Optional[Dict]:
        """Get AI suggestion for a match score"""
        if not self.is_available():
            logger.warning("AI service not available - GROQ_API_KEY not set")
            return None
        
        try:
            # Build context
            prompt = self._build_prompt(match, user_history, style)
            
            # Call Groq
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a World Cup prediction assistant using historical data and statistics. 
                        Always provide predictions in JSON format: {
                            "home_score": int (0-8),
                            "away_score": int (0-8),
                            "confidence": float (0.0-1.0),
                            "reasoning": "brief explanation in Portuguese",
                            "alternatives": [{"score": "X-Y", "probability": 0.1}]
                        }
                        Important: Your predictions are NOT guaranteed. Users should verify independently."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=settings.GROQ_TIMEOUT,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Parse response
            response_text = response.choices[0].message.content
            
            try:
                import json
                # Try to extract JSON from response
                if "{" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    json_str = response_text[json_start:json_end]
                    suggestion = json.loads(json_str)
                else:
                    suggestion = None
            except Exception as e:
                logger.error(f"Error parsing AI response: {e}")
                suggestion = None
            
            # Log usage
            if db and user_id:
                log = AIUsageLog(
                    user_id=user_id,
                    match_id=match.id,
                    prompt=prompt[:500],  # Truncate
                    suggestion=suggestion or {"error": "parse_failed"},
                    ip_address=ip_address,
                    latency_ms=latency_ms,
                )
                db.add(log)
                db.commit()
            
            return suggestion
        
        except Exception as e:
            logger.error(f"Error getting AI suggestion: {e}")
            if db and user_id:
                log = AIUsageLog(
                    user_id=user_id,
                    match_id=match.id,
                    suggestion={},
                    error=str(e),
                    ip_address=ip_address,
                )
                db.add(log)
                db.commit()
            return None
    
    @staticmethod
    def _build_prompt(match: Match, user_history: Dict = None, style: str = "balanced") -> str:
        """Build prompt for AI"""
        prompt = f"""
Por favor, forneça uma sugestão de placar para este jogo da Copa 2026:

**Jogo**: {match.home_team} vs {match.away_team}
**Fase**: {match.stage}
**Horário**: {match.kickoff_at_utc.isoformat()}
**Local**: {match.venue or 'TBD'}

Considere:
- Histórico recente dos times
- Rankings FIFA (não fornecidos neste contexto)
- Condições do jogo (altitude, clima, etc.)
- Estilo de jogo de cada seleção

Estilo de predição: {style}
- 'conservador': scores baixos, mais empates
- 'agressivo': scores altos, mais vitórias decisivas
- 'balanced': mix equilibrado

Responda APENAS em JSON válido, sem explicações adicionais.
"""
        return prompt.strip()
    
    @staticmethod
    def check_quota(db: Session, user_id: int) -> int:
        """Check AI usage quota for user today"""
        from datetime import datetime, timedelta, timezone
        
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        count = db.query(AIUsageLog).filter(
            AIUsageLog.user_id == user_id,
            AIUsageLog.created_at >= today_start,
            AIUsageLog.error.is_(None),  # Only count successful requests
        ).count()
        
        remaining = max(0, settings.AI_SUGGESTION_QUOTA_PER_DAY - count)
        return remaining
    
    @staticmethod
    def has_quota(db: Session, user_id: int) -> bool:
        """Check if user has remaining quota"""
        return AIService.check_quota(db, user_id) > 0
