from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

# Elasticsearch服务器地址和端口
host = "https://119.188.113.120"
port = 8992

# Elasticsearch账号和密码
username = "deyuTech"
password = "deyuES%"

# 创建Elasticsearch连接
es = Elasticsearch([f"{host}:{port}"], http_auth=(username, password), scheme="https", verify_certs=False)

# 要删除的索引名称
index_name = "my_excel_2"

# 尝试删除索引
try:
    es.indices.delete(index=index_name)
    print(f"索引 {index_name} 删除成功")
except NotFoundError:
    print(f"索引 {index_name} 不存在")
except Exception as e:
    print(f"删除索引 {index_name} 出现异常: {e}")
