from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ComprehendSentimentRequest(BaseModel):
    text: str = Field(..., description="Texto para análise de sentimento")
    language_code: str = Field(default="pt", description="Idioma do texto")

class ComprehendSentimentResponse(BaseModel):
    sentiment: str = Field(..., description="Sentimento detectado (POSITIVE, NEGATIVE, NEUTRAL, MIXED)")

class ComprehendMedicalRequest(BaseModel):
    text: str = Field(..., description="Texto médico para extração de entidades")

class ComprehendMedicalResponse(BaseModel):
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Entidades médicas detectadas")
