# from init import engine
from sqlalchemy import text
from smolagents import tool
import ibm_db

@tool
def sql_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the table. Returns a string representation of the result.
    The table is named 'receipts'. Its description is as follows:
        Columns:
        - receipt_id: INTEGER
        - customer_name: VARCHAR(16)
        - price: FLOAT
        - tip: FLOAT

    Args:
        query: The query to perform. This should be correct SQL.
    """
    output = ""
    with engine.connect() as con:
        rows = con.execute(text(query))
        for row in rows:
            output += "\n" + str(row)
    return output

@tool
def sql_engine_db2_asset(query: str) -> str:
    """
    Allows you to perform SQL queries on the DB2 database. Returns a string representation of the result.
    The tables are:
    Table 'ASSET':
    - ASSETNUM: VARCHAR(20)
    - SITEID: VARCHAR(16)
    - EQ1 (as REPAIRFAC): VARCHAR(16)
    - EQ2 (as DEPARTMENT): VARCHAR(16)

    Table 'ZZ_DEPT':
    - DEPARTMENT: VARCHAR(16)
    - DESCRIPTION: VARCHAR(50)

    Args:
        query: The query to perform. This should be correct SQL.
    """
    # DB2数据库连接配置
    connection_string = (
        'DATABASE=maxdb76;'
        'HOSTNAME=10.10.10.115;'
        'PORT=50005;'
        'PROTOCOL=TCPIP;'
        'UID=maximo;'
        'PWD=maximo;'
        'CURRENTSCHEMA=MAXIMO;'
    )
    
    output = ""
    try:
        # 连接到DB2
        conn = ibm_db.connect(connection_string, '', '')
        
        # 执行查询
        stmt = ibm_db.exec_immediate(conn, query)
        
        # 获取结果
        result = ibm_db.fetch_assoc(stmt)
        while result:
            # 将字典转换为字符串并添加到输出
            row_str = ", ".join([f"{k}: {v}" for k, v in result.items()])
            output += "\n" + row_str
            result = ibm_db.fetch_assoc(stmt)
            
    except Exception as e:
        output = f"查询错误: {str(e)}"
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)
            
    return output

@tool
def sql_engine_db2_carava(query: str) -> str:
    """
    
    """
    # DB2数据库连接配置
    connection_string = (
        'DATABASE=maxdb76;'
        'HOSTNAME=10.10.10.115;'
        'PORT=50005;'
        'PROTOCOL=TCPIP;'
        'UID=maximo;'
        'PWD=maximo;'
        'CURRENTSCHEMA=MAXIMO;'
    )
    
    output = ""
    try:
        # 连接到DB2
        conn = ibm_db.connect(connection_string, '', '')
        
        # 执行查询
        stmt = ibm_db.exec_immediate(conn, query)
        
        # 获取结果
        result = ibm_db.fetch_assoc(stmt)
        while result:
            # 将字典转换为字符串并添加到输出
            row_str = ", ".join([f"{k}: {v}" for k, v in result.items()])
            output += "\n" + row_str
            result = ibm_db.fetch_assoc(stmt)
            
    except Exception as e:
        output = f"查询错误: {str(e)}"
    finally:
        if 'conn' in locals():
            ibm_db.close(conn)
            
    return output