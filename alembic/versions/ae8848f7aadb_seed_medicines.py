"""seed_medicines

Revision ID: ae8848f7aadb
Revises: 20260713_0003
Create Date: 2026-07-21 17:27:53.328654
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

revision = 'ae8848f7aadb'
down_revision = '20260713_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Check if medicines table exists
    if 'medicines' not in inspector.get_table_names():
        return

    # Check if seed data already exists (by checking for Crocin)
    existing = bind.execute(text("SELECT COUNT(*) FROM medicines WHERE name = 'Crocin 500'")).scalar()
    if existing and existing > 0:
        return  # Seed data already present

    # Define medicines to seed
    # Format: (name, generic_name, brand_name, composition, strength, unit, dosage_form, route)
    medicines = [
        # Crocin / Paracetamol
        ("Crocin 500", "Paracetamol", "Crocin 500", "Paracetamol", "500", "mg", "tablet", "oral"),
        ("Crocin 650", "Paracetamol", "Crocin 650", "Paracetamol", "650", "mg", "tablet", "oral"),
        ("Dolo 650", "Paracetamol", "Dolo 650", "Paracetamol", "650", "mg", "tablet", "oral"),
        ("Tylenol 500", "Paracetamol", "Tylenol 500", "Paracetamol", "500", "mg", "tablet", "oral"),
        ("Paracetamol 500 Generic", "Paracetamol", None, "Paracetamol", "500", "mg", "tablet", "oral"),
        ("Paracetamol 650 Generic", "Paracetamol", None, "Paracetamol", "650", "mg", "tablet", "oral"),

        # Brufen / Ibuprofen
        ("Brufen 400", "Ibuprofen", "Brufen 400", "Ibuprofen", "400", "mg", "tablet", "oral"),
        ("Brufen 600", "Ibuprofen", "Brufen 600", "Ibuprofen", "600", "mg", "tablet", "oral"),
        ("Ibuprofen 400 Generic", "Ibuprofen", None, "Ibuprofen", "400", "mg", "tablet", "oral"),
        ("Ibuprofen 600 Generic", "Ibuprofen", None, "Ibuprofen", "600", "mg", "tablet", "oral"),

        # Augmentin / Amoxicillin + Clavulanic Acid
        ("Augmentin 625", "Amoxicillin + Clavulanic Acid", "Augmentin 625", "Amoxicillin + Clavulanic Acid", "625", "mg", "tablet", "oral"),
        ("Augmentin 1g", "Amoxicillin + Clavulanic Acid", "Augmentin 1g", "Amoxicillin + Clavulanic Acid", "1000", "mg", "tablet", "oral"),
        ("Amoxicillin Clavulanate 625 Generic", "Amoxicillin + Clavulanic Acid", None, "Amoxicillin + Clavulanic Acid", "625", "mg", "tablet", "oral"),

        # Azithral / Azithromycin
        ("Azithral 500", "Azithromycin", "Azithral 500", "Azithromycin", "500", "mg", "tablet", "oral"),
        ("Azithromycin 500 Generic", "Azithromycin", None, "Azithromycin", "500", "mg", "tablet", "oral"),

        # Additional common medicines
        ("Cetirizine 10 Generic", "Cetirizine", None, "Cetirizine", "10", "mg", "tablet", "oral"),
        ("Allegra 120", "Fexofenadine", "Allegra 120", "Fexofenadine", "120", "mg", "tablet", "oral"),
        ("Fexofenadine 120 Generic", "Fexofenadine", None, "Fexofenadine", "120", "mg", "tablet", "oral"),
        ("Pantoprazole 40 Generic", "Pantoprazole", None, "Pantoprazole", "40", "mg", "tablet", "oral"),
        ("Omeprazole 20 Generic", "Omeprazole", None, "Omeprazole", "20", "mg", "capsule", "oral"),
        ("Metformin 500 Generic", "Metformin", None, "Metformin", "500", "mg", "tablet", "oral"),
        ("Metformin 1000 Generic", "Metformin", None, "Metformin", "1000", "mg", "tablet", "oral"),
        ("Amlodipine 5 Generic", "Amlodipine", None, "Amlodipine", "5", "mg", "tablet", "oral"),
        ("Losartan 50 Generic", "Losartan", None, "Losartan", "50", "mg", "tablet", "oral"),
    ]

    # Insert medicines
    medicines_table = sa.Table(
        'medicines',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('generic_name', sa.String(255), nullable=True),
        sa.Column('brand_name', sa.String(255), nullable=True),
        sa.Column('composition', sa.Text, nullable=True),
        sa.Column('strength', sa.String(100), nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('dosage_form', sa.String(50), nullable=False),
        sa.Column('route', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    for med in medicines:
        op.execute(
            medicines_table.insert().values(
                name=med[0],
                generic_name=med[1],
                brand_name=med[2],
                composition=med[3],
                strength=med[4],
                unit=med[5],
                dosage_form=med[6],
                route=med[7],
                is_deleted=False,
            )
        )


def downgrade() -> None:
    # Remove seeded medicines by name patterns
    bind = op.get_bind()
    bind.execute(text("""
        DELETE FROM medicines
        WHERE name IN (
            'Crocin 500', 'Crocin 650', 'Dolo 650', 'Tylenol 500',
            'Paracetamol 500 Generic', 'Paracetamol 650 Generic',
            'Brufen 400', 'Brufen 600', 'Ibuprofen 400 Generic', 'Ibuprofen 600 Generic',
            'Augmentin 625', 'Augmentin 1g', 'Amoxicillin Clavulanate 625 Generic',
            'Azithral 500', 'Azithromycin 500 Generic',
            'Cetirizine 10 Generic', 'Allegra 120', 'Fexofenadine 120 Generic',
            'Pantoprazole 40 Generic', 'Omeprazole 20 Generic',
            'Metformin 500 Generic', 'Metformin 1000 Generic',
            'Amlodipine 5 Generic', 'Losartan 50 Generic'
        )
    """))