import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 按要求左边是id选择,右边根据选择的不同id显示对应的数据
# 示例数据
data = {
    'ID': ['A', 'B', 'C'],
    'Value1': [10, 20, 15],
    'Value2': [5, 8, 12],
    'Value3': [7, 10, 9]
}

df = pd.DataFrame(data)


# 绘制柱状图
def plot_bar_chart(selected_id):
    selected_data = df[df['ID'] == selected_id]
    values = selected_data.iloc[:, 1:].values.flatten()
    labels = selected_data.columns[1:]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel('Category')
    ax.set_ylabel('Value')
    ax.set_title('Bar Chart for ID: ' + selected_id)
    return fig


# 在Streamlit应用中显示柱状图
def main():
    st.title('Bar Chart Example')

    # 左侧选择ID
    selected_id = st.sidebar.selectbox('Select ID', df['ID'])

    # 右侧显示柱状图
    fig = plot_bar_chart(selected_id)
    st.pyplot(fig)


if __name__ == '__main__':
    main()