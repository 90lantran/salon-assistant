from datetime import date, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.business_hours import BusinessHours
from app.models.customer import Customer
from app.models.service import Service


def get_available_slots(
    db: Session,
    service_id: int,
    requested_date: date,
) -> list[dict[str, datetime]]:
    service = db.get(Service, service_id)
    if service is None or not service.is_active:
        return []

    hours = db.scalar(
        select(BusinessHours).where(BusinessHours.day_of_week == requested_date.weekday())
    )
    if hours is None:
        return []

    open_at = datetime.combine(requested_date, hours.open_time)
    close_at = datetime.combine(requested_date, hours.close_time)
    duration = timedelta(minutes=service.duration_minutes)

    appointments = list(
        db.scalars(
            select(Appointment)
            .where(
                Appointment.status == AppointmentStatus.BOOKED,
                Appointment.start_time < close_at,
                Appointment.end_time > open_at,
            )
            .order_by(Appointment.start_time.asc())
        )
    )

    slots: list[dict[str, datetime]] = []
    cursor = open_at

    for appointment in appointments:
        if cursor + duration <= appointment.start_time:
            slots.append({"start_time": cursor, "end_time": cursor + duration})
        if appointment.end_time > cursor:
            cursor = appointment.end_time

    if cursor + duration <= close_at:
        slots.append({"start_time": cursor, "end_time": cursor + duration})

    return slots


def create_booking(
    db: Session,
    customer_name: str,
    phone: str,
    service_id: int,
    start_time: datetime,
    notes: str | None = None,
) -> Appointment:
    service = db.get(Service, service_id)
    if service is None or not service.is_active:
        raise ValueError("Service not found.")

    hours = db.scalar(
        select(BusinessHours).where(BusinessHours.day_of_week == start_time.weekday())
    )
    if hours is None:
        raise ValueError("Salon is closed on the requested day.")

    requested_end_time = start_time + timedelta(minutes=service.duration_minutes)
    open_at = datetime.combine(start_time.date(), hours.open_time)
    close_at = datetime.combine(start_time.date(), hours.close_time)

    if start_time < open_at or requested_end_time > close_at:
        raise ValueError("Appointment must be within business hours.")

    conflicting_appointment = db.scalar(
        select(Appointment).where(
            and_(
                Appointment.status == AppointmentStatus.BOOKED,
                Appointment.start_time < requested_end_time,
                Appointment.end_time > start_time,
            )
        )
    )
    if conflicting_appointment is not None:
        raise ValueError("Requested time is no longer available.")

    customer = db.scalar(select(Customer).where(Customer.phone == phone))
    if customer is None:
        customer = Customer(name=customer_name, phone=phone)
        db.add(customer)
        db.flush()
    else:
        customer.name = customer_name

    appointment = Appointment(
        customer_id=customer.id,
        service_id=service_id,
        start_time=start_time,
        end_time=requested_end_time,
        status=AppointmentStatus.BOOKED,
        notes=notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
