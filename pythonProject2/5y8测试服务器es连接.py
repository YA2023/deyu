from elasticsearch import Elasticsearch

def test_es_connection():
    # 创建Elasticsearch客户端实例
    es = Elasticsearch(
        hosts=[{'host': '119.188.113.120', 'port': 8992, 'scheme': 'https'}],
        http_auth=('deyuTech', 'deyuES%'),
        use_ssl=True,
        verify_certs=False  # 如果使用自签名证书，设为False；如果有权威证书，设置为True并提供CA证书路径
    )

    # 获取并打印Elasticsearch集群的健康状况
    try:
        health = es.cluster.health()
        print("Elasticsearch cluster health:")
        print(health)
    except Exception as e:
        print("Failed to connect to Elasticsearch:")
        print(str(e))

test_es_connection()
