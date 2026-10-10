import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np

from app.schemas import IrisInput, PredictionResult

logger = logging.getLogger("mlops.model")

# Iris dataset target class mapping
CLASS_MAPPING: Dict[int, str] = {
    0: "setosa",
    1: "versicolor",
    2: "virginica",
}


class ModelService:
    """Production ML model service encapsulating loading, caching, and inference."""

    def __init__(self, model_path: Path, model_version: str = "v1"):
        self.model_path = model_path
        self.model_version = model_version
        self._model = None

    def load(self) -> None:
        """Load model artifact into memory with sanity checks."""
        if not self.model_path.exists():
            error_msg = f"Model artifact not found at: {self.model_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading model artifact from {self.model_path}...")
        try:
            self._model = joblib.load(self.model_path)
            # Basic validation of expected scikit-learn estimator interface
            if not hasattr(self._model, "predict"):
                raise TypeError("Loaded artifact does not implement `predict` method.")
            logger.info("Model loaded successfully into memory.")
        except Exception as e:
            logger.exception(f"Failed to load model artifact: {e}")
            raise

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def _format_prediction(self, class_id: int, probs: Optional[np.ndarray]) -> PredictionResult:
        class_name = CLASS_MAPPING.get(class_id, f"unknown_{class_id}")
        if probs is not None and len(probs) == len(CLASS_MAPPING):
            prob_dict = {CLASS_MAPPING[i]: round(float(probs[i]), 4) for i in range(len(probs))}
            confidence = round(float(np.max(probs)), 4)
        else:
            prob_dict = {class_name: 1.0}
            confidence = 1.0

        return PredictionResult(
            predicted_class_id=int(class_id),
            predicted_class_name=class_name,
            confidence=confidence,
            probabilities=prob_dict,
        )

    def predict(self, iris_input: IrisInput) -> Tuple[PredictionResult, float]:
        """Perform single sample inference and calculate latency."""
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Cannot execute inference.")

        start_time = time.perf_counter()
        features = np.array([iris_input.to_feature_list()], dtype=np.float32)

        raw_pred = self._model.predict(features)[0]
        has_proba = hasattr(self._model, "predict_proba")
        raw_proba = self._model.predict_proba(features)[0] if has_proba else None

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        result = self._format_prediction(int(raw_pred), raw_proba)
        return result, latency_ms

    def predict_batch(self, inputs: List[IrisInput]) -> Tuple[List[PredictionResult], float]:
        """Perform vectorized batch inference across multiple samples."""
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Cannot execute inference.")

        start_time = time.perf_counter()
        features = np.array([item.to_feature_list() for item in inputs], dtype=np.float32)

        raw_preds = self._model.predict(features)
        has_proba = hasattr(self._model, "predict_proba")
        raw_probas = self._model.predict_proba(features) if has_proba else None

        results = []
        for idx, pred in enumerate(raw_preds):
            proba = raw_probas[idx] if raw_probas is not None else None
            results.append(self._format_prediction(int(pred), proba))

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        return results, latency_ms
