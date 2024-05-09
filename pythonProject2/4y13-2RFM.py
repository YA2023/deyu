import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import timedelta


# 使用Streamlit的数据缓存功能
@st.cache_data
def load_data(filename):
    data = pd.read_excel(filename)
    data['下单时间'] = pd.to_datetime(data['下单时间'])
    return data


# 预测下一次购买时间的函数
def predict_next_purchase(dates):
    if len(dates) < 2:
        return None
    # 对日期进行排序以确保正确顺序
    dates = dates.sort_values()

    # 计算购买间隔（以天为单位）
    intervals = (dates.shift(-1) - dates).dt.days.dropna()

    # 过滤掉小于一天的间隔
    intervals = intervals[intervals > 1]

    if len(intervals) > 0:
        return intervals.mean()
    return None


def main():
    st.title("用户购买行为分析")

    # 加载数据
    df = load_data('./data/保健品部分订单.xlsx')

    # 用户选择和商品ID选择（依赖关系）
    username = st.sidebar.selectbox('选择用户(用户购买行为分析)', df['买家ID(客户昵称)'].unique())
    product_ids_by_user = df[df['买家ID(客户昵称)'] == username]['【线上】宝贝ID'].unique()
    user_product_id = st.sidebar.selectbox('选择商品ID(用户购买行为分析)', product_ids_by_user)

    # 单独的商品ID选择（直方图用）
    all_product_id = st.sidebar.selectbox('选择直方图商品ID(商品分析)', df['【线上】宝贝ID'].unique(), index=0,
                                          key='histogram_product_id')

    # 提取并处理数据
    user_data = df[(df['买家ID(客户昵称)'] == username) & (df['【线上】宝贝ID'] == user_product_id)]
    if not user_data.empty:
        # 去除重复的时间戳
        user_data = user_data.drop_duplicates(subset=['下单时间'])

        purchase_dates = user_data['下单时间'].sort_values()
        last_purchase = purchase_dates.max()
        total_spent = (user_data['单价'] * user_data.get('数量', 1)).sum()  # 假设数量列名为'数量'
        purchase_frequency = len(purchase_dates)  # 更新购买频率计算，考虑了去重

        # 预测下一次购买时间
        next_purchase_pred = predict_next_purchase(purchase_dates)
        if next_purchase_pred is None:
            # 尝试使用其他用户的数据
            other_user_dates = df[(df['【线上】宝贝ID'] == user_product_id) & (df['买家ID(客户昵称)'] != username)][
                '下单时间']
            other_user_dates = other_user_dates.drop_duplicates()  # 同样应用去重
            other_user_dates = other_user_dates.sort_values()
            next_purchase_pred = predict_next_purchase(other_user_dates.sort_values())
            if next_purchase_pred is None:
                next_purchase_str = "无法预测"
            else:
                next_purchase_str = (last_purchase + timedelta(days=next_purchase_pred)).strftime('%Y-%m-%d')
        else:
            next_purchase_str = (last_purchase + timedelta(days=next_purchase_pred)).strftime('%Y-%m-%d')

        # 展示用户购买信息
        st.write(f"用户名: {username}")
        st.write(f"商品ID: {user_product_id}")
        st.write(f"一年内购买频率: {purchase_frequency}")
        st.write(f"一年内总购买金额: {total_spent} 元")
        st.write(f"此商品最近的一次购买时间: {last_purchase.strftime('%Y-%m-%d')}")
        st.write(f"此商品预测下一次的购买时间: {next_purchase_str}")
    else:
        st.write("没有找到对应的用户商品购买记录。")

    # 直方图：给定商品的复购间隔天数分布
    plt.rcParams['font.sans-serif'] = ['SimHei']
    st.title("商品分析")
    intervals = df[df['【线上】宝贝ID'] == all_product_id]
    # 选择与所有产品ID匹配的行
    intervals = intervals.groupby('买家ID(客户昵称)')['下单时间'].apply(
        lambda x: (
            x.sort_values()  # 对订单时间进行排序
            .diff()  # 计算每个订单时间之间的差值
            .dt.days  # 将差值转换为天数
            .dropna()  # 删除由diff()产生的NaN值
            .loc[lambda d: d > 1]  # 过滤掉1天或更短时间间隔的差值
            .mean()  # 计算剩余差值的平均值
        )
    )
    # 按'买家ID(客户昵称)'分组，计算每个买家的平均购买间隔时间
    with st.expander("单个商品复购过的用户的平均复购天数情况"):
        fig, ax = plt.subplots()
        ax.hist(intervals.dropna(), bins=20, color='blue', alpha=0.7)
        ax.set_xlabel('复购间隔天数')
        ax.set_ylabel('用户数量')
        ax.set_xlim(left=0)  # 设置横坐标从0开始
        ax.set_ylim(bottom=0)  # 设置纵坐标从0开始
        st.pyplot(fig)
    
    # 绘制直方图2
    all_intervals = df.groupby(['【线上】宝贝ID', '买家ID(客户昵称)'])['下单时间'].apply(
        lambda x: (x.sort_values().drop_duplicates(keep='first').diff().dt.days.dropna().loc[lambda d: d > 1].mean())
    ).groupby(level=0).mean().dropna()
    #折叠效果
    with st.expander("查看所有商品的平均复购间隔天数分布"):
        st.subheader("所有商品的平均复购间隔天数分布")
        fig, ax = plt.subplots()
        ax.hist(all_intervals, bins=30, color='green', alpha=0.7)
        ax.set_xlabel('复购间隔天数')
        ax.set_ylabel('商品数量')
        ax.set_xlim(left=0.1)  # 设置横坐标从0开始
        ax.set_ylim(bottom=0)  # 设置纵坐标从0开始
        st.pyplot(fig)


if __name__ == "__main__":
    main()

    # @st.cache
    # def load_data(filename):
    #     data = pd.read_excel(filename)
    #     data['下单时间'] = pd.to_datetime(data['下单时间'])
    #     return data


    # # 展示选中用户的所有购买记录
    # if not user_data.empty:
    #     st.subheader(f"{username}的全部购买记录")
    #     st.dataframe(user_data)  # 使用st.dataframe代替st.table，支持内部滚动

    # # 展示选中商品ID的所有被购买记录
    # product_data = df[df['【线上】宝贝ID'] == user_product_id]
    # if not product_data.empty:
    #     st.subheader(f"商品ID {user_product_id} 的全部被购买记录")
    #     st.dataframe(product_data)  # 使用st.dataframe代替st.table，支持内部滚动
