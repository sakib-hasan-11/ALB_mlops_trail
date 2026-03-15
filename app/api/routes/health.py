import logging

from fastapi import APIRouter

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
def health() -> dict:
    logger.info("Health endpoint called")
    return {"status": "ok"}
