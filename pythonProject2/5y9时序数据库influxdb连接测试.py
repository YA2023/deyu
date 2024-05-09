from influxdb_client import InfluxDBClient

# 设置InfluxDB连接信息
url = "http://119.188.113.120:1088"
token = "fGJEZfqZaZMUPg2zFQL5nKS-7b4gkmldrBTeqBxFwxWon9OVMhjCzd3rwhTsmxpNOxw8q8CeE4o-ZBnM4BYdCA=="
org = "DeYuTech"

# 创建InfluxDB客户端
client = InfluxDBClient(url=url, token=token, org=org)

try:
    # 测试连接并获取buckets列表来验证连接
    buckets_api = client.buckets_api()
    buckets = buckets_api.find_buckets()
    if buckets:
        print("连接成功！以下是可用的Buckets:")
        for bucket in buckets.buckets:
            print(f"- {bucket.name}")
    else:
        print("没有找到任何Buckets。")
except Exception as e:
    print(f"连接失败：{e}")
finally:
    # 关闭客户端
    client.close()
