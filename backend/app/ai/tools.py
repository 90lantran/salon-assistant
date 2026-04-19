from datetime import date, datetime
from typing import Any

from app.ai.types import ToolDefinition
from app.db import SessionLocal
from app.schemas.appointment import AppointmentRead
from app.schemas.availability import AvailabilitySlot
from app.services.booking import create_booking, get_available_slots
from app.services.pricing import find_service_by_name, list_active_services, lookup_price


TOOL_DEFINITIONS = [
    ToolDefinition(
        name="lookup_service_price",
        description="Look up the current price and duration for a salon service.",
        input_schema={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "The service name or best caller-provided match.",
                }
            },
            "required": ["service_name"],
        },
    ),
    ToolDefinition(
        name="check_availability",
        description="Check open appointment slots for a given service and date.",
        input_schema={
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "The requested salon service name.",
                },
                "requested_date": {
                    "type": "string",
                    "description": "Requested date in ISO format, like 2026-04-20.",
                },
            },
            "required": ["service_name", "requested_date"],
        },
    ),
    ToolDefinition(
        name="create_appointment",
        description="Create a salon appointment for a customer.",
        input_schema={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "phone": {"type": "string"},
                "service_name": {"type": "string"},
                "start_time": {
                    "type": "string",
                    "description": "Appointment start time in ISO datetime format.",
                },
                "notes": {"type": "string"},
            },
            "required": ["customer_name", "phone", "service_name", "start_time"],
        },
    ),
]


def get_tool_definitions() -> list[dict[str, Any]]:
    return [definition.model_dump() for definition in TOOL_DEFINITIONS]


def lookup_service_price(service_name: str) -> dict[str, Any]:
    with SessionLocal() as db:
        service = find_service_by_name(db, service_name)
        if service is None:
            available_services = [item.name for item in list_active_services(db)]
            return {
                "found": False,
                "service_name": service_name,
                "message": "Service not found.",
                "available_services": available_services,
            }

        price_info = lookup_price(db, service.name)
        return {
            "found": True,
            "service_id": service.id,
            "service_name": price_info["service_name"],
            "price_cents": price_info["price_cents"],
            "duration_minutes": service.duration_minutes,
            "category": service.category,
        }


def check_availability(service_name: str, requested_date: str) -> dict[str, Any]:
    requested_day = date.fromisoformat(requested_date)

    with SessionLocal() as db:
        service = find_service_by_name(db, service_name)
        if service is None:
            return {
                "found": False,
                "service_name": service_name,
                "message": "Service not found.",
                "slots": [],
            }

        slots = get_available_slots(db, service_id=service.id, requested_date=requested_day)
        return {
            "found": True,
            "service_id": service.id,
            "service_name": service.name,
            "requested_date": requested_day.isoformat(),
            "slots": [AvailabilitySlot(**slot).model_dump(mode="json") for slot in slots],
        }


def create_appointment(
    customer_name: str,
    phone: str,
    service_name: str,
    start_time: str,
    notes: str | None = None,
) -> dict[str, Any]:
    appointment_start = datetime.fromisoformat(start_time)

    with SessionLocal() as db:
        service = find_service_by_name(db, service_name)
        if service is None:
            return {
                "created": False,
                "service_name": service_name,
                "message": "Service not found.",
            }

        try:
            appointment = create_booking(
                db,
                customer_name=customer_name,
                phone=phone,
                service_id=service.id,
                start_time=appointment_start,
                notes=notes,
            )
        except ValueError as exc:
            return {
                "created": False,
                "service_name": service.name,
                "message": str(exc),
            }

        payload = AppointmentRead(
            id=appointment.id,
            customer_id=appointment.customer_id,
            service_id=appointment.service_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status.value,
            notes=appointment.notes,
        )
        return {
            "created": True,
            "service_name": service.name,
            "appointment": payload.model_dump(mode="json"),
        }


TOOL_HANDLERS = {
    "lookup_service_price": lookup_service_price,
    "check_availability": check_availability,
    "create_appointment": create_appointment,
}


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name not in TOOL_HANDLERS:
        raise ValueError(f"Unknown tool: {name}")

    return TOOL_HANDLERS[name](**arguments)
