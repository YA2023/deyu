import sys
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from influxdb_client import InfluxDBClient, Point, WriteOptions
from datetime import datetime
from time import sleep

# 接收命令行参数
if len(sys.argv) < 2:
    print("请提供直播间ID")
    sys.exit(1)

live_id = sys.argv[1]

# 设置 InfluxDB 连接信息
# url = "http://192.168.5.3:8086"    #内网
url = "http://119.188.113.120:1088" #外网
token = "fGJEZfqZaZMUPg2zFQL5nKS-7b4gkmldrBTeqBxFwxWon9OVMhjCzd3rwhTsmxpNOxw8q8CeE4o-ZBnM4BYdCA=="
org = "DeYuTech"
bucket = "web_spider"

# 创建 InfluxDB 客户端
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=WriteOptions(batch_size=1000, flush_interval=10_000))

# 检查并创建 bucket 如果不存在
buckets_api = client.buckets_api()
if not buckets_api.find_bucket_by_name(bucket):
    buckets_api.create_bucket(bucket_name=bucket, org=org)

option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = Chrome(options=option)

try:
    driver.get("https://login.taobao.com")
    sleep(3)

    with open('cookies.txt', 'r') as file:
        for line in file:
            name, value = line.strip().split('=', 1)
            cookie = {'name': name, 'value': value, 'domain': '.taobao.com'}
            driver.add_cookie(cookie)

    driver.refresh()
    sleep(3)
    driver.get(f'https://liveplatform.taobao.com/restful/index/live/control?liveId={live_id}')
    sleep(3)

    seen_comments = set()

    while True:
        try:
            comment_items = driver.find_elements(By.CLASS_NAME, "tc-comment-item")
        except:
            print("没有找到评论")
            continue

        for item in comment_items:
            try:
                username = item.find_element(By.CLASS_NAME, "tc-comment-item-userinfo-name").text.strip()
                comment_time = item.find_element(By.CLASS_NAME, "alpw-comment-time").text.strip()
                comment_content = item.find_element(By.CLASS_NAME, "tc-comment-item-content").text.strip()
                comment_id = f"{username}_{comment_time}"
                if comment_id not in seen_comments:
                    seen_comments.add(comment_id)
                    full_comment_time = f"{datetime.now().strftime('%Y-%m-%d')} {comment_time}"
                    point = Point("comment").tag("username", username).field("content", comment_content).time(full_comment_time)
                    write_api.write(bucket=bucket, record=point)
                    print(f"已添加: {username}, {full_comment_time}, {comment_content}")
            except Exception as e:
                print(f"错误详情: {e}")
        sleep(10)

finally:
    driver.quit()
    client.close()
