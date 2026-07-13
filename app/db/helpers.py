from sqlalchemy import text

from app.db.session import session_manager


def ping_database() -> bool:
    with session_manager.engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
