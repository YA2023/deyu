import pandas as pd
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# 读取Excel文件
df = pd.read_excel('./data/保健品部分订单.xlsx')

# 解析下单时间列为datetime格式
df['下单时间'] = pd.to_datetime(df['下单时间'], format='%Y/%m/%d %H:%M:%S')


# 定义移动平均函数
def moving_average(values, window_size):
    # 将时间戳转换为秒数进行加减运算
    values_sec = [t.timestamp() for t in values]
    return sum(values_sec[-window_size:]) / window_size


# 初始化字典存储结果
user_product_predictions = defaultdict(list)
product_user_predictions = defaultdict(list)
final_output = []

# 对买家ID和宝贝ID进行分组
grouped = df.groupby(['买家ID(客户昵称)', '【线上】宝贝ID'])

# 遍历分组
for (username, product_id), group in grouped:
    # 计算历史购买次数、总购买金额、最近购买时间
    purchase_count = len(group)
    total_purchase_amount = (group['单价'] * purchase_count).sum()
    last_purchase_time = group['下单时间'].max()

    # 判断历史购买时间数量并预测下一次购买时间
    if purchase_count == 1:
        next_purchase_time = last_purchase_time
        historical_purchase_times = [last_purchase_time]  # 添加历史购买时间列表
    else:
        historical_purchase_times = group['下单时间'].tolist()
        predicted_next_purchase_time = moving_average(historical_purchase_times, window_size=2)
        next_purchase_time = predicted_next_purchase_time

    # 更新用户-商品预测列表和商品-用户预测列表
    user_product_predictions[username, product_id] = [username, product_id, purchase_count, next_purchase_time,
                                                      historical_purchase_times]
    product_user_predictions[product_id, username] = [product_id, username, purchase_count, next_purchase_time,
                                                      historical_purchase_times]

    # 更新最终输出列表
    final_output.append(
        [username, product_id, purchase_count, total_purchase_amount, last_purchase_time, next_purchase_time])

# 计算商品一年内购买频率和预测下一次购买时间
product_purchase_freq = df.groupby('【线上】宝贝ID')['下单时间'].count()
product_avg_purchase_freq = product_purchase_freq.mean()
product_next_purchase_time = df.groupby('【线上】宝贝ID')['下单时间'].max() + pd.DateOffset(
    days=product_avg_purchase_freq)

# 输出三个列表
print("用户对不同商品的下一次购买时间预测数据:")
for key, value in user_product_predictions.items():
    print(value)

print("\n商品对不同用户的下一次购买时间预测数据:")
for key, value in product_user_predictions.items():
    print(value)

print("\n最终输出列表:")
for item in final_output:
    print(item)

print("\n商品一年内购买频率和预测下一次购买时间:")
print(product_next_purchase_time)
