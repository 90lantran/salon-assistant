from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"),
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer())
    comments: Mapped[str | None] = mapped_column(Text(), nullable=True)
    follow_up_requested: Mapped[bool] = mapped_column(default=False)
    channel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())

    appointment = relationship("Appointment", back_populates="feedback_entries")
