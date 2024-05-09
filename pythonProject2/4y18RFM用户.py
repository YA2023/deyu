import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

@st.cache_data
def load_data(filename):
    """从Excel文件加载数据，并处理时间格式"""
    data = pd.read_excel(filename)
    data['下单时间'] = pd.to_datetime(data['下单时间'])
    return data

def predict_next_purchase(user_dates, all_dates):
    """根据购买日期预测下次购买时间
    如果用户的购买次数少于2次，使用其他用户的购买日期进行预测"""
    user_dates = user_dates.sort_values()
    if len(user_dates) >= 2:
        user_intervals = (user_dates.shift(-1) - user_dates).dt.days.dropna()
        user_intervals = user_intervals[user_intervals > 1]
        if not user_intervals.empty:
            return user_intervals.mean()

    # 当用户数据不足时，使用其他用户的数据进行预测
    all_dates = all_dates.sort_values()
    all_intervals = (all_dates.shift(-1) - all_dates).dt.days.dropna()
    all_intervals = all_intervals[all_intervals > 1]
    return all_intervals.mean() if not all_intervals.empty else None

def display_rfm_analysis(user_data, all_data, entity_id, entity_name, entity_type):
    """展示RFM分析结果，并尝试预测下一次购买时间"""
    st.write(f"**{entity_name}**")
    purchase_frequency = user_data['下单时间'].nunique()
    total_spent = (user_data['单价'] * user_data.get('数量', 1)).sum()
    last_purchase = user_data['下单时间'].max()

    # 根据实体类型（品类或商品ID）获取所有相关购买日期
    if entity_type == "category":
        all_dates = all_data[(all_data['品类'] == entity_id)]['下单时间']
    else:
        all_dates = all_data[(all_data['【线上】宝贝ID'] == entity_id)]['下单时间']

    next_purchase_pred = predict_next_purchase(user_data['下单时间'], all_dates)
    next_purchase_str = "无法预测" if next_purchase_pred is None else (
        last_purchase + timedelta(days=next_purchase_pred)).strftime('%Y-%m-%d')

    st.write(f"购买频率: {purchase_frequency}次")
    st.write(f"总消费金额: {total_spent:.2f}元")
    st.write(f"最近购买时间: {last_purchase.strftime('%Y-%m-%d') if last_purchase else '未记录'}")
    st.write(f"预测下一次的购买时间: {next_purchase_str}")

def main():
    st.title("用户购买行为分析")
    df = load_data('./data/保健品部分订单.xlsx')

    with st.sidebar:
        username = st.selectbox('选择用户', df['买家ID(客户昵称)'].unique())
        selected_category = st.selectbox('选择品类', df[df['买家ID(客户昵称)'] == username]['品类'].unique())
        selected_product_id = st.selectbox('选择商品ID', df[(df['买家ID(客户昵称)'] == username) & (df['品类'] == selected_category)]['【线上】宝贝ID'].unique())

    user_data = df[df['买家ID(客户昵称)'] == username]
    category_data = user_data[user_data['品类'] == selected_category]
    product_data = category_data[category_data['【线上】宝贝ID'] == selected_product_id]

    display_rfm_analysis(category_data, df, selected_category, f"品类: {selected_category}", "category")
    display_rfm_analysis(product_data, df, selected_product_id, f"商品ID: {selected_product_id}", "product")

if __name__ == "__main__":
    main()
