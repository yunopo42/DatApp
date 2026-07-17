from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
@router.get("/live")
def liveness_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(response: Response) -> dict[str, str]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}

    return {"status": "ready"}
