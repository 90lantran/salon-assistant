from datetime import time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.business_hours import BusinessHours
from app.models.service import Service


DEMO_SERVICES = [
    {
        "name": "Classic Manicure",
        "description": "Nail shaping, cuticle care, and regular polish.",
        "duration_minutes": 45,
        "price_cents": 2500,
        "category": "manicure",
        "is_active": True,
    },
    {
        "name": "Gel Manicure",
        "description": "Long-lasting gel polish manicure.",
        "duration_minutes": 60,
        "price_cents": 3500,
        "category": "manicure",
        "is_active": True,
    },
    {
        "name": "Acrylic Full Set",
        "description": "Full acrylic extension set with shape and polish.",
        "duration_minutes": 90,
        "price_cents": 5500,
        "category": "enhancements",
        "is_active": True,
    },
    {
        "name": "Classic Pedicure",
        "description": "Foot soak, nail care, exfoliation, and regular polish.",
        "duration_minutes": 60,
        "price_cents": 4000,
        "category": "pedicure",
        "is_active": True,
    },
    {
        "name": "Gel Pedicure",
        "description": "Pedicure finished with durable gel polish.",
        "duration_minutes": 75,
        "price_cents": 5000,
        "category": "pedicure",
        "is_active": True,
    },
    {
        "name": "Dip Powder Overlay",
        "description": "Dip powder overlay on natural nails.",
        "duration_minutes": 60,
        "price_cents": 4500,
        "category": "enhancements",
        "is_active": True,
    },
]

DEMO_BUSINESS_HOURS = [
    {"day_of_week": 0, "open_time": time(9, 0), "close_time": time(19, 0), "label": "Monday"},
    {"day_of_week": 1, "open_time": time(9, 0), "close_time": time(19, 0), "label": "Tuesday"},
    {"day_of_week": 2, "open_time": time(9, 0), "close_time": time(19, 0), "label": "Wednesday"},
    {"day_of_week": 3, "open_time": time(9, 0), "close_time": time(19, 0), "label": "Thursday"},
    {"day_of_week": 4, "open_time": time(9, 0), "close_time": time(19, 0), "label": "Friday"},
    {"day_of_week": 5, "open_time": time(9, 0), "close_time": time(17, 0), "label": "Saturday"},
]


def seed_demo_data(db: Session) -> dict[str, int]:
    existing_services = set(db.scalars(select(Service.name)))

    services_created = 0
    for service_data in DEMO_SERVICES:
        if service_data["name"] in existing_services:
            continue
        db.add(Service(**service_data))
        services_created += 1

    db.execute(delete(BusinessHours))
    for hours_data in DEMO_BUSINESS_HOURS:
        db.add(BusinessHours(**hours_data))

    db.commit()

    return {
        "services_created": services_created,
        "business_hours_written": len(DEMO_BUSINESS_HOURS),
    }
