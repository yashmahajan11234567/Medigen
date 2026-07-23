from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Self


class Settings(BaseSettings):
    app_name: str = "MediGen API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./medigen.db"
    auto_create_tables: bool = True
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "https://medigen-frontend.onrender.com"]
    )
    log_level: str = "INFO"
    # OCR Configuration
    OCR_ENGINE: str = "paddleocr"
    OCR_LANGUAGES: list[str] = ["en"]
    OCR_CONFIDENCE_THRESHOLD: float = 0.6
    OCR_LOW_CONFIDENCE_WARN_THRESHOLD: float = 0.4
    OCR_LOW_CONFIDENCE_REJECT_THRESHOLD: float = 0.25
    OCR_MAX_UPLOAD_MB: int = 5
    OCR_ALLOWED_MIME_TYPES: str = "image/png,image/jpeg,application/pdf"
    OCR_TEMP_DIR: str = "/tmp/medigen_ocr"
    OCR_ENGINE_TIMEOUT_SEC: int = 30
    OCR_PREPROCESS_GRAYSCALE: bool = True
    OCR_PREPROCESS_BINARIZE: bool = True
    OCR_PREPROCESS_DESKEW: bool = True
    OCR_PREPROCESS_APPLY_CLAHE: bool = True
    OCR_PREPROCESS_DENOISE: bool = True
    OCR_USE_ANGLE_CLS: bool = False
    # Image quality check configuration
    OCR_ENABLE_QUALITY_CHECK: bool = True
    OCR_BLUR_THRESHOLD: float = 100.0
    OCR_MIN_BRIGHTNESS: int = 40
    OCR_MAX_BRIGHTNESS: int = 240
    OCR_MIN_CONTRAST: float = 20.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MEDIGEN_",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def enforce_production_secret(self) -> Self:
        if self.environment == "production" and self.secret_key == "change-this-secret-key":
            raise ValueError(
                "MEDIGEN_SECRET_KEY must be set to a strong, unique value in production. "
                "Do not use the default secret key."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
