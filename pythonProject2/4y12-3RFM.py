import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 读取Excel文件
df = pd.read_excel('./data/保健品部分订单.xlsx')

# 将日期转换为datetime类型
df['下单时间'] = pd.to_datetime(df['下单时间'], format='%Y-%m-%d %H:%M:%S')


# 定义移动平均时间预测函数
def moving_average(dates, window_size):
    if len(dates) < window_size:
        return None
    timestamps = [date.timestamp() for date in dates]
    return datetime.fromtimestamp(sum(timestamps[-window_size:]) / window_size)


# 计算每个用户每个商品的购买频率和金额
def calculate_user_product_stats(df):
    one_year_ago = pd.Timestamp.today() - pd.DateOffset(years=1)
    filtered_df = df[df['下单时间'] >= one_year_ago]
    grouped = filtered_df.groupby(['买家ID(客户昵称)', '【线上】宝贝ID'])

    output = []
    for (user_id, product_id), group in grouped:
        purchase_frequency = len(group)
        total_amount = group['单价'].sum()
        last_purchase = group['下单时间'].max()
        historical_times = group['下单时间'].sort_values().tolist()
        next_purchase = moving_average(historical_times, 2)
        if next_purchase:
            next_purchase = next_purchase.strftime('%Y-%m-%d %H:%M:%S')
        else:
            next_purchase = '数据不足，无法预测'

        output.append([user_id, product_id, purchase_frequency, total_amount, last_purchase, next_purchase])

    return pd.DataFrame(output, columns=['用户名', '商品ID', '一年内购买频率', '一年内总购买金额', '最近一次购买时间',
                                         '预测下一次购买时间'])


# 计算商品的平均复购间隔
def calculate_repurchase_intervals(df):
    grouped = df.groupby('【线上】宝贝ID')
    intervals = {}
    for product_id, group in grouped:
        dates = group['下单时间'].sort_values()
        if len(dates) > 1:
            intervals[product_id] = (dates.diff().dt.days.dropna().mean())
    return intervals


final_stats = calculate_user_product_stats(df)
all_intervals = calculate_repurchase_intervals(df)

# 使用Streamlit展示结果
st.title('用户购买数据展示')

# 选择用户名
selected_username = st.selectbox('请选择用户名', final_stats['用户名'].unique())
user_data = final_stats[final_stats['用户名'] == selected_username]
st.dataframe(user_data)

# 绘制给定商品的复购间隔分布
st.title('给定商品的复购间隔天数分布')
selected_product_id = st.selectbox('请选择商品ID', df['【线上】宝贝ID'].unique())
product_data = df[df['【线上】宝贝ID'] == selected_product_id]
if len(product_data) > 1:
    intervals = product_data['下单时间'].sort_values().diff().dt.days.dropna()
    st.bar_chart(intervals)

# 绘制所有商品的平均复购间隔分布
st.title('所有商品的平均复购间隔天数分布')
interval_values = list(all_intervals.values())
if interval_values:
    st.bar_chart(interval_values)
else:
    st.write("没有足够的数据来显示复购间隔分布。")

# 商品总览统计
st.title("商品统计总览")
product_stats = df.groupby('【线上】宝贝ID').agg({
    '下单时间': ['count', lambda x: (x.max() - x.min()).days / max(1, len(x.unique()) - 1)],
    '单价': 'sum'
}).rename(columns={'count': '购买次数', '<lambda_0>': '平均复购间隔（天）', 'sum': '总销售额'})
product_stats.columns = product_stats.columns.droplevel(0)  # Flatten the MultiIndex for easier access in Streamlit

# 显示商品统计总览数据
st.dataframe(product_stats.reset_index())

# 提供给用户查看特定商品的详细信息的选项
st.title("查看特定商品的详细统计")
selected_product_id_for_details = st.selectbox('选择一个商品ID以查看详细统计', df['【线上】宝贝ID'].unique())
detailed_product_data = df[df['【线上】宝贝ID'] == selected_product_id_for_details]

# 显示选定商品的具体交易记录
st.write("选定商品的具体交易记录:")
st.dataframe(detailed_product_data)

# 也可以对选定商品进行进一步的统计分析
st.write("选定商品的统计分析:")
st.write(f"总交易额: {detailed_product_data['单价'].sum()}")
st.write(f"交易次数: {len(detailed_product_data)}")
st.write(f"首次购买日期: {detailed_product_data['下单时间'].min().strftime('%Y-%m-%d')}")
st.write(f"最后购买日期: {detailed_product_data['下单时间'].max().strftime('%Y-%m-%d')}")

# 如果有足够的数据，绘制购买频率的时间序列图
if len(detailed_product_data) > 1:
    st.line_chart(detailed_product_data['下单时间'].value_counts().sort_index())
else:
    st.write("选定商品的交易记录不足，无法生成时间序列图。")

