from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


class DatabaseSessionManager:
    def __init__(self, database_url: str) -> None:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, connect_args=connect_args, future=True)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )

    def session(self) -> Generator[Session, None, None]:
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()

    def dispose(self) -> None:
        self.engine.dispose()


def get_db() -> Generator[Session, None, None]:
    yield from session_manager.session()


session_manager = DatabaseSessionManager(get_settings().database_url)
DbSession = Annotated[Session, Depends(get_db)]


def initialize_database() -> None:
    from app.db.base import Base
    from app.models import load_all_models

    load_all_models()
    if get_settings().auto_create_tables:
        Base.metadata.create_all(bind=session_manager.engine)


def shutdown_database() -> None:
    session_manager.dispose()
