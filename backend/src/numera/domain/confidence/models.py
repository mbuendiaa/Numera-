from pydantic import BaseModel


class ConfidenceCard(BaseModel):
    overall_confidence: float
    evidence: list[str]
    warnings: list[str] = []
    decision: str
