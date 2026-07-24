
"""inventory unique constraint

Revision ID: 20260724_0004
Revises: ae8848f7aadb
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "20260724_0004"
down_revision = "ae8848f7aadb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Check if the index already exists
    existing_indexes = {index["name"] for index in inspector.get_indexes("inventory")}
    if "uq_inventory_user_medicine_expiry_active" in existing_indexes:
        return

    # Check for existing duplicates among non-deleted rows
    duplicate_check = text("""
        SELECT user_id, medicine_id, expiry_date, COUNT(*) as cnt
        FROM inventory
        WHERE is_deleted = 0
        GROUP BY user_id, medicine_id, expiry_date
        HAVING COUNT(*) > 1
    """)
    result = bind.execute(duplicate_check)
    duplicates = result.fetchall()
    if duplicates:
        dup_details = ", ".join(f"(user={r.user_id}, med={r.medicine_id}, expiry={r.expiry_date})" for r in duplicates)
        raise RuntimeError(
            f"Cannot create unique index: duplicate active inventory items found: {dup_details}. "
            "Manually resolve duplicates (e.g., soft-delete or merge) before applying this migration."
        )

    # Create the partial unique index for both PostgreSQL and SQLite
    op.create_index(
        "uq_inventory_user_medicine_expiry_active",
        "inventory",
        ["user_id", "medicine_id", "expiry_date"],
        unique=True,
        sqlite_where=text("is_deleted = 0"),
        postgresql_where=text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_inventory_user_medicine_expiry_active",
        table_name="inventory",
        sqlite_where=text("is_deleted = 0"),
        postgresql_where=text("is_deleted = false"),
    )

