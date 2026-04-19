from fastapi import APIRouter

from app.api.routes import appointments, availability, calls, feedback, services


api_router = APIRouter()
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(
    availability.router, prefix="/availability", tags=["availability"]
)
api_router.include_router(
    appointments.router, prefix="/appointments", tags=["appointments"]
)
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
