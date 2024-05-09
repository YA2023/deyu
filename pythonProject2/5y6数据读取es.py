from elasticsearch import Elasticsearch
import pandas as pd

# Elasticsearch 相关信息
es_host = 'localhost'  # Elasticsearch 服务器地址
es_port = 9200  # Elasticsearch 服务器端口
index_name = 'my_excel_2'  # Elasticsearch 索引名称

# 连接 Elasticsearch
es = Elasticsearch([{'host': es_host, 'port': es_port}])

# 查询所有数据
query = {
    "query": {
        "match_all": {}
    }
}

# 从 Elasticsearch 中获取数据
response = es.search(index=index_name, body=query, size=1000)  # 限制返回的最大数据量为 1000 条

# 将数据转换为 DataFrame
data = [hit["_source"] for hit in response["hits"]["hits"]]
df = pd.DataFrame(data)

# 打印 DataFrame
print(df.head())  # 打印前几行数据
