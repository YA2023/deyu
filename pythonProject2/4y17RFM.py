import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def load_data(filepath):
    """从Excel文件加载数据"""
    return pd.read_excel(filepath)

def filter_dates(df):
    """仅当同一用户在相同日期购买相同商品时，去除重复的日期记录"""
    df['下单时间'] = pd.to_datetime(df['下单时间'])
    return df.drop_duplicates(subset=['买家ID(客户昵称)', '【线上】宝贝ID', '下单时间'])

def main():
    st.title("商品购买分析")

    # 加载数据
    df = load_data('./data/保健品部分订单.xlsx')

    # 首先选择品类
    category = st.sidebar.selectbox('选择品类:', df['品类'].unique())

    # 根据所选品类过滤可用的商品ID
    filtered_df = df[df['品类'] == category]
    selected_product_id = st.sidebar.selectbox('选择商品ID:', filtered_df['【线上】宝贝ID'].unique())

    # 根据选中的商品ID过滤数据
    product_data = filtered_df[filtered_df['【线上】宝贝ID'] == selected_product_id]

    # 显示历史总购买者人数和总消费金额（在日期过滤前计算）
    unique_buyers = product_data['买家ID(客户昵称)'].nunique()
    total_spent = (product_data['单价'] * product_data.get('数量', 1)).sum()
    st.write(f"历史总购买人数: {unique_buyers}")
    st.write(f"历史总消费金额: {total_spent:.2f}")

    # 应用日期过滤并设置时间索引
    product_data_filtered = filter_dates(product_data)
    one_year_ago = datetime.now() - timedelta(days=365)
    product_data_filtered = product_data_filtered[product_data_filtered['下单时间'] > one_year_ago]
    product_data_filtered.set_index('下单时间', inplace=True)

    # 计算每周的购买者人数并重命名列
    weekly_buyers = product_data_filtered['买家ID(客户昵称)'].resample('W').nunique().rename('人数')

    # 计算每周的消费金额
    weekly_spent = (product_data_filtered['单价'] * product_data_filtered.get('数量', 1)).resample('W').sum().rename('金额')

    # 绘制图表，显示每周数据
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体，以便显示中文标签
    if not weekly_buyers.empty and not weekly_spent.empty:
        st.write("每周购买人数:")
        st.write(weekly_buyers)
        st.write("每周消费金额:")
        st.write(weekly_spent)

        # 绘制数据图表，中间隔一段距离
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))
        fig.subplots_adjust(hspace=0.5)  # 设置子图之间的垂直间距为0.5
        weekly_buyers.plot(kind='bar', ax=ax[0], title="每周购买人数")
        ax[0].set_xticklabels(weekly_buyers.index.strftime('%Y-%m-%d'), rotation=0, ha='right')  # 设置横轴标签旋转角度为0度，并向右对齐
        weekly_spent.plot(kind='bar', ax=ax[1], title="每周消费金额", color='orange')
        ax[1].set_xticklabels(weekly_spent.index.strftime('%Y-%m-%d'), rotation=0, ha='right')  # 设置横轴标签旋转角度为0度，并向右对齐
        st.pyplot(fig)
    else:
        st.error("没有足够的数据来绘图。")

if __name__ == "__main__":
    main()
