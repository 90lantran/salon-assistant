from fastapi import FastAPI

from app.api.router import api_router
from app.db import Base, engine
from app.models import Appointment, BusinessHours, Customer, Feedback, Service


app = FastAPI(title="Nail Salon Voice Assistant API")
app.include_router(api_router)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
