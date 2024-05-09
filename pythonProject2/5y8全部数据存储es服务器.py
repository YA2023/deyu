import pandas as pd
from elasticsearch import Elasticsearch, helpers
from datetime import datetime

# 预处理数据函数，用于填充空值
def preprocess_data(df):
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
        elif df[col].dtype == 'object':
            df[col] = df[col].fillna('未知')
    return df

# 处理日期数据函数
def process_dates(df, date_columns):
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = df[col].apply(lambda x: x.strftime('%Y/%m/%d %H:%M:%S') if pd.notnull(x) else None)
    return df

# 检查记录是否已存在于 Elasticsearch 中
def record_exists(es, index, buyer_id, product_id, buyer_times):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"buyer_nickname.keyword": buyer_id}},
                    {"term": {"online_product_id.keyword": product_id}},
                    {"term": {"order_time": buyer_times}} if buyer_times else {"match_all": {}}
                ]
            }
        }
    }
    response = es.search(index=index, body=query)
    return response['hits']['total']['value'] > 0  # 注意这里修改了返回结果的处理方式

# 映射中文列名到英文
column_mapping = {
    '店铺名称': 'store_name',
    '订单号': 'order_number',
    '系统单号': 'system_order_number',
    '外部单号': 'external_order_number',
    '原始单号（原平台分销订单号）': 'original_order_number',
    '订单标记': 'order_tag',
    '异常类型': 'abnormal_type',
    '应收总计': 'total_receivable',
    '买家实付': 'buyer_payment',
    '优惠总计': 'total_discount',
    '仓库编码': 'warehouse_code',
    '仓库名称': 'warehouse_name',
    '买家留言': 'buyer_message',
    '线上备注': 'online_remark',
    '系统备注': 'system_remark',
    '打印备注': 'print_remark',
    '系统订单状态': 'system_order_status',
    '线上订单状态': 'online_order_status',
    '批次流水号': 'batch_serial_number',
    '商品成本(订单)': 'product_cost_order',
    '预计送达时间': 'estimated_delivery_time',
    '附加信息': 'additional_info',
    '商品总数': 'total_products',
    '商品概况': 'product_overview',
    '出库单号': 'stock_out_number',
    '明细状态': 'detail_status',
    '原订单号': 'original_order_id',
    '商品编码': 'product_code',
    '商品名称': 'product_name',
    '规格名称': 'specification_name',
    '【线上】商品编码': 'online_product_code',
    '【线上】商品标题': 'online_product_title',
    '【线上】规格': 'online_specification',
    '【线上】宝贝ID': 'online_product_id',
    '品牌': 'brand',
    '条码': 'barcode',
    '商品成本(明细)': 'product_cost_detail',
    '参考进价': 'reference_purchase_price',
    '单价': 'unit_price',
    '折后单价': 'discounted_price',
    '数量': 'quantity',
    '单位': 'unit',
    '应收': 'receivable',
    '销售金额': 'sales_amount',
    '仓库成本(明细)': 'warehouse_cost_detail',
    '明细备注': 'detail_remark',
    '达人ID': 'influencer_id',
    '达人昵称': 'influencer_nickname',
    '流量来源': 'traffic_source',
    '库存状况': 'stock_status',
    '预计发货时间': 'expected_shipping_time',
    '明细类型': 'detail_type',
    '发票抬头': 'invoice_title',
    '开票内容': 'invoice_content',
    '开户银行': 'bank_name',
    '银行账户': 'bank_account',
    '开票税号': 'tax_number',
    '开票地址': 'invoice_address',
    '开票电话': 'invoice_phone',
    '开票邮箱': 'invoice_email',
    '开票备注': 'invoice_remark',
    '开票类型': 'invoice_type',
    '快递公司': 'courier_company',
    '快递单号': 'courier_number',
    '多包裹': 'multiple_packages',
    '包裹数量': 'number_of_packages',
    '快递成本': 'courier_cost',
    '仓库成本': 'warehouse_cost',
    '估重': 'estimated_weight',
    '称重': 'weighing',
    '体积': 'volume',
    '运费': 'freight',
    '服务费': 'service_fee',
    '买家ID(客户昵称)': 'buyer_id',
    '收货人': 'recipient',
    '身份证号': 'id_number',
    '身份证姓名': 'id_name',
    '手机/电话': 'phone',
    '省': 'province',
    '市': 'city',
    '区': 'district',
    '详细地址': 'detailed_address',
    '邮编': 'zipcode',
    '下单时间': 'order_time',
    '付款时间': 'payment_time',
    '打单时间': 'printing_time',
    '发货时间': 'shipping_time',
    '完成时间': 'completion_time',
    '审单时间': 'audit_time',
    '交易佣金': 'transaction_commission',
    '信用卡佣金': 'credit_card_commission',
    '返点积分': 'rebate_points',
    '审单员': 'auditor',
    '财审员': 'financial_auditor',
    '打单员': 'printer',
    '配货员': 'distributor',
    '验货员': 'inspector',
    '打包员': 'packer',
    '称重员': 'weigher',
    '发货员': 'shipper',
    '业务员': 'salesman',
    '定金': 'deposit',
    '代发店铺': 'consignment_store',
    '关联售后单': 'related_aftersales_order',
    '商品货号': 'product_item_number',
    '商品默认供应商': 'default_supplier',
    '材质': 'material',
    '成分含量': 'composition',
    '面料': 'fabric',
    '上市年份/季节': 'season_year',
    '年份季节': 'year_season',
    '上市年份季节': 'listed_year_season',
    '帮面材质': 'upper_material',
    '后跟高': 'heel_height',
    '跟底款式': 'sole_style',
    '质地': 'texture',
    '裤长': 'trouser_length',
    '厚薄': 'thickness',
    '功能用途': 'functional_use',
    '预计发货时间（订单）': 'expected_order_shipping_time',
    '原始平台': 'original_platform',
    '品类': 'category'
}

# 加载 Excel 数据
updated_file_path = './data/万里牛测试数据分类后.xlsx'
updated_df = pd.read_excel(updated_file_path)

# 应用列名映射
updated_df.rename(columns=column_mapping, inplace=True)

# 数据预处理
updated_df = preprocess_data(updated_df)
date_columns = [col for col in updated_df.columns if 'date' in col.lower() or 'time' in col.lower()]
updated_df = process_dates(updated_df, date_columns)

# 连接到 Elasticsearch，设置认证和安全连接
es = Elasticsearch(
    hosts=[{'host': '119.188.113.120', 'port': 8992, 'scheme': 'https'}],
    http_auth=('deyuTech', 'deyuES%'),
    use_ssl=True,
    verify_certs=False
)

# 定义索引映射
index_mappings = {
    "properties": {
        col: {"type": "text", "fields": {"keyword": {"type": "keyword"}}} for col in updated_df.columns
    }
}
for col in updated_df.columns:
    if updated_df[col].dtype == 'datetime64[ns]':
        index_mappings['properties'][col] = {"type": "date", "format": "yyyy/MM/dd HH:mm:ss"}
    elif updated_df[col].dtype in ['float64', 'int64']:
        index_mappings['properties'][col] = {"type": "long"}

# 创建索引，如果不存在
if not es.indices.exists(index='my_excel_2'):
    es.indices.create(index='my_excel_2', body={"mappings": index_mappings})

# 准备数据并上传到 Elasticsearch
actions = []
for index, row in updated_df.iterrows():
    source_data = {col: row[col] for col in updated_df.columns}
    if not record_exists(es, 'my_excel_2', row['buyer_id'], row['online_product_id'], row.get('order_time')):
        action = {
            "_index": "my_excel_2",
            "_source": source_data
        }
        actions.append(action)

# 使用 helpers.bulk 批量上传数据
if actions:
    try:
        helpers.bulk(es, actions)
    except Exception as e:
        print(f"发生错误：{str(e)}")
