import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

@st.cache_data  # 使用 Streamlit 的缓存机制加速数据加载
def load_data(filename):
    """从Excel文件加载数据，并处理时间格式"""
    data = pd.read_excel(filename)
    data['下单时间'] = pd.to_datetime(data['下单时间'])
    return data

def predict_next_purchase(dates):
    """根据购买日期预测下次购买时间"""
    if len(dates) < 2:
        return None
    dates = dates.sort_values()
    intervals = (dates.shift(-1) - dates).dt.days.dropna()
    intervals = intervals[intervals > 1]
    if len(intervals) > 0:
        return intervals.mean()
    return None

def display_rfm_analysis(user_data, all_data, entity_name, entity_id):
    """展示RFM分析结果，并尝试预测下一次购买时间，只考虑最近一年的数据"""
    one_year_ago = datetime.now() - timedelta(days=365)
    user_data = user_data[(user_data['下单时间'] > one_year_ago) & (user_data['下单时间'] <= datetime.now())]
    purchase_dates = user_data['下单时间'].sort_values()
    last_purchase = purchase_dates.max() if not purchase_dates.empty else None
    total_spent = (user_data['单价'] * user_data.get('数量', 1)).sum()
    purchase_frequency = len(purchase_dates)

    next_purchase_pred = predict_next_purchase(purchase_dates)
    if next_purchase_pred is None and not user_data.empty:
        # 尝试使用其他用户的购买数据进行预测
        # other_user_data = all_data[(all_data['【线上】宝贝ID'] == entity_id) &
        #                            (all_data['买家ID(客户昵称)'] != user_data['买家ID(客户昵称)'].iloc[0]) &
        #                            (all_data['下单时间'] > one_year_ago)]
        other_user_data = all_data[(all_data['【线上】宝贝ID'] == entity_id) &
                                   (all_data['买家ID(客户昵称)'].ne(user_data['买家ID(客户昵称)'])) &
                                   (all_data['下单时间'] > one_year_ago)]
        other_purchase_dates = other_user_data['下单时间'].drop_duplicates()
        next_purchase_pred = predict_next_purchase(other_purchase_dates)

    next_purchase_str = "无法预测" if next_purchase_pred is None else (
                last_purchase + timedelta(days=next_purchase_pred)).strftime('%Y-%m-%d') if last_purchase else "无法预测"

    st.write(f"类别: {entity_name}")
    st.write(f"一年内购买频率: {purchase_frequency}")
    st.write(f"一年内总购买金额: {total_spent} 元")
    st.write(f"最近的一次购买时间: {last_purchase.strftime('%Y-%m-%d') if last_purchase else '未记录'}")
    st.write(f"预测下一次的购买时间: {next_purchase_str}")

def main():
    st.title("用户购买行为分析")
    df = load_data('./data/保健品部分订单.xlsx')
    username = st.sidebar.selectbox('选择用户', df['买家ID(客户昵称)'].unique())
    categories_by_user = df[df['买家ID(客户昵称)'] == username]['品类'].unique()
    selected_category = st.sidebar.selectbox('选择品类', categories_by_user)

    category_data = df[(df['买家ID(客户昵称)'] == username) & (df['品类'] == selected_category)]
    display_rfm_analysis(category_data, df, f"品类: {selected_category}", selected_category)

    product_ids_by_user = df[(df['买家ID(客户昵称)'] == username) & (df['品类'] == selected_category)]['【线上】宝贝ID'].unique()
    selected_product_id = st.sidebar.selectbox('选择商品ID', product_ids_by_user)

    product_data = df[(df['买家ID(客户昵称)'] == username) & (df['【线上】宝贝ID'] == selected_product_id)]
    display_rfm_analysis(product_data, df, f"商品ID: {selected_product_id}", selected_product_id)

if __name__ == "__main__":
    main()
