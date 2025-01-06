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
    ForeignKey,
)


engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

# 首先创建dept表
table_name = "dept"
dept = Table(
    table_name,
    metadata_obj,
    Column("deptid", String(16), primary_key=True, comment="部門代碼"),
    Column("description", String(50), comment="部門名稱"),
)
metadata_obj.create_all(engine)

# 插入dept数据
rows = [
    {"deptid": "MGY00", "description": "七堵機務段"},
    {"deptid": "MHY10", "description": "新竹機務段"},
]
for row in rows:
    stmt = insert(dept).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

# 然后创建asset表
table_name = "asset"
asset = Table(
    table_name,
    metadata_obj,
    Column("assetnum", String(20), primary_key=True, comment="資產編號"),
    Column("siteid", String(16), primary_key=True, comment="站點代碼"),    
    Column("eq1", String(16), comment="設備類型"),
    Column("deptid", String(16), ForeignKey("dept.deptid"), comment="部門代碼"),
    Column("eq3", String(16), comment="設備子類型"),
    Column("eq4", String(16), comment="設備型號"),
)
metadata_obj.create_all(engine)

# 插入asset数据
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

# 生成表描述
updated_description = """Allows you to perform SQL queries on the table. Beware that this tool's output is a string representation of the execution output.
It can use the following tables:"""

inspector = inspect(engine)
for table in ["asset", "dept"]:
    columns_info = inspector.get_columns(table)
    table_description = f"Table '{table}':\n"
    table_description += "Columns:\n"
    
    for col in columns_info:
        col_name = col['name']
        col_type = col['type']
        # SQLite不支持原生的列注释，所以我们需要从Table对象中获取
        if table == "asset":
            comment = asset.c[col_name].comment or 'No comment'
        else:
            comment = dept.c[col_name].comment or 'No comment'
        
        table_description += f"  - {col_name}: {col_type} ({comment})\n"
    
    updated_description += "\n\n" + table_description.rstrip()

print(updated_description)

        