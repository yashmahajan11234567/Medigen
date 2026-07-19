from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()