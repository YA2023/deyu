import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt


# 读取Excel文件
df = pd.read_excel('./data/保健品部分订单.xlsx')

# 解析下单时间列为datetime格式
df['下单时间'] = pd.to_datetime(df['下单时间'], format='%Y/%m/%d %H:%M:%S')

# 计算当前时间
current_time = datetime.now()

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

    # 计算购买频率
    purchase_duration = (current_time - group['下单时间'].min()).total_seconds()
    purchase_frequency = purchase_count / ((purchase_duration / (365 * 24 * 60 * 60)) or 1)  # 避免除以零

    # 判断历史购买时间数量并预测下一次购买时间
    if purchase_count == 1:
        next_purchase_time = last_purchase_time
        historical_purchase_times = [last_purchase_time]
    else:
        historical_purchase_times = group['下单时间'].tolist()
        # 使用移动平均法预测下一次购买时间
        predicted_next_purchase_time = sum([t.timestamp() for t in historical_purchase_times[-2:]]) / 2
        next_purchase_time = datetime.fromtimestamp(predicted_next_purchase_time)

    # 更新用户-商品预测列表和商品-用户预测列表
    user_product_predictions[username, product_id] = [username, product_id, purchase_count, next_purchase_time,
                                                      historical_purchase_times]
    product_user_predictions[product_id, username] = [product_id, username, purchase_count, next_purchase_time,
                                                      historical_purchase_times]

    # 更新最终输出列表
    final_output.append(
        [username, product_id, purchase_frequency, total_purchase_amount, last_purchase_time, next_purchase_time])

# 输出三个列表
user_product_predictions_list = list(user_product_predictions.values())
product_user_predictions_list = list(product_user_predictions.values())

# 输出最终结果
final_output_df = pd.DataFrame(final_output,
                                columns=['用户名', '商品id', '此商品一年内购买频率', '此商品一年内总购买金额', '此商品最近的一次购买时间', '此商品预测下一次的购买时间'])

# 选择被购买次数最多的商品展示
most_purchased_product = final_output_df[final_output_df['此商品一年内购买频率'] == final_output_df['此商品一年内购买频率'].max()]

# 展示结果
print("用户对不同商品的下一次购买时间预测数据：")
print(user_product_predictions_list)
print("\n商品对不同用户的下一次购买时间预测数据：")
print(product_user_predictions_list)
print("\n最终输出列表：")
print(final_output_df)
print("\n被购买次数最多的商品展示：")
print(most_purchased_product)

# # 将最终的 pandas DataFrame 转换为列表
# final_output_list = most_purchased_product.values.tolist()
#
# # 展示转换后的列表
# print(final_output_list)

# 获取购买频率最高的商品数据
most_purchased_item = max(final_output_df, key=lambda x: x[2])

# 提取商品信息
product_id = most_purchased_item[1]
purchase_frequency = most_purchased_item[2]

# 创建柱状图
plt.bar(product_id, purchase_frequency)
plt.xlabel('商品ID')
plt.ylabel('购买频率')
plt.title('购买频率最高的商品')
plt.show()

