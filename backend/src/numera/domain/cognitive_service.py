from sqlalchemy.orm import Session

from numera.domain.schemas import CognitiveDecisionRequest
from numera.infrastructure.repositories import CognitiveDecisionRepository


class CognitiveService:
    def __init__(self, db: Session):
        self.repo = CognitiveDecisionRepository(db)

    def evaluate(self, request: CognitiveDecisionRequest):
        high_risk = request.risk_level == "high"
        return self.repo.create(
            company_id=request.company_id,
            input_type=request.input_type,
            description=request.description,
            risk_level=request.risk_level,
            status="requires_human_review" if high_risk else "recommendation_ready",
            recommendation=(
                "Do not automate. Human approval required."
                if high_risk
                else "Proceed with low-risk recommendation."
            ),
            confidence=0.55 if high_risk else 0.82,
            explanation=(
                ["High-risk action detected.", "Human approval required."]
                if high_risk
                else ["Input classified.", "No blocking rule detected in v0.5."]
            ),
        )
