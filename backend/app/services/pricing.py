from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service


def list_active_services(db: Session) -> list[Service]:
    query = (
        select(Service)
        .where(Service.is_active.is_(True))
        .order_by(Service.category.asc(), Service.name.asc())
    )
    return list(db.scalars(query))


def lookup_price(db: Session, service_name: str) -> dict:
    query = select(Service).where(Service.name == service_name, Service.is_active.is_(True))
    service = db.scalar(query)

    if service is None:
        return {"service_name": service_name, "price_cents": None}

    return {"service_name": service.name, "price_cents": service.price_cents}


def find_service_by_name(db: Session, service_name: str) -> Service | None:
    normalized_name = service_name.strip().lower()

    exact_match = db.scalar(
        select(Service).where(
            Service.name.ilike(service_name),
            Service.is_active.is_(True),
        )
    )
    if exact_match is not None:
        return exact_match

    partial_matches = list(
        db.scalars(
            select(Service)
            .where(
                Service.name.ilike(f"%{normalized_name}%"),
                Service.is_active.is_(True),
            )
            .order_by(Service.name.asc())
        )
    )
    if partial_matches:
        return partial_matches[0]

    return None
