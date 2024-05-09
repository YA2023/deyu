import pandas as pd
from sqlalchemy import create_engine

# 读取 Excel 文件
excel_file = './data/宝贝报表.xlsx'
df = pd.read_excel(excel_file)

# 连接到 MySQL 数据库
username = 'root'      # 替换为你的MySQL用户名
password = '123456'    # 替换为你的MySQL密码
host = 'localhost'     # 或者MySQL服务器的IP地址
database = 'deyuceshi' # 你要连接的数据库名
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database}')

# 指定要读取和写入的表名
table_name = 'ceshi'

# 尝试读取数据库中已存在的表，如果不存在则创建一个空的DataFrame
try:
    existing_df = pd.read_sql_table(table_name, engine)
except ValueError as e:
    existing_df = pd.DataFrame()

# 将新数据追加到已有数据上，并去重
combined_df = pd.concat([existing_df, df]).drop_duplicates()

# 将去重后的数据写回数据库，替换原有表
combined_df.to_sql(table_name, engine, index=False, if_exists='replace')

# 提交更改并关闭连接
engine.dispose()
