from fastapi import APIRouter, HTTPException, Query

from numera.engines.business_events import event_bus

router = APIRouter()


@router.get("/")
def list_business_events(
    event_type: str | None = Query(default=None),
    company_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    try:
        events = event_bus.recent(event_type=event_type, company_id=company_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return [event.to_dict() for event in events]
