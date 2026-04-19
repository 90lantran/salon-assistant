from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.availability import AvailabilityResponse, AvailabilitySlot
from app.services.booking import get_available_slots

router = APIRouter()


@router.get("", response_model=AvailabilityResponse)
def get_availability(
    service_id: int = Query(..., ge=1),
    requested_date: date = Query(...),
    db: Session = Depends(get_db),
) -> AvailabilityResponse:
    slots = get_available_slots(db, service_id=service_id, requested_date=requested_date)
    return AvailabilityResponse(
        service_id=service_id,
        slots=[AvailabilitySlot(**slot) for slot in slots],
    )
