from fastapi import APIRouter, status

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness() -> dict[str, str]:
    return {"status": "ready"}
