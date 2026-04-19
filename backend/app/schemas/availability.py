from datetime import datetime

from pydantic import BaseModel


class AvailabilitySlot(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailabilityResponse(BaseModel):
    service_id: int
    slots: list[AvailabilitySlot]
