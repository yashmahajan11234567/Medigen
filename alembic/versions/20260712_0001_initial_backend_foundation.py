"""initial backend foundation

Revision ID: 20260712_0001
Revises: 
Create Date: 2026-07-12 00:00:01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260712_0001"
down_revision = None
branch_labels = None
depends_on = None


medicine_type_enum = sa.Enum(
    "tablet",
    "capsule",
    "syrup",
    "cream",
    "injection",
    "drops",
    "inhaler",
    "other",
    name="medicinetype",
    native_enum=False,
)

inventory_status_enum = sa.Enum(
    "available",
    "low_stock",
    "expiring_soon",
    "expired",
    "out_of_stock",
    name="inventorystatus",
    native_enum=False,
)

schedule_status_enum = sa.Enum(
    "active",
    "paused",
    "completed",
    "cancelled",
    name="schedulestatus",
    native_enum=False,
)

schedule_source_enum = sa.Enum(
    "manual",
    "pharmacy_bill",
    "generic_finder",
    name="schedulesource",
    native_enum=False,
)

notification_type_enum = sa.Enum(
    "reminder",
    "expiry",
    "system",
    name="notificationtype",
    native_enum=False,
)

notification_status_enum = sa.Enum(
    "pending",
    "sent",
    "read",
    "archived",
    name="notificationstatus",
    native_enum=False,
)

document_type_enum = sa.Enum(
    "prescription",
    "pharmacy_bill",
    "other_document",
    name="medicalrecorddocumenttype",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_is_deleted", "users", ["is_deleted"], unique=False)

    op.create_table(
        "medicines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("generic_name", sa.String(length=255), nullable=True),
        sa.Column("brand_name", sa.String(length=255), nullable=True),
        sa.Column("composition", sa.Text(), nullable=True),
        sa.Column("strength", sa.String(length=100), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("dosage_form", medicine_type_enum, nullable=False),
        sa.Column("route", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_medicines_name", "medicines", ["name"], unique=False)
    op.create_index("ix_medicines_generic_name", "medicines", ["generic_name"], unique=False)
    op.create_index("ix_medicines_brand_name", "medicines", ["brand_name"], unique=False)
    op.create_index("ix_medicines_is_deleted", "medicines", ["is_deleted"], unique=False)

    op.create_table(
        "medical_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("diagnosis", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("linked_generic_search_ids", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_medical_records_user_id_users"),
    )
    op.create_index("ix_medical_records_user_title", "medical_records", ["user_id", "title"], unique=False)
    op.create_index("ix_medical_records_is_deleted", "medical_records", ["is_deleted"], unique=False)

    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("medicine_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("quantity_unit", sa.String(length=50), nullable=True),
        sa.Column("status", inventory_status_enum, nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.id"], name="fk_inventory_medicine_id_medicines"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_inventory_user_id_users"),
    )
    op.create_index("ix_inventory_status", "inventory", ["status"], unique=False)
    op.create_index("ix_inventory_expiry_date", "inventory", ["expiry_date"], unique=False)
    op.create_index("ix_inventory_is_deleted", "inventory", ["is_deleted"], unique=False)
    op.create_index("ix_inventory_user_status", "inventory", ["user_id", "status"], unique=False)

    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("medicine_id", sa.Integer(), nullable=False),
        sa.Column("dosage_amount", sa.String(length=50), nullable=True),
        sa.Column("dosage_unit", sa.String(length=50), nullable=True),
        sa.Column("frequency", sa.String(length=100), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("reminder_time", sa.Time(), nullable=True),
        sa.Column("status", schedule_status_enum, nullable=False),
        sa.Column("source", schedule_source_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.id"], name="fk_schedules_medicine_id_medicines"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_schedules_user_id_users"),
    )
    op.create_index("ix_schedules_is_deleted", "schedules", ["is_deleted"], unique=False)
    op.create_index("ix_schedules_user_start_date", "schedules", ["user_id", "start_date"], unique=False)
    op.create_index("ix_schedules_user_status", "schedules", ["user_id", "status"], unique=False)

    op.create_table(
        "medical_record_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("medical_record_id", sa.Integer(), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("doctor_name", sa.String(length=255), nullable=True),
        sa.Column("hospital_or_clinic", sa.String(length=255), nullable=True),
        sa.Column("doctor_specialty", sa.String(length=255), nullable=True),
        sa.Column("consultation_date", sa.Date(), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("diagnosis", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["medical_record_id"],
            ["medical_records.id"],
            name="fk_medical_record_documents_medical_record_id_medical_records",
        ),
        sa.UniqueConstraint("medical_record_id", "file_path", name="uq_record_document_path"),
    )
    op.create_index(
        "ix_medical_record_documents_record_type",
        "medical_record_documents",
        ["medical_record_id", "document_type"],
        unique=False,
    )
    op.create_index(
        "ix_medical_record_documents_is_deleted",
        "medical_record_documents",
        ["is_deleted"],
        unique=False,
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.Column("notification_type", notification_type_enum, nullable=False),
        sa.Column("status", notification_status_enum, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], name="fk_notifications_schedule_id_schedules"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_notifications_user_id_users"),
    )
    op.create_index("ix_notifications_is_deleted", "notifications", ["is_deleted"], unique=False)
    op.create_index("ix_notifications_scheduled_for", "notifications", ["scheduled_for"], unique=False)
    op.create_index("ix_notifications_user_status", "notifications", ["user_id", "status"], unique=False)

    op.create_table(
        "medical_record_schedules",
        sa.Column("medical_record_id", sa.Integer(), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["medical_record_id"],
            ["medical_records.id"],
            name="fk_medical_record_schedules_medical_record_id_medical_records",
        ),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["schedules.id"],
            name="fk_medical_record_schedules_schedule_id_schedules",
        ),
        sa.PrimaryKeyConstraint("medical_record_id", "schedule_id", name="pk_medical_record_schedules"),
    )

    op.create_table(
        "medical_record_inventory_items",
        sa.Column("medical_record_id", sa.Integer(), nullable=False),
        sa.Column("inventory_item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["inventory_item_id"],
            ["inventory.id"],
            name="fk_medrec_invitem_inventory",
        ),
        sa.ForeignKeyConstraint(
            ["medical_record_id"],
            ["medical_records.id"],
            name="fk_medrec_invitem_medrec",
        ),
        sa.PrimaryKeyConstraint(
            "medical_record_id",
            "inventory_item_id",
            name="pk_medical_record_inventory_items",
        ),
    )


def downgrade() -> None:
    op.drop_table("medical_record_inventory_items")
    op.drop_table("medical_record_schedules")
    op.drop_index("ix_notifications_user_status", table_name="notifications")
    op.drop_index("ix_notifications_scheduled_for", table_name="notifications")
    op.drop_index("ix_notifications_is_deleted", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_medical_record_documents_is_deleted", table_name="medical_record_documents")
    op.drop_index("ix_medical_record_documents_record_type", table_name="medical_record_documents")
    op.drop_table("medical_record_documents")
    op.drop_index("ix_schedules_user_status", table_name="schedules")
    op.drop_index("ix_schedules_user_start_date", table_name="schedules")
    op.drop_index("ix_schedules_is_deleted", table_name="schedules")
    op.drop_table("schedules")
    op.drop_index("ix_inventory_user_status", table_name="inventory")
    op.drop_index("ix_inventory_is_deleted", table_name="inventory")
    op.drop_index("ix_inventory_expiry_date", table_name="inventory")
    op.drop_index("ix_inventory_status", table_name="inventory")
    op.drop_table("inventory")
    op.drop_index("ix_medical_records_is_deleted", table_name="medical_records")
    op.drop_index("ix_medical_records_user_title", table_name="medical_records")
    op.drop_table("medical_records")
    op.drop_index("ix_medicines_is_deleted", table_name="medicines")
    op.drop_index("ix_medicines_brand_name", table_name="medicines")
    op.drop_index("ix_medicines_generic_name", table_name="medicines")
    op.drop_index("ix_medicines_name", table_name="medicines")
    op.drop_table("medicines")
    op.drop_index("ix_users_is_deleted", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

