from fastapi import APIRouter


router = APIRouter(tags=["health"])

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    # сюда позже можно добавить проверки подключений к БД/брокеру
    return {"status": "ready"}
