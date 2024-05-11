import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# 假设的列名到英文的映射字典
column_mapping = {
    '序号': 'serial_number',
    '商品id': 'product_id',
    '标题': 'title',
    '商品链接': 'product_url',
    'SKUID': 'sku_id',
    'sku名称': 'sku_name',
    'sku备注': 'sku_comment',
    # '高清颜色属性图': 'high_definition_color_attribute_image',
    '价格': 'value',
    '库存': 'Inventory',
    # '高清商品主图': 'high_definition_product_main_image'
    '商品状态': 'product_status'
}

# 加载Excel文件
file_path = 'E:\千牛商品/掌中宝商品_商品管理_商品列表1245.xlsx'
df = pd.read_excel(file_path)

# 应用列名映射
df.rename(columns=column_mapping, inplace=True)

# 检查并补全[商品id, 标题, 商品链接]为空的行
df[['product_id', 'title', 'product_url']] = df[['product_id', 'title', 'product_url']].ffill()
# 处理商品状态为空的行
df['product_status'] = df['product_status'].ffill()


# 删除SKUID为空的行
df.dropna(subset=['sku_id'], inplace=True)

# 处理其他为空的值，这里要确保填充类型与列类型兼容
df = df.apply(lambda x: x.fillna('未知') if x.dtype == 'object' else x.fillna(0))

# 连接到 Elasticsearch
es = Elasticsearch(
    hosts=[{'host': '119.188.113.120', 'port': 8992, 'scheme': 'https'}],
    http_auth=('deyuTech', 'deyuES%'),
    use_ssl=True,
    verify_certs=False
)

# 确保索引存在，如果不存在则创建
index_name = 'goods'
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

# 准备数据批量上传到 Elasticsearch
actions = [
    {
        "_index": index_name,
        "_source": row.to_dict()
    }
    for index, row in df.iterrows()
]

# 批量写入数据到 Elasticsearch
bulk(es, actions)

# 打印最终的表格
print(df)
