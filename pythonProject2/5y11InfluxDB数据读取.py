from influxdb_client import InfluxDBClient, Point, WriteOptions

# 设置InfluxDB连接信息
url = "http://119.188.113.120:1088"
token = "fGJEZfqZaZMUPg2zFQL5nKS-7b4gkmldrBTeqBxFwxWon9OVMhjCzd3rwhTsmxpNOxw8q8CeE4o-ZBnM4BYdCA=="
org = "DeYuTech"

# 创建InfluxDB客户端
client = InfluxDBClient(url=url, token=token, org=org)

try:
    query_api = client.query_api()
    query = f'from(bucket: "web_spider") |> range(start: -1d)'  # 查询最近一天的数据
    result = query_api.query(org=org, query=query)

    if result:
        print("查询到的数据如下:")
        for table in result:
            for record in table.records:
                print(f'Time: {record.get_time()}, Measurement: {record.get_measurement()}, Fields: {record.values}')
    else:
        print("在指定的时间范围内没有找到数据。")
except Exception as e:
    print(f"查询失败：{e}")
finally:
    # 关闭客户端
    client.close()
