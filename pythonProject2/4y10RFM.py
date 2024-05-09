import pandas as pd
from datetime import datetime
from collections import defaultdict
import streamlit as st  # 导入Streamlit库
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
        next_purchase_time = last_purchase_time.strftime('%Y/%m/%d %H:%M:%S')  # 将时间戳转换为字符串时间
        historical_purchase_times = [last_purchase_time.strftime('%Y/%m/%d %H:%M:%S')]  # 添加历史购买时间列表
    else:
        historical_purchase_times = group['下单时间'].tolist()
        predicted_next_purchase_time = moving_average(historical_purchase_times, window_size=2)
        next_purchase_time = datetime.fromtimestamp(predicted_next_purchase_time).strftime(
            '%Y/%m/%d %H:%M:%S')  # 转换为字符串时间

    # 更新用户-商品预测列表和商品-用户预测列表
    user_product_predictions[username, product_id] = [username, product_id, purchase_count, next_purchase_time,
                                                      [t.strftime('%Y/%m/%d %H:%M:%S') for t in
                                                       pd.to_datetime(historical_purchase_times)]]
    product_user_predictions[product_id, username] = [product_id, username, purchase_count, next_purchase_time,
                                                      [t.strftime('%Y/%m/%d %H:%M:%S') for t in
                                                       pd.to_datetime(historical_purchase_times)]]

    # 更新最终输出列表
    final_output.append(
        [username, product_id, purchase_count, total_purchase_amount, last_purchase_time.strftime('%Y/%m/%d %H:%M:%S'),
         next_purchase_time])

# 计算商品一年内购买频率和预测下一次购买时间
product_purchase_freq = df.groupby('【线上】宝贝ID')['下单时间'].count()
product_avg_purchase_freq = product_purchase_freq.mean()
product_next_purchase_time = df.groupby('【线上】宝贝ID')['下单时间'].max() + pd.DateOffset(
    days=product_avg_purchase_freq)
product_next_purchase_time_str = product_next_purchase_time.dt.strftime('%Y/%m/%d %H:%M:%S')

# 将最终输出列表转换为DataFrame
final_output_df = pd.DataFrame(final_output, columns=['用户名', '商品ID', '购买次数', '总购买金额', '最近购买时间', '预测下一次购买时间'])
# 按购买次数降序排列
final_output_df_sorted = final_output_df.sort_values(by='购买次数', ascending=False)


# 使用Streamlit展示数据
st.title('用户购买的全部商品展示')
# 创建用户选择框
selected_username = st.selectbox('请选择用户ID', final_output_df_sorted['用户名'].unique())
# 根据用户选择展示对应的数据
st.subheader(f'{selected_username}的购买商品：')
selected_user_data = final_output_df_sorted[final_output_df_sorted['用户名'] == selected_username]
st.dataframe(selected_user_data)


# 取购买次数前三的商品
top_3_products = final_output_df_sorted.head(3)


# 展示购买人数最多的前三件商品的商品ID和购买人数
st.subheader('购买人数最多的前三件商品：')
st.write(top_3_products[['商品ID', '购买次数']])




# 设置中文字体为SimHei或者其他支持中文的字体
plt.rcParams['font.family'] = 'SimHei'  # 设置中文字体为SimHei或者其他支持中文的字体
# 绘制直方图
plt.figure(figsize=(8, 6))
plt.hist(final_output_df_sorted['购买次数'], bins=10, edgecolor='black')  # 调整 bins 的数量和边框颜色
plt.xlabel('购买次数', fontsize=12)  # 调整字体大小
plt.ylabel('商品数量', fontsize=12)  # 调整字体大小
plt.title('购买次数分布直方图', fontsize=14)  # 调整标题字体大小
plt.tight_layout()  # 调整布局以确保文字显示完整
st.pyplot(plt)  # 在Streamlit中展示图表



# 对每个用户来说购买次数最多的前三个商品的商品ID和购买次数的展示
st.subheader('每个用户购买次数最多的前三个商品：')
# 对每个用户进行分组并计算购买次数最多的前三个商品
top_3_per_user = final_output_df_sorted.groupby('用户名').apply(lambda x: x.nlargest(3, '购买次数'))
st.write(top_3_per_user[['商品ID', '购买次数']])
