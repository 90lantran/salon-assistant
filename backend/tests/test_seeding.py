from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models.business_hours import BusinessHours
from app.models.service import Service
from app.services.seeding import seed_demo_data


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_seed_demo_data_is_idempotent_for_services() -> None:
    with SessionLocal() as db:
        first_result = seed_demo_data(db)
        second_result = seed_demo_data(db)

        service_count = len(list(db.scalars(select(Service))))
        business_hours_count = len(list(db.scalars(select(BusinessHours))))

    assert first_result["services_created"] == 6
    assert second_result["services_created"] == 0
    assert service_count == 6
    assert business_hours_count == 6
