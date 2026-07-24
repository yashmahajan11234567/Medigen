with open(r"C:\\Users\\hitoy\\Downloads\\Medigen\\app\\models\\inventory.py", "r") as f:
    content = f.read()

# Add event import
content = content.replace(
    "from sqlalchemy import Date, Enum as SqlEnum, Float, ForeignKey, Index, String, Text, UniqueConstraint, text",
    "from sqlalchemy import Date, Enum as SqlEnum, Float, ForeignKey, Index, String, Text, UniqueConstraint, text, event"
)  

# Replace the UniqueConstraint block
content = content.replace(
    '''        UniqueConstraint(
            "user_id",
            "medicine_id",
            "expiry_date",
            name="uq_inventory_user_medicine_expiry_active",
            sqlite_where=text("is_deleted = 0"),
            postgresql_where=text("is_deleted = false"),
        ),''',
    '''        UniqueConstraint(
            "user_id",
            "medicine_id",
            "expiry_date",
            name="uq_inventory_user_medicine_expiry_active",
        ),'''
)

# Add event listener at the end
content = content.rstrip() + '''

# Create partial unique index for SQLite and PostgreSQL after table creation
@event.listens_for(InventoryItem.__table__, "after_create")
def create_partial_unique_index(target, connection, **kw):
    dialect_name = connection.dialect.name
    if dialect_name == "sqlite":
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_user_medicine_expiry_active "
                "ON inventory (user_id, medicine_id, expiry_date) WHERE is_deleted = 0"
            )
        )
    elif dialect_name == "postgresql":
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_user_medicine_expiry_active "
                "ON inventory (user_id, medicine_id, expiry_date) WHERE is_deleted = false"
            )
        )
'''

with open(r"C:\\Users\\hitoy\\Downloads\\Medigen\\app\\models\\inventory.py", "w") as f:
    f.write(content)
print("Done")
