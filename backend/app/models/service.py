from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer())
    price_cents: Mapped[int] = mapped_column(Integer())
    category: Mapped[str] = mapped_column(String(50), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)

    appointments = relationship("Appointment", back_populates="service")
