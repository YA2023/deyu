import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def load_and_filter_data(filepath):
    """从Excel文件加载数据，并立即过滤重复日期记录"""
    data = pd.read_excel(filepath)
    data['下单时间'] = pd.to_datetime(data['下单时间'])
    return data.drop_duplicates(subset=['买家ID(客户昵称)', '【线上】宝贝ID', '下单时间'])

def main():
    st.title("商品购买分析")

    # 使用侧边栏和布局优化
    with st.sidebar:
        df = load_and_filter_data('./data/保健品部分订单.xlsx')
        category = st.selectbox('选择品类:', df['品类'].unique())
        filtered_df = df[df['品类'] == category]
        selected_product_id = st.selectbox('选择商品ID:', filtered_df['【线上】宝贝ID'].unique())

    product_data = filtered_df[filtered_df['【线上】宝贝ID'] == selected_product_id]
    unique_buyers = product_data['买家ID(客户昵称)'].nunique()
    total_spent = (product_data['单价'] * product_data.get('数量', 1)).sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="历史总购买人数", value=unique_buyers)
    with col2:
        st.metric(label="历史总消费金额", value=f"{total_spent:.2f} 元")

    one_year_ago = datetime.now() - timedelta(days=365)
    product_data_filtered = product_data[product_data['下单时间'] > one_year_ago]
    product_data_filtered.set_index('下单时间', inplace=True)

    weekly_buyers = product_data_filtered['买家ID(客户昵称)'].resample('W').nunique().rename('人数')
    weekly_spent = (product_data_filtered['单价'] * product_data_filtered.get('数量', 1)).resample('W').sum().rename('金额')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体，以便显示中文标签
    # 优化图表显示
    if not weekly_buyers.empty and not weekly_spent.empty:
        st.write("每周购买人数:")
        st.write(weekly_buyers)
        st.write("每周消费金额:")
        st.write(weekly_spent)

        fig, ax = plt.subplots(2, 1, figsize=(10, 8), tight_layout=True)
        weekly_buyers.plot(kind='bar', ax=ax[0], title="每周购买人数", color='skyblue')
        ax[0].set_xticklabels(weekly_buyers.index.strftime('%Y-%m-%d'), rotation=0, ha='right')
        weekly_spent.plot(kind='bar', ax=ax[1], title="每周消费金额", color='orange')
        ax[1].set_xticklabels(weekly_spent.index.strftime('%Y-%m-%d'), rotation=0, ha='right')
        st.pyplot(fig)
    else:
        st.error("没有足够的数据来绘图。")

if __name__ == "__main__":
    main()
