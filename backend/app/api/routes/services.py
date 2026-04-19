from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.service import ServiceRead
from app.services.pricing import list_active_services

router = APIRouter()


@router.get("", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)) -> list[ServiceRead]:
    return list_active_services(db)
