from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.db.helpers import ping_database
from app.db.session import initialize_database, shutdown_database
from app.middleware.authentication import AuthenticationContextMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.schemas.common import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    initialize_database()
    yield
    shutdown_database()


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
        redirect_slashes=False,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(AuthenticationContextMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    def health_check() -> HealthResponse:
        return HealthResponse(
            app_name=settings.app_name,
            environment=settings.environment,
            database="connected" if ping_database() else "unavailable",
        )

    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "Welcome to MediGen API",
            "version": "settings.app_version",
            "status": "online",
            "documentation": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
        }

    print("\n========== REGISTERED ROUTES ==========")
    for route in app.routes:
        methods = ",".join(sorted(route.methods or []))
        print(f"{methods:20} {route.path} -> {route.name}")
    print("=======================================\n")

    return app


app = create_application()
