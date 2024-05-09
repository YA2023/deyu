import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# 使用新的缓存装饰器
@st.cache_data
def load_data(filename):
    return pd.read_excel(filename)


# 预测下一次购买时间的函数，确保返回非None值时再进行计算
def predict_next_purchase(dates):
    if len(dates) < 2:
        return None
    intervals = (dates.shift(-1) - dates).dt.days.dropna()
    if len(intervals) == 0:
        return None
    return intervals.mean()


def main():
    st.title("用户购买行为分析")

    # 加载数据
    df = load_data('./data/保健品部分订单.xlsx')
    df['下单时间'] = pd.to_datetime(df['下单时间'])

    # 选择用户和商品
    username = st.sidebar.selectbox('选择用户', df['买家ID(客户昵称)'].unique())
    product_id = st.sidebar.selectbox('选择商品ID', df[df['买家ID(客户昵称)'] == username]['【线上】宝贝ID'].unique())

    # 提取用户数据
    user_data = df[(df['买家ID(客户昵称)'] == username) & (df['【线上】宝贝ID'] == product_id)]
    last_purchase = user_data['下单时间'].max()
    total_spent = (user_data['单价'] * user_data['数量']).sum()
    purchase_frequency = user_data.shape[0]
    dates = user_data['下单时间'].sort_values()
    predicted_days = predict_next_purchase(dates)
    if predicted_days is not None:
        next_purchase_date = dates.max() + timedelta(days=predicted_days)
        next_purchase_str = next_purchase_date.strftime('%Y-%m-%d')
    else:
        next_purchase_str = '无足够数据预测'

    # 显示用户购买信息
    st.write(f"用户名: {username}")
    st.write(f"商品ID: {product_id}")
    st.write(f"一年内购买频率: {purchase_frequency}")
    st.write(f"一年内总购买金额: {total_spent} 元")
    st.write(f"此商品最近的一次购买时间: {last_purchase}")
    st.write(f"此商品预测下一次的购买时间: {next_purchase_str}")

    # 绘制直方图1
    product_data = df[df['【线上】宝贝ID'] == product_id]
    intervals = product_data.groupby('买家ID(客户昵称)')['下单时间'].apply(
        lambda x: (x.sort_values().diff().dt.days).mean()).dropna()
    st.subheader("复购间隔天数分布")
    fig, ax = plt.subplots()
    ax.hist(intervals, bins=20, color='blue', alpha=0.7)
    ax.set_xlabel('复购间隔天数')
    ax.set_ylabel('用户数量')
    st.pyplot(fig)

    # 绘制直方图2
    all_intervals = df.groupby('【线上】宝贝ID')['下单时间'].apply(
        lambda x: (x.sort_values().diff().dt.days).mean()).dropna()
    st.subheader("所有商品的平均复购间隔天数分布")
    fig, ax = plt.subplots()
    ax.hist(all_intervals, bins=30, color='green', alpha=0.7)
    ax.set_xlabel('复购间隔天数')
    ax.set_ylabel('商品数量')
    st.pyplot(fig)


if __name__ == "__main__":
    main()
