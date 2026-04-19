"""API schema package."""

from app.schemas.appointment import AppointmentCreate, AppointmentRead
from app.schemas.availability import AvailabilityResponse, AvailabilitySlot
from app.schemas.service import ServiceRead

__all__ = [
    "AppointmentCreate",
    "AppointmentRead",
    "AvailabilityResponse",
    "AvailabilitySlot",
    "ServiceRead",
]
