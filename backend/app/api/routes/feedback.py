from fastapi import APIRouter

router = APIRouter()


@router.post("")
def submit_feedback() -> dict[str, str]:
    return {"status": "not_implemented"}
