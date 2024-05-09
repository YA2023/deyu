from elasticsearch import Elasticsearch, helpers
import pandas as pd
from datetime import datetime
#可指定上传列对象,可去重

# 去重函数
def record_exists(es, index, buyer_id, product_id, buyer_times):
    buyer_times_str = buyer_times.strftime('%Y/%m/%d %H:%M:%S')  # 确保日期格式正确
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"买家ID(客户昵称)": buyer_id}},
                    {"match": {"【线上】宝贝ID": product_id}},
                    {"range": {"下单时间": {"gte": buyer_times_str, "lte": buyer_times_str, "format": "yyyy/MM/dd HH:mm:ss"}}}
                ]
            }
        }
    }
    response = es.search(index=index, body=query)
    return response['hits']['total'] > 0


# 重新加载更新的Excel文件
updated_file_path = './data/万里牛测试数据分类后.xlsx'
updated_df = pd.read_excel(updated_file_path)

# 查看包含指定列的数据预览，并预处理
selected_columns = [
    '买家ID(客户昵称)', '【线上】宝贝ID', '下单时间', '单价', '数量', '【线上】商品标题', '品类'
]
updated_df = updated_df[selected_columns]

# 数据预处理
updated_df['下单时间'] = pd.to_datetime(updated_df['下单时间'], errors='coerce')  # 转换日期格式并处理无法转换的错误
updated_df.dropna(subset=['下单时间'], inplace=True)  # 删除下单时间为空的行

# 连接到Elasticsearch
es = Elasticsearch(
    hosts=[{'host': 'localhost', 'port': 9200, 'scheme': 'http'}]
)

# 定义索引映射
index_mappings = {
    "mappings": {
        "doc": {  # 使用类型名 'doc'
            "properties": {
                "买家ID(客户昵称)": {"type": "keyword"},
                "【线上】宝贝ID": {"type": "keyword"},
                "下单时间": {"type": "date", "format": "yyyy/MM/dd HH:mm:ss"},
                "单价": {"type": "float"},
                "数量": {"type": "integer"},
                "【线上】商品标题": {"type": "text"},
                "品类": {"type": "keyword"}
            }
        }
    }
}

# 创建索引
if not es.indices.exists(index='my_excel'):
    es.indices.create(index='my_excel', body=index_mappings)

# 准备数据上传
actions = []
for index, row in updated_df.iterrows():
    buyer_times = row['下单时间']
    if not record_exists(es, 'my_excel', row['买家ID(客户昵称)'], row['【线上】宝贝ID'], buyer_times):
        action = {
            "_index": "my_excel",
            "_type": "doc",
            "_source": {
                "买家ID(客户昵称)": row['买家ID(客户昵称)'] if pd.notna(row['买家ID(客户昵称)']) else "未知",
                "【线上】宝贝ID": row['【线上】宝贝ID'] if pd.notna(row['【线上】宝贝ID']) else "未知",
                "下单时间": buyer_times.strftime('%Y/%m/%d %H:%M:%S'),
                "单价": float(row['单价']) if pd.notna(row['单价']) else 0.0,
                "数量": int(row['数量']) if pd.notna(row['数量']) else 0,
                "【线上】商品标题": row['【线上】商品标题'] if pd.notna(row['【线上】商品标题']) else "无标题",
                "品类": row['品类'] if pd.notna(row['品类']) else "未分类"
            }
        }
        actions.append(action)

# 批量上传数据，如果actions列表不为空
if actions:
    helpers.bulk(es, actions)

