from datetime import datetime, time

from app.ai.tools import (
    call_tool,
    check_availability,
    create_appointment,
    get_tool_definitions,
    lookup_service_price,
)
from app.db import Base, SessionLocal, engine
from app.models.business_hours import BusinessHours
from app.models.service import Service


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.add(
            Service(
                name="Gel Manicure",
                description="Long-lasting gel polish manicure.",
                duration_minutes=60,
                price_cents=3500,
                category="manicure",
                is_active=True,
            )
        )
        db.add(
            BusinessHours(
                day_of_week=0,
                open_time=time(9, 0),
                close_time=time(17, 0),
                label="Monday",
            )
        )
        db.commit()


def test_get_tool_definitions_lists_core_tools() -> None:
    definitions = get_tool_definitions()
    tool_names = {item["name"] for item in definitions}

    assert tool_names == {
        "lookup_service_price",
        "check_availability",
        "create_appointment",
    }


def test_lookup_service_price_returns_service_details() -> None:
    result = lookup_service_price("gel manicure")

    assert result["found"] is True
    assert result["service_name"] == "Gel Manicure"
    assert result["price_cents"] == 3500


def test_check_availability_returns_slots_for_matching_service() -> None:
    result = check_availability("gel", "2026-04-20")

    assert result["found"] is True
    assert result["slots"][0]["start_time"] == "2026-04-20T09:00:00"


def test_create_appointment_returns_created_payload() -> None:
    result = create_appointment(
        customer_name="Lan Tran",
        phone="5551234567",
        service_name="gel manicure",
        start_time=datetime(2026, 4, 20, 9, 0).isoformat(),
        notes="First-time customer.",
    )

    assert result["created"] is True
    assert result["appointment"]["status"] == "booked"
    assert result["appointment"]["end_time"] == "2026-04-20T10:00:00"


def test_call_tool_dispatches_by_name() -> None:
    result = call_tool("lookup_service_price", {"service_name": "Gel Manicure"})

    assert result["found"] is True
    assert result["service_name"] == "Gel Manicure"
