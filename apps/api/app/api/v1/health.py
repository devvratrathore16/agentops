"""Liveness and database readiness endpoints."""

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["health"])
logger = structlog.get_logger(__name__)


@router.get("/health", summary="Check API process liveness")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Check API and database readiness")
def readiness(db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("database_readiness_failed", error_type=type(exc).__name__)
        raise HTTPException(status_code=503, detail="database_unavailable") from exc
    return {"status": "ready", "checks": {"database": "ok"}}
