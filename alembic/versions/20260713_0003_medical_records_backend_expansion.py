"""medical records backend expansion

Revision ID: 20260713_0003
Revises: 20260713_0002
Create Date: 2026-07-13 00:00:02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_0003"
down_revision = "20260713_0002"
branch_labels = None
depends_on = None


document_type_enum = sa.Enum(
    "prescription",
    "pharmacy_bill",
    "other_document",
    name="medicalrecorddocumenttype",
    native_enum=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    medical_record_columns = {column["name"] for column in inspector.get_columns("medical_records")}
    if "folder_name" not in medical_record_columns:
        op.add_column(
            "medical_records",
            sa.Column("folder_name", sa.String(length=255), nullable=True),
        )
        op.execute(sa.text("UPDATE medical_records SET folder_name = 'General' WHERE folder_name IS NULL"))
    if "description" not in medical_record_columns:
        op.add_column("medical_records", sa.Column("description", sa.Text(), nullable=True))
    if "hospital_name" not in medical_record_columns:
        op.add_column("medical_records", sa.Column("hospital_name", sa.String(length=255), nullable=True))
    if "doctor_name" not in medical_record_columns:
        op.add_column("medical_records", sa.Column("doctor_name", sa.String(length=255), nullable=True))
    if "visit_date" not in medical_record_columns:
        op.add_column("medical_records", sa.Column("visit_date", sa.Date(), nullable=True))
    if "treatment_name" not in medical_record_columns:
        op.add_column("medical_records", sa.Column("treatment_name", sa.String(length=255), nullable=True))

    with op.batch_alter_table("medical_records") as batch_op:
        batch_op.alter_column("folder_name", existing_type=sa.String(length=255), nullable=False)

    medical_record_indexes = {index["name"] for index in inspector.get_indexes("medical_records")}
    if "ix_medical_records_folder_name" not in medical_record_indexes:
        op.create_index("ix_medical_records_folder_name", "medical_records", ["folder_name"], unique=False)
    if "ix_medical_records_visit_date" not in medical_record_indexes:
        op.create_index("ix_medical_records_visit_date", "medical_records", ["visit_date"], unique=False)

    document_columns = {column["name"] for column in inspector.get_columns("medical_record_documents")}
    if "storage_path" not in document_columns:
        op.add_column("medical_record_documents", sa.Column("storage_path", sa.String(length=500), nullable=True))
        op.execute(
            sa.text(
                "UPDATE medical_record_documents SET storage_path = file_path WHERE storage_path IS NULL"
            )
        )
    if "file_type" not in document_columns:
        op.add_column("medical_record_documents", sa.Column("file_type", sa.String(length=100), nullable=True))
        op.execute(
            sa.text(
                "UPDATE medical_record_documents "
                "SET file_type = COALESCE(NULLIF(mime_type, ''), 'application/octet-stream') "
                "WHERE file_type IS NULL"
            )
        )
    if "file_size" not in document_columns:
        op.add_column("medical_record_documents", sa.Column("file_size", sa.Integer(), nullable=True))
        op.execute(sa.text("UPDATE medical_record_documents SET file_size = 0 WHERE file_size IS NULL"))
    if "upload_date" not in document_columns:
        op.add_column("medical_record_documents", sa.Column("upload_date", sa.DateTime(timezone=True), nullable=True))
        op.execute(
            sa.text(
                "UPDATE medical_record_documents "
                "SET upload_date = COALESCE(created_at, CURRENT_TIMESTAMP) "
                "WHERE upload_date IS NULL"
            )
        )

    with op.batch_alter_table("medical_record_documents") as batch_op:
        batch_op.alter_column("storage_path", existing_type=sa.String(length=500), nullable=False)
        batch_op.alter_column("file_type", existing_type=sa.String(length=100), nullable=False)
        batch_op.alter_column("file_size", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("upload_date", existing_type=sa.DateTime(timezone=True), nullable=False)
        batch_op.create_unique_constraint("uq_record_document_storage_path", ["medical_record_id", "storage_path"])

    existing_tables = set(inspector.get_table_names())
    if "medical_record_medicines" not in existing_tables:
        op.create_table(
            "medical_record_medicines",
            sa.Column("medical_record_id", sa.Integer(), nullable=False),
            sa.Column("medicine_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["medical_record_id"],
                ["medical_records.id"],
                name="fk_medical_record_medicines_medical_record_id_medical_records",
            ),
            sa.ForeignKeyConstraint(
                ["medicine_id"],
                ["medicines.id"],
                name="fk_medical_record_medicines_medicine_id_medicines",
            ),
            sa.PrimaryKeyConstraint(
                "medical_record_id",
                "medicine_id",
                name="pk_medical_record_medicines",
            ),
        )


def downgrade() -> None:
    op.drop_table("medical_record_medicines")
    with op.batch_alter_table("medical_record_documents") as batch_op:
        batch_op.drop_constraint("uq_record_document_storage_path", type_="unique")
        batch_op.drop_column("upload_date")
        batch_op.drop_column("file_size")
        batch_op.drop_column("file_type")
        batch_op.drop_column("storage_path")
    op.drop_index("ix_medical_records_visit_date", table_name="medical_records")
    op.drop_index("ix_medical_records_folder_name", table_name="medical_records")
    with op.batch_alter_table("medical_records") as batch_op:
        batch_op.drop_column("treatment_name")
        batch_op.drop_column("visit_date")
        batch_op.drop_column("doctor_name")
        batch_op.drop_column("hospital_name")
        batch_op.drop_column("description")
        batch_op.drop_column("folder_name")
