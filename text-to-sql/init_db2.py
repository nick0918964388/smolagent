import pyodbc

# 連接字串
conn_str = (
    "DRIVER={IBM DB2 ODBC DRIVER};"
    "DATABASE=maxdb76;"
    "HOSTNAME=10.10.10.115;"
    "PORT=50005;"
    "PROTOCOL=TCPIP;"
    "UID=maximo;"
    "PWD=maximo;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # 生成表描述
    updated_description = """允許您對DB2數據庫執行SQL查詢。請注意，此工具的輸出是執行結果的字符串表示。
    可以使用以下表格："""

    # 使用 DB2 系統表查詢表結構
    schema = 'MAXIMO'
    table_query = """
    SELECT TABNAME, COLNAME, TYPENAME, LENGTH, SCALE
    FROM SYSCAT.COLUMNS 
    WHERE TABSCHEMA = ? and TABNAME = 'ASSET' and COLNAME in ('ASSETNUM','SITEID','EQ1','EQ2','EQ3','EQ4')
    ORDER BY TABNAME
    """
    
    cursor.execute(table_query, (schema,))
    columns_data = cursor.fetchall()
    
    # 整理表格資訊
    table_info = {}
    for row in columns_data:
        table_name = row[0]
        column_name = row[1]
        data_type = row[2]
        length = row[3]
        scale = row[4]
        
        if table_name not in table_info:
            table_info[table_name] = []
            
        # 格式化數據類型
        if data_type in ('VARCHAR', 'CHAR'):
            type_desc = f"{data_type}({length})"
        elif data_type == 'DECIMAL':
            type_desc = f"{data_type}({length},{scale})"
        else:
            type_desc = data_type
            
        table_info[table_name].append((column_name, type_desc))
    
    # 生成描述文本
    for table_name, columns in table_info.items():
        table_description = f"\n表格 '{table_name}':\n"
        table_description += "欄位:\n" + "\n".join(
            [f"  - {name}: {col_type}" for name, col_type in columns]
        )
        updated_description += table_description
    
    print(updated_description)

except pyodbc.Error as e:
    print(f"連接或查詢DB2時發生錯誤: {str(e)}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close() 