from datetime import datetime

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    service_id: int
    start_time: datetime
    notes: str | None = Field(default=None, max_length=255)


class AppointmentRead(BaseModel):
    id: int
    customer_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: str
    notes: str | None

    model_config = {"from_attributes": True}
