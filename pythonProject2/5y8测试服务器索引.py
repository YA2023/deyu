from elasticsearch import Elasticsearch

# Elasticsearch服务器地址和端口
host = "https://119.188.113.120"
port = 8992

# Elasticsearch账号和密码
username = "deyuTech"
password = "deyuES%"

# 创建Elasticsearch连接
es = Elasticsearch([f"{host}:{port}"], http_auth=(username, password), scheme="https", verify_certs=False)

# 查询my_excel_2索引中的所有文档
index_name = "my_excel_2"
query = {
    "query": {
        "match_all": {}
    }
}

# 发送查询请求并获取结果
result = es.search(index=index_name, body=query)

# 打印查询结果
for hit in result['hits']['hits']:
    print(hit['_source'])

# # 发送count请求并获取结果
# result = es.count(index=index_name, body=query)
#
# # 打印索引中的文档数量
# print(f"索引 {index_name} 中共有 {result['count']} 条文档")
