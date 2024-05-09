import pandas as pd
from datetime import datetime
from collections import defaultdict
import streamlit as st
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
final_output_df = pd.DataFrame(final_output, columns=['用户名', '商品ID', '购买次数', '总购买金额', '最近购买时间',
                                                      '预测下一次购买时间'])
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

# 使用Streamlit展示数据
st.title('用户购买的全部商品展示')
# 创建用户选择框
selected_username = st.selectbox('请选择用户ID', final_output_df_sorted['用户名'].unique(), key='user_selection')
# 根据用户选择展示对应的数据
st.subheader(f'{selected_username}的购买商品：')
selected_user_data = final_output_df_sorted[final_output_df_sorted['用户名'] == selected_username]
st.bar_chart(selected_user_data['购买次数'])  # 使用直方图展示购买次数

# 取购买次数前三的商品
top_3_products = final_output_df_sorted.head(3)

# 展示购买人数最多的前三件商品的商品ID和购买人数
st.subheader('购买人数最多的前三件商品：')
st.bar_chart(top_3_products.set_index('商品ID')['购买次数'])  # 使用直方图展示前三件商品的购买次数

# 绘制直方图：给定一件商品所有复购过的用户他们平均复购间隔天数的分布
st.title('给定一件商品所有复购过的用户平均复购间隔天数的分布')
selected_product_id = st.selectbox('请选择商品ID', final_output_df_sorted['商品ID'].unique())
repeat_users = df[df['【线上】宝贝ID'] == selected_product_id]['买家ID(客户昵称)'].value_counts()
repeat_intervals = (df[df['【线上】宝贝ID'] == selected_product_id]
                    .groupby('买家ID(客户昵称)')['下单时间']
                    .apply(lambda x: x.diff().mean().days)
                    .dropna())

# 绘制直方图
st.bar_chart(repeat_intervals)

# 绘制直方图：所有商品的平均复购间隔天数分布
st.title('所有商品的平均复购间隔天数分布')
all_repeat_intervals = (df.groupby('【线上】宝贝ID')
                        .apply(lambda x: x['下单时间'].diff().mean().days)
                        .dropna())

# 绘制直方图
st.bar_chart(all_repeat_intervals)