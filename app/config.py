from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime configuration."""

    APP_NAME: str = "Iris Classifier Production API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Base directory resolves to repository root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Model configuration
    MODEL_PATH: Path = BASE_DIR / "model" / "model.joblib"
    MODEL_VERSION: str = "v1"

    # API Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
