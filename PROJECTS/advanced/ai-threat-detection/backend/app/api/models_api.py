"""
©AngelaMos | 2026
models_api.py
"""

import uuid

from fastapi import APIRouter, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_metadata import ModelMetadata

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/status")
async def model_status(request: Request, ) -> dict[str, object]:
    """
    Return the status of active ML models
    """
    models_loaded = getattr(request.app.state, "models_loaded", False)
    detection_mode = getattr(request.app.state, "detection_mode", "rules")

    active_models: list[dict[str, object]] = []
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is not None:
        async with session_factory() as session:
            active_models = await _get_active_models(session)

    return {
        "models_loaded": models_loaded,
        "detection_mode": detection_mode,
        "active_models": active_models,
    }


@router.post("/retrain", status_code=202)
async def retrain() -> dict[str, object]:
    """
    Trigger an async model retraining job
    """
    return {
        "status": "accepted",
        "job_id": uuid.uuid4().hex,
    }


async def _get_active_models(
    session: AsyncSession, ) -> list[dict[str, object]]:
    """
    Query all active model metadata records
    """
    query = select(ModelMetadata).where(
        ModelMetadata.is_active == True  # noqa: E712
    )
    rows = (await session.execute(query)).scalars().all()
    return [{
        "model_type": row.model_type,
        "version": row.version,
        "training_samples": row.training_samples,
        "metrics": row.metrics,
        "threshold": row.threshold,
    } for row in rows]
