import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import settings
from app.model import ModelService
from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    IrisInput,
    SinglePredictionResponse,
)

logger = logging.getLogger("mlops.api")
router = APIRouter()


def get_model_service(request: Request) -> ModelService:
    """Dependency provider for ModelService attached to application state."""
    model_service: ModelService = getattr(request.app.state, "model_service", None)
    if not model_service or not model_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model service is currently unavailable or uninitialized.",
        )
    return model_service


@router.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health_check(request: Request):
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    model_service: ModelService = getattr(request.app.state, "model_service", None)
    is_ready = model_service is not None and model_service.is_loaded

    return HealthResponse(
        status="healthy" if is_ready else "degraded",
        model_loaded=is_ready,
        model_version=settings.MODEL_VERSION,
        app_version=settings.APP_VERSION,
    )


@router.post(
    "/predict",
    response_model=SinglePredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Inference"],
    summary="Predict Iris species for a single feature set",
)
def predict(
    payload: IrisInput,
    model_service: ModelService = Depends(get_model_service),
):
    """Run real-time inference on a single sample."""
    try:
        prediction, latency_ms = model_service.predict(payload)
        return SinglePredictionResponse(
            success=True,
            model_version=settings.MODEL_VERSION,
            prediction=prediction,
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.exception(f"Inference error on single prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(e)}",
        )


@router.post(
    "/predict-batch",
    response_model=BatchPredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Inference"],
    summary="Batch inference on multiple Iris feature sets",
)
def predict_batch(
    payload: BatchPredictionRequest,
    model_service: ModelService = Depends(get_model_service),
):
    """Run vectorized high-throughput inference on a batch of samples."""
    try:
        predictions, latency_ms = model_service.predict_batch(payload.inputs)
        return BatchPredictionResponse(
            success=True,
            model_version=settings.MODEL_VERSION,
            total_samples=len(payload.inputs),
            predictions=predictions,
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.exception(f"Inference error on batch prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference failed: {str(e)}",
        )
