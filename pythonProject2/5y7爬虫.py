import csv
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions

option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = Chrome(options=option)

# 设置Chrome选项以使用已有的Chrome实例
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# driver = webdriver.Chrome(options=chrome_options)

try:
    # 访问登录后的直播后台页面
    driver.get('https://liveplatform.taobao.com/restful/index/live/control?liveId=455518116401')
    sleep(3)  # 等待页面加载完毕

    # 检查是否需要登录（根据页面元素）
    if driver.find_elements(By.ID, "identity"):  # 假设需要登录的页面会有id为'identity'的元素
        # 加载Cookie并刷新页面，这里需要你提前导出登录后的Cookie
        with open('cookies.txt', 'r') as file:
            for line in file:
                name, value = line.strip().split('=', 1)
                driver.add_cookie({'name': name, 'value': value})

        driver.refresh()  # 使用加载的Cookies刷新页面
        sleep(3)  # 等待页面重新加载

    # 开始处理CSV文件和读取评论
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

    seen_comments = set()  # 存储已经看到的评论的标识符，以避免重复

    while True:
        comment_items = []
        try:
            comment_items = driver.find_elements(By.CLASS_NAME, "tc-comment-item")
        except:
            print("No comments found")

        for item in comment_items:
            # 提取信息
            try:
                username = item.find_element(By.CLASS_NAME, "tc-comment-item-userinfo-name").text.strip()
                comment_time = item.find_element(By.CLASS_NAME, "alpw-comment-time").text.strip()
                comment_content = item.find_element(By.CLASS_NAME, "tc-comment-item-content").text.strip()
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
        sleep(10)

finally:
    driver.quit()
