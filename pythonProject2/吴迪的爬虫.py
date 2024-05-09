import csv
import time
from time import sleep
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
#我的谷歌浏览器版本号: 124.0.6367.119 (正式版本) （64 位） (cohort: Stable) 

# 创建 ChromeOptions 对象并添加调试选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 启动 Chrome 浏览器
driver = webdriver.Chrome(options=chrome_options)

print(driver.title)

driver.get('https://liveplatform.taobao.com/restful/index/live/control?liveId=455518116401')
# CSV文件头
csv_headers = ['Username', 'Comment Time', 'Comment Content']
# 获取当前时间
current_time = datetime.now()
formatted_time = current_time.strftime('%Y%m%d%H%M')
csv_path = f'comments{formatted_time}.csv'
# 创建或打开CSV文件并写入表头
with open(csv_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)

try:
    seen_comments = set()  # 存储已经看到的评论的标识符，以避免重复

    while True:  # 持续监控直到手动停止
        comment_items = []
        try:
            comment_items = driver.find_elements(By.CLASS_NAME, "tc-comment-item")
        except:
            print("No comments found")
        # print(comment_items)
        for item in comment_items:
            # 提取信息
            try:
                username = item.find_element(By.CLASS_NAME, "tc-comment-item-userinfo-name").text.strip()
                comment_time = item.find_element(By.CLASS_NAME, "alpw-comment-time").text.strip()
                comment_content = item.find_element(By.CLASS_NAME, "tc-comment-item-content").text.strip()
                # print(username, comment_time, comment_content)
                # 使用用户名和评论时间作为唯一标识符，避免重复
                comment_id = f"{comment_content}_{comment_time}"
                if comment_id not in seen_comments:
                    seen_comments.add(comment_id)
                    # 将当前日期添加到评论时间中
                    full_comment_time = f"{current_time.strftime('%Y-%m-%d')} {comment_time}"

                    # 将评论信息保存到CSV文件
                    with open(csv_path, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([username, full_comment_time, comment_content])
                    print(f"Added: {username}, {full_comment_time}, {comment_content}")
            except:
                print("Error extracting comment details")
        # 等待一段时间后再次检查新评论
        time.sleep(10)  # 适当调整等待时间

finally:
    driver.quit()
