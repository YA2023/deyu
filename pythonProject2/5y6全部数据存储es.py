import pandas as pd
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
#万里牛数据集
#注意文件路劲,按需求修改
#输入路劲:  updated_file_path
#输出路劲:   本地es数据库  版本:5.6.8

def preprocess_data(df):
    """预处理数据，包括填充空值等操作。"""
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df.loc[:, col] = df[col].fillna(0)
        elif df[col].dtype == 'object':
            df.loc[:, col] = df[col].fillna('未知')
    return df

def process_dates(df, date_columns):
    """处理指定的日期列，转换格式并处理错误。"""
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = df[col].apply(lambda x: x.strftime('%Y/%m/%d %H:%M:%S') if pd.notnull(x) else None)
    return df

def record_exists(es, index, buyer_id, product_id, buyer_times):
    """检查 Elasticsearch 中是否存在记录，以防止重复。"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"买家ID(客户昵称).keyword": buyer_id}},
                    {"term": {"【线上】宝贝ID.keyword": product_id}},
                    {"term": {"下单时间": buyer_times}} if buyer_times else {"match_all": {}}
                ]
            }
        }
    }
    response = es.search(index=index, body=query)
    return response['hits']['total'] > 0

# 加载更新后的 Excel 文件
updated_file_path = './data/万里牛测试数据分类后.xlsx'
updated_df = pd.read_excel(updated_file_path)

# 预处理数据
updated_df = preprocess_data(updated_df)

# 指定可能包含日期数据的列
date_columns = [col for col in updated_df.columns if 'date' in col.lower() or 'time' in col.lower()]
updated_df = process_dates(updated_df, date_columns)

# 连接到 Elasticsearch
es = Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# 定义索引映射
index_mappings = {
    "mappings": {
        "doc": {
            "properties": {
                col: {"type": "text", "fields": {"keyword": {"type": "keyword"}}} for col in updated_df.columns
            }
        }
    }
}
for col in updated_df.columns:
    if updated_df[col].dtype == 'datetime64[ns]':
        index_mappings['mappings']['doc']['properties'][col] = {"type": "date", "format": "yyyy/MM/dd HH:mm:ss"}
    elif updated_df[col].dtype in ['float64', 'int64']:
        index_mappings['mappings']['doc']['properties'][col] = {"type": "long"}  # Ensure large numbers are supported

# 确保索引不存在时创建索引
if not es.indices.exists(index='my_excel_2'):
    es.indices.create(index='my_excel_2', body=index_mappings)

# 准备上传数据
actions = []
for index, row in updated_df.iterrows():
    source_data = {col: row[col] for col in updated_df.columns}
    if not record_exists(es, 'my_excel_2', row['买家ID(客户昵称)'], row['【线上】宝贝ID'], row.get('下单时间')):
        action = {
            "_index": "my_excel_2",
            "_type": "doc",
            "_source": source_data
        }
        actions.append(action)

# 批量上传数据
if actions:
    try:
        helpers.bulk(es, actions)
    except Exception as e:
        print(f"发生错误：{str(e)}")
