from pydantic import BaseModel


class ServiceRead(BaseModel):
    id: int
    name: str
    description: str | None
    duration_minutes: int
    price_cents: int
    category: str
    is_active: bool

    model_config = {"from_attributes": True}
