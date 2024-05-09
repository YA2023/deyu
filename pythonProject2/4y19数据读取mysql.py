import pandas as pd
from sqlalchemy import create_engine

# 连接到 MySQL 数据库
username = 'root'       # 替换为你的MySQL用户名
password = '123456'     # 替换为你的MySQL密码
host = 'localhost'      # 或者MySQL服务器的IP地址
database = 'deyuceshi'  # 你要连接的数据库名
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database}')

# 指定要读取的表名
table_name = 'ceshi'

# 从数据库中读取表
df = pd.read_sql_table(table_name, engine)

# 显示数据，或者进一步处理
print(df)

# 关闭数据库连接
engine.dispose()
