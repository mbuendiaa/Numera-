from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from numera.domain.cognitive_service import CognitiveService
from numera.domain.schemas import CognitiveDecisionRead, CognitiveDecisionRequest
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import CognitiveDecisionRepository

router = APIRouter()


@router.post("/decision", response_model=CognitiveDecisionRead)
def create_decision(payload: CognitiveDecisionRequest, db: Session = Depends(get_db)):
    return CognitiveService(db).evaluate(payload)


@router.get("/decisions", response_model=list[CognitiveDecisionRead])
def list_decisions(db: Session = Depends(get_db)):
    return CognitiveDecisionRepository(db).list()
