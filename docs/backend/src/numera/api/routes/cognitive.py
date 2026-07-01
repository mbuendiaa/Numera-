from fastapi import APIRouter
from pydantic import BaseModel

from numera.domain.cognitive.models import CognitiveDecisionRequest
from numera.domain.cognitive.service import CognitiveService

router = APIRouter()


class CognitiveDecisionResponse(BaseModel):
    decision_id: str
    status: str
    recommendation: str
    confidence: float
    explanation: list[str]


@router.post("/decision", response_model=CognitiveDecisionResponse)
def create_decision(payload: CognitiveDecisionRequest):
    service = CognitiveService()
    decision = service.evaluate(payload)
    return CognitiveDecisionResponse(**decision.model_dump())
