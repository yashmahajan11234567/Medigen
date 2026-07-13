from typing import Any

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    message: str
    code: str
    details: list[dict[str, Any]] | None = None


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    app_name: str
    environment: str
    database: str

