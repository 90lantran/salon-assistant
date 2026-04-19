from datetime import date, datetime, time

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models.business_hours import BusinessHours
from app.models.service import Service


client = TestClient(app)


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


def test_list_services_returns_seeded_service() -> None:
    response = client.get("/services")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Gel Manicure"
    assert body[0]["price_cents"] == 3500


def test_get_availability_returns_open_slot() -> None:
    response = client.get(
        "/availability",
        params={"service_id": 1, "requested_date": date(2026, 4, 20).isoformat()},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["service_id"] == 1
    assert body["slots"][0]["start_time"] == "2026-04-20T09:00:00"
    assert body["slots"][0]["end_time"] == "2026-04-20T10:00:00"


def test_create_appointment_returns_booking() -> None:
    response = client.post(
        "/appointments",
        json={
            "customer_name": "Lan Tran",
            "phone": "5551234567",
            "service_id": 1,
            "start_time": datetime(2026, 4, 20, 9, 0).isoformat(),
            "notes": "Prefers quick soak-off.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["service_id"] == 1
    assert body["status"] == "booked"
    assert body["end_time"] == "2026-04-20T10:00:00"


def test_create_appointment_rejects_conflicting_time() -> None:
    first_response = client.post(
        "/appointments",
        json={
            "customer_name": "Lan Tran",
            "phone": "5551234567",
            "service_id": 1,
            "start_time": datetime(2026, 4, 20, 9, 0).isoformat(),
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/appointments",
        json={
            "customer_name": "Jamie Nguyen",
            "phone": "5550001111",
            "service_id": 1,
            "start_time": datetime(2026, 4, 20, 9, 30).isoformat(),
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Requested time is no longer available."
