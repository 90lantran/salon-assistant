"""API schema package."""

from app.schemas.assistant import (
    AssistantRequest,
    AssistantResponse,
    ConversationMessage,
    ToolResult,
)
from app.schemas.appointment import AppointmentCreate, AppointmentRead
from app.schemas.availability import AvailabilityResponse, AvailabilitySlot
from app.schemas.service import ServiceRead

__all__ = [
    "AssistantRequest",
    "AssistantResponse",
    "AppointmentCreate",
    "AppointmentRead",
    "AvailabilityResponse",
    "AvailabilitySlot",
    "ConversationMessage",
    "ServiceRead",
    "ToolResult",
]
