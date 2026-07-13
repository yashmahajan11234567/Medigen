"""schedule backend expansion

Revision ID: 20260713_0002
Revises: 20260712_0001
Create Date: 2026-07-13 00:00:01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0002"
down_revision = "20260712_0001"
branch_labels = None
depends_on = None


food_timing_enum = sa.Enum("before_food", "after_food", name="foodtiming", native_enum=False)
reminder_period_enum = sa.Enum("morning", "afternoon", "night", name="reminderperiod", native_enum=False)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    schedule_columns = {column["name"] for column in inspector.get_columns("schedules")}

    if "dosage_pattern" not in schedule_columns:
        op.add_column("schedules", sa.Column("dosage_pattern", sa.String(length=50), nullable=True))
    if "food_timing" not in schedule_columns:
        op.add_column("schedules", sa.Column("food_timing", food_timing_enum, nullable=True))
    if "notes" not in schedule_columns:
        op.add_column("schedules", sa.Column("notes", sa.Text(), nullable=True))
    if "duration_days" not in schedule_columns:
        op.add_column("schedules", sa.Column("duration_days", sa.Integer(), nullable=True))
    if "purchase_date" not in schedule_columns:
        op.add_column("schedules", sa.Column("purchase_date", sa.Date(), nullable=True))
    if "expiry_date" not in schedule_columns:
        op.add_column("schedules", sa.Column("expiry_date", sa.Date(), nullable=True))
    if "quantity" not in schedule_columns:
        op.add_column("schedules", sa.Column("quantity", sa.Float(), nullable=True))
    if "pharmacy_name" not in schedule_columns:
        op.add_column("schedules", sa.Column("pharmacy_name", sa.String(length=255), nullable=True))

    existing_tables = set(inspector.get_table_names())
    if "schedule_reminders" not in existing_tables:
        op.create_table(
            "schedule_reminders",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("schedule_id", sa.Integer(), nullable=False),
            sa.Column("reminder_date", sa.Date(), nullable=False),
            sa.Column("reminder_time", sa.Time(), nullable=False),
            sa.Column("period", reminder_period_enum, nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], name="fk_schedule_reminders_schedule_id_schedules"),
        )

    existing_indexes = {index["name"] for index in inspector.get_indexes("schedule_reminders")}
    if "ix_schedule_reminders_is_deleted" not in existing_indexes:
        op.create_index("ix_schedule_reminders_is_deleted", "schedule_reminders", ["is_deleted"], unique=False)
    if "ix_schedule_reminders_schedule_date" not in existing_indexes:
        op.create_index("ix_schedule_reminders_schedule_date", "schedule_reminders", ["schedule_id", "reminder_date"], unique=False)
    if "ix_schedule_reminders_date_time" not in existing_indexes:
        op.create_index("ix_schedule_reminders_date_time", "schedule_reminders", ["reminder_date", "reminder_time"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_schedule_reminders_date_time", table_name="schedule_reminders")
    op.drop_index("ix_schedule_reminders_schedule_date", table_name="schedule_reminders")
    op.drop_index("ix_schedule_reminders_is_deleted", table_name="schedule_reminders")
    op.drop_table("schedule_reminders")
    op.drop_column("schedules", "pharmacy_name")
    op.drop_column("schedules", "quantity")
    op.drop_column("schedules", "expiry_date")
    op.drop_column("schedules", "purchase_date")
    op.drop_column("schedules", "duration_days")
    op.drop_column("schedules", "notes")
    op.drop_column("schedules", "food_timing")
    op.drop_column("schedules", "dosage_pattern")
