from fastapi import APIRouter

router = APIRouter()


@router.post("/incoming")
def incoming_call() -> dict[str, str]:
    return {"status": "not_implemented"}
