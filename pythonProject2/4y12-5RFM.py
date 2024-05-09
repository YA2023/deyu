import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

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


# 预测购买时间函数
def predict_next_purchase(user_df, all_df, product_id):
    if len(user_df) >= 2:
        # 如果用户购买记录足够，则直接预测
        return moving_average(user_df['下单时间'].sort_values().tolist())
    elif len(all_df) >= 2:
        # 否则使用所有用户的购买时间来预测
        return moving_average(all_df['下单时间'].sort_values().tolist())
    else:
        return "无法预测"


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
        predicted_next_purchase = predict_next_purchase(group, df[df['【线上】宝贝ID'] == product_id], product_id)
        if predicted_next_purchase and isinstance(predicted_next_purchase, datetime):
            predicted_next_purchase = predicted_next_purchase.strftime('%Y-%m-%d %H:%M:%S')

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
if intervals is not None and not intervals.empty:
    # fig, ax = plt.subplots()
    # ax.hist(intervals, bins=30, color='blue', edgecolor='black')
    # ax.set_title('复购间隔天数分布')
    # ax.set_xlabel('复购间隔天数')
    # ax.set_ylabel('次数')
    # st.pyplot(fig)
    st.bar_chart(intervals.value_counts())
else:
    st.write('此商品没有足够的复购数据。')

# 直方图2: 所有商品的平均复购间隔天数分布
st.header('所有商品的平均复购间隔天数分布')
avg_intervals = average_repurchase_intervals(df)
if avg_intervals:
    # fig, ax = plt.subplots()
    # ax.hist(avg_intervals, bins=30, color='green', edgecolor='black')
    # ax.set_title('所有商品的平均复购间隔天数分布')
    # ax.set_xlabel('平均复购间隔天数')
    # ax.set_ylabel('商品数量')
    # st.pyplot(fig)
    st.bar_chart(pd.Series(avg_intervals).value_counts())
else:
    st.write('没有足够的数据来展示复购间隔分布。')
