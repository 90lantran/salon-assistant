from sqlalchemy import Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BusinessHours(Base):
    __tablename__ = "business_hours"

    id: Mapped[int] = mapped_column(primary_key=True)
    day_of_week: Mapped[int] = mapped_column(Integer(), index=True)
    open_time: Mapped[Time] = mapped_column(Time())
    close_time: Mapped[Time] = mapped_column(Time())
    label: Mapped[str | None] = mapped_column(String(50), nullable=True)
