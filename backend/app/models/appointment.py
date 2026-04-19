import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(), index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime())
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.BOOKED,
    )
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())

    customer = relationship("Customer", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    feedback_entries = relationship("Feedback", back_populates="appointment")
