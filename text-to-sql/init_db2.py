import os
import sys


# 设置系统编码
if sys.platform.startswith('win'):
    os.add_dll_directory(r"C:\Program Files\IBM\SQLLIB\BIN")

import ibm_db

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

# 定义表结构
TABLES_SCHEMA = {
    'ASSET': {
        'ASSETNUM': {'type': 'VARCHAR(20)', 'comment': '資產編號'},
        'SITEID': {'type': 'VARCHAR(16)', 'comment': '站點代碼'},
        'EQ1': {'type': 'VARCHAR(16)', 'comment': '設備類型', 'alias': 'REPAIRFAC'},
        'EQ2': {'type': 'VARCHAR(16)', 'comment': '部門代碼', 'alias': 'DEPARTMENT'}
    },
    'ZZ_DEPT': {
        'DEPARTMENT': {'type': 'VARCHAR(16)', 'comment': '部門代碼'},
        'DESCRIPTION': {'type': 'VARCHAR(50)', 'comment': '部門名稱'}
    }
}

try:
    # 使用ibm_db直接连接
    conn = ibm_db.connect(connection_string, '', '')
    
    # 初始化updated_description
    updated_description = """Allows you to perform SQL queries on the table. Beware that this tool's output is a string representation of the execution output.
It can use the following tables:"""

    # 遍历所有表生成描述
    for table_name, columns in TABLES_SCHEMA.items():
        table_description = f"\n\nTable '{table_name}':\nColumns:\n"
        
        for col_name, col_info in columns.items():
            # 组合注释信息
            comments = []
            if 'alias' in col_info:
                comments.append(f"as {col_info['alias']}")
            if col_info['comment']:
                comments.append(col_info['comment'])
            
            comment_str = ' | '.join(comments) if comments else 'No comment'
            table_description += f"  - {col_name}: {col_info['type']} ({comment_str})\n"
        
        updated_description += table_description.rstrip()
    
    # 添加额外说明
    updated_description += "\n\n機務段是部門名稱 , 資產編號表示車號"
    
    print(updated_description)

except Exception as e:
    print(f"连接或查询DB2时发生错误: {str(e)}")
finally:
    try:
        if 'conn' in locals():
            ibm_db.close(conn)
    except Exception as e:
        print(f"关闭连接时发生错误: {str(e)}") 