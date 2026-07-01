from pydantic import BaseModel, Field


class CognitiveDecisionRequest(BaseModel):
    company_id: str
    input_type: str = Field(..., examples=["invoice", "bank_transaction", "user_question"])
    description: str
    risk_level: str = Field(default="low", examples=["low", "medium", "high"])


class CognitiveDecision(BaseModel):
    decision_id: str
    status: str
    recommendation: str
    confidence: float
    explanation: list[str]
