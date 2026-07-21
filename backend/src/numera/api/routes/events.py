import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import BusinessEventRepository

router = APIRouter()


def _serialize(event):
    payload = json.loads(event.payload_json)
    payload["entity_type"] = event.entity_type
    payload["entity_id"] = event.entity_id
    return payload


@router.get("/")
def list_business_events(
    event_type: str | None = Query(default=None),
    company_id: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    events = BusinessEventRepository(db).list(
        company_id=company_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )
    return [_serialize(event) for event in events]


@router.get("/timeline/{entity_type}/{entity_id}")
def get_business_timeline(
    entity_type: str,
    entity_id: str,
    company_id: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    events = BusinessEventRepository(db).list(
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )
    return list(reversed([_serialize(event) for event in events]))