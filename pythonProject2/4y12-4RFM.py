import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt

# 读取Excel文件
df = pd.read_excel('./data/保健品部分订单.xlsx')

# 解析日期
df['下单时间'] = pd.to_datetime(df['下单时间'], format='%Y-%m-%d %H:%M:%S')


# 定义移动平均函数
def moving_average(dates, window=2):
    if len(dates) < window:
        return None
    timestamps = [date.timestamp() for date in dates]
    average_timestamp = sum(timestamps[-window:]) / window
    return datetime.fromtimestamp(average_timestamp)


# 计算用户商品统计信息
def user_product_stats(df):
    current_date = pd.Timestamp('now')
    one_year_ago = current_date - pd.DateOffset(years=1)
    filtered_df = df[df['下单时间'] >= one_year_ago]

    result = []
    grouped = filtered_df.groupby(['买家ID(客户昵称)', '【线上】宝贝ID'])
    for (user_id, product_id), group in grouped:
        purchase_frequency = len(group)
        total_amount = group['单价'].sum()
        last_purchase_date = group['下单时间'].max()
        sorted_dates = group['下单时间'].sort_values().tolist()
        predicted_next_purchase = moving_average(sorted_dates)
        if predicted_next_purchase:
            predicted_next_purchase = predicted_next_purchase.strftime('%Y-%m-%d %H:%M:%S')
        else:
            predicted_next_purchase = "无法预测"

        result.append(
            [user_id, product_id, purchase_frequency, total_amount, last_purchase_date, predicted_next_purchase])

    return pd.DataFrame(result, columns=['用户名', '商品ID', '一年内购买频率', '一年内总购买金额', '最近的一次购买时间',
                                         '预测下一次购买时间'])


# 复购间隔天数分布
def repurchase_intervals(df, product_id):
    product_data = df[df['【线上】宝贝ID'] == product_id]
    if len(product_data) < 2:
        return None
    product_data = product_data.sort_values(by='下单时间')
    return product_data['下单时间'].diff().dt.days.dropna()


# 平均复购间隔天数的分布
def average_repurchase_intervals(df):
    grouped = df.groupby('【线上】宝贝ID')
    intervals = []
    for _, group in grouped:
        if len(group) > 1:
            sorted_dates = group.sort_values(by='下单时间')['下单时间']
            intervals.extend(sorted_dates.diff().dt.days.dropna().tolist())
    return intervals


# 使用Streamlit构建界面
st.title('交易数据分析')

# 用户选择
user_df = user_product_stats(df)
selected_user = st.selectbox('请选择用户:', user_df['用户名'].unique())
user_data = user_df[user_df['用户名'] == selected_user]
st.dataframe(user_data)

# 直方图1: 给定商品的复购间隔天数分布
st.header('给定商品的复购间隔天数分布')
selected_product = st.selectbox('请选择商品ID:', df['【线上】宝贝ID'].unique())
intervals = repurchase_intervals(df, selected_product)
if intervals is not None:
    st.bar_chart(intervals.value_counts())
else:
    st.write('此商品没有足够的复购数据。')

# 直方图2: 所有商品的平均复购间隔天数分布
st.header('所有商品的平均复购间隔天数分布')
avg_intervals = average_repurchase_intervals(df)
if avg_intervals:
    st.bar_chart(pd.Series(avg_intervals).value_counts())
else:
    st.write('没有足够的数据来展示复购间隔分布。')
