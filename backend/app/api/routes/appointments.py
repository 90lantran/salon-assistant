from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentRead
from app.services.booking import create_booking

router = APIRouter()


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
) -> AppointmentRead:
    try:
        appointment = create_booking(
            db,
            customer_name=payload.customer_name,
            phone=payload.phone,
            service_id=payload.service_id,
            start_time=payload.start_time,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AppointmentRead(
        id=appointment.id,
        customer_id=appointment.customer_id,
        service_id=appointment.service_id,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        status=appointment.status.value,
        notes=appointment.notes,
    )
