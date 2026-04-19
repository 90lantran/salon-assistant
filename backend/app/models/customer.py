from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())

    appointments = relationship("Appointment", back_populates="customer")
