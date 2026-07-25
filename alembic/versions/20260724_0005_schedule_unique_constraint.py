
"""schedule unique constraint for active schedules

Revision ID: 20260724_0005
Revises: 20260724_0004
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "20260724_0005"
down_revision = "20260724_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Check if the index already exists
    existing_indexes = {index["name"] for index in inspector.get_indexes("schedules")}
    if "uq_schedules_user_medicine_active_dates" in existing_indexes:
        return

    # Check for existing exact duplicate active schedules
    # (same user, medicine, start_date, end_date, status=active, not soft-deleted)
    # Use SQLAlchemy expression for dialect-compatible boolean comparison
    # is_deleted.is_(False) generates "is_deleted = false" on PostgreSQL and "is_deleted = 0" on SQLite
    schedules_table = sa.Table("schedules", sa.MetaData(), autoload_with=bind)
    duplicate_check = (
        sa.select(
            schedules_table.c.user_id,
            schedules_table.c.medicine_id,
            schedules_table.c.start_date,
            schedules_table.c.end_date,
            sa.func.count().label("cnt"),
        )
        .where(
            schedules_table.c.is_deleted.is_(False) &
            (schedules_table.c.status == "active")
        )
        .group_by(
            schedules_table.c.user_id,
            schedules_table.c.medicine_id,
            schedules_table.c.start_date,
            schedules_table.c.end_date,
        )
        .having(sa.func.count() > 1)
    )
    result = bind.execute(duplicate_check)
    duplicates = result.fetchall()
    if duplicates:
        dup_details = ", ".join(
            f"(user={r.user_id}, med={r.medicine_id}, start={r.start_date}, end={r.end_date})"
            for r in duplicates
        )
        raise RuntimeError(
            f"Cannot create unique index: duplicate exact active schedules found: {dup_details}. "
            "Manually resolve duplicates (e.g., soft-delete or update) before applying this migration."
        )

    # Create the partial unique index for both PostgreSQL and SQLite
    # This prevents EXACT duplicate active schedules (same user, medicine, start_date, end_date)
    # The service layer (_ensure_no_duplicate_schedule) has a stricter check that prevents
    # OVERLAPPING schedules - that logic remains in the service layer and cannot be
    # expressed as a portable partial unique index across PostgreSQL and SQLite.
    op.create_index(
        "uq_schedules_user_medicine_active_dates",
        "schedules",
        ["user_id", "medicine_id", "start_date", "end_date"],
        unique=True,
        sqlite_where=text("is_deleted = 0 AND status = 'active'"),
        postgresql_where=text("is_deleted = false AND status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_schedules_user_medicine_active_dates",
        table_name="schedules",
        sqlite_where=text("is_deleted = 0 AND status = 'active'"),
        postgresql_where=text("is_deleted = false AND status = 'active'"),
    )
