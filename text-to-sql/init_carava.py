# 定义表结构
TABLES_SCHEMA = {
    'ZZ_V_DAILYDYNAMIC': {
        '車種': {'type': 'VARCHAR(20)', 'comment': '車種'},
        '段所': {'type': 'VARCHAR(16)', 'comment': '部門或單位名稱'},
        '車型': {'type': 'VARCHAR(16)', 'comment': '車輛類型'},
        '配屬(A)': {'type': 'VARCHAR(16)', 'comment': '配屬數量'},
        '借出(B)': {'type': 'VARCHAR(16)', 'comment': '借出數量'},
        '借入(C)': {'type': 'VARCHAR(16)', 'comment': '借入數量'},
        '現有(D)': {'type': 'VARCHAR(16)', 'comment': '現有數量'},
        '定期(E)': {'type': 'VARCHAR(16)', 'comment': '定期數量'},
        '臨時(F)': {'type': 'VARCHAR(16)', 'comment': '配屬數量'},
        '預備(G)': {'type': 'VARCHAR(16)', 'comment': '配屬數量'},
        'W或保養(H)': {'type': 'VARCHAR(16)', 'comment': '保養數量'},
        '段修(I)': {'type': 'VARCHAR(16)', 'comment': '段修數量'},
        '待料待修(K)': {'type': 'VARCHAR(16)', 'comment': '待料待修數量'},
        '無火迴送(L)': {'type': 'VARCHAR(16)', 'comment': '無火迴送數量'},
        '停用(M)': {'type': 'VARCHAR(16)', 'comment': '停用數量'},
        '備註': {'type': 'VARCHAR(16)', 'comment': '備註'},            
    }
}

try:
    # 初始化updated_description
    carava_description = """Allows you to perform SQL queries on the table. Beware that this tool's output is a string representation of the execution output.
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
        
        carava_description += table_description.rstrip()
    
    # 添加额外说明
    carava_description += "\n\n 配置數量、借出數量、借入數量、現有數量、定期數量、段修數量、待料待修數量、無火迴送數量、停用數量、備註 的相關查詢"
    
    print(carava_description)

except Exception as e:
    print(f"连接或查询DB2时发生错误: {str(e)}")
finally:
    try:
        if 'conn' in locals():
            ibm_db.close(conn)
    except Exception as e:
        print(f"关闭连接时发生错误: {str(e)}") 