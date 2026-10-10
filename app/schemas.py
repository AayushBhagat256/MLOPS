from typing import Dict, List
from pydantic import BaseModel, Field


class IrisInput(BaseModel):
    """Input features for single iris prediction with validation."""

    sepal_length: float = Field(
        ...,
        gt=0.0,
        lt=20.0,
        description="Sepal length in centimeters (0 < length < 20)",
        examples=[5.1],
    )
    sepal_width: float = Field(
        ...,
        gt=0.0,
        lt=20.0,
        description="Sepal width in centimeters (0 < width < 20)",
        examples=[3.5],
    )
    petal_length: float = Field(
        ...,
        gt=0.0,
        lt=20.0,
        description="Petal length in centimeters (0 < length < 20)",
        examples=[1.4],
    )
    petal_width: float = Field(
        ...,
        gt=0.0,
        lt=20.0,
        description="Petal width in centimeters (0 < width < 20)",
        examples=[0.2],
    )

    def to_feature_list(self) -> List[float]:
        return [self.sepal_length, self.sepal_width, self.petal_length, self.petal_width]


class PredictionResult(BaseModel):
    """Detailed model prediction output."""

    predicted_class_id: int = Field(..., description="Target class integer: 0, 1, or 2")
    predicted_class_name: str = Field(..., description="Iris species name (setosa, versicolor, virginica)")
    confidence: float = Field(..., description="Highest class probability score")
    probabilities: Dict[str, float] = Field(..., description="Probability distribution across all classes")


class SinglePredictionResponse(BaseModel):
    """API response for a single prediction request."""

    success: bool = True
    model_version: str
    prediction: PredictionResult
    latency_ms: float = Field(..., description="Inference latency in milliseconds")


class BatchPredictionRequest(BaseModel):
    """Batch prediction payload with size constraints."""

    inputs: List[IrisInput] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of feature sets (up to 1,000 samples per batch)",
    )


class BatchPredictionResponse(BaseModel):
    """API response for batch prediction requests."""

    success: bool = True
    model_version: str
    total_samples: int
    predictions: List[PredictionResult]
    latency_ms: float = Field(..., description="Batch inference latency in milliseconds")


class HealthResponse(BaseModel):
    """Service health and readiness check response."""

    status: str
    model_loaded: bool
    model_version: str
    app_version: str
