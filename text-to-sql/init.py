from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Float,
    insert,
    inspect,
    text,
)


engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

# create city SQL table
table_name = "asset"
asset = Table(
    table_name,
    metadata_obj,
    Column("assetnum", String(20), primary_key=True),
    Column("siteid", String(16), primary_key=True),    
    Column("eq1", String(16)),
    Column("deptid", String(16), foreign_key="dept.deptid"),
    Column("eq3", String(16)),
    Column("eq4", String(16)),
)
metadata_obj.create_all(engine)

rows = [
    {"assetnum": "EMU901", "siteid": "TRATW", "eq1": "WAY00", "deptid": "MGY00", "eq3": "EMU", "eq4": "EMU900"},
    {"assetnum": "EMU902", "siteid": "TRATW", "eq1": "WAY00", "deptid": "MGY00", "eq3": "EMU", "eq4": "EMU900"},
    {"assetnum": "EMU903", "siteid": "TRATW", "eq1": "WAY00", "deptid": "MHY10", "eq3": "EMU", "eq4": "EMU900"},
    {"assetnum": "EMU904", "siteid": "TRATW", "eq1": "WAY00", "deptid": "MHY10", "eq3": "EMU", "eq4": "EMU900"},
]
for row in rows:
    stmt = insert(asset).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

# inspector = inspect(engine)
# columns_info = [(col["name"], col["type"]) for col in inspector.get_columns("receipts")]

# table_description = "Columns:\n" + "\n".join([f"  - {name}: {col_type}" for name, col_type in columns_info])
# print(table_description)

table_name = "dept"
dept = Table(
    table_name,
    metadata_obj,
    Column("deptid", String(16), primary_key=True),
    Column("description", String(50)),
)
metadata_obj.create_all(engine)

rows = [
    {"deptid": "MGY00", "description": "七堵機務段"},
    {"deptid": "MHY10", "description": "新竹機務段"},
]
for row in rows:
    stmt = insert(dept).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)


updated_description = """Allows you to perform SQL queries on the table. Beware that this tool's output is a string representation of the execution output.
It can use the following tables:"""

inspector = inspect(engine)
for table in ["asset", "dept"]:
    columns_info = [(col["name"], col["type"]) for col in inspector.get_columns(table)]

    table_description = f"Table '{table}':\n"

    table_description += "Columns:\n" + "\n".join([f"  - {name}: {col_type}" for name, col_type in columns_info])
    updated_description += "\n\n" + table_description

print(updated_description)

        