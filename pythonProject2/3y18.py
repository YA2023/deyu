import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#普通图标,仅作测试用
# 创建示例数据
data = pd.DataFrame({
    'Category': ['A', 'B', 'C'],
    'Value': [10, 20, 15]
})

# 绘制柱状图
def plot_bar_chart():
    fig, ax = plt.subplots()
    ax.bar(data['Category'], data['Value'])
    ax.set_xlabel('Category')
    ax.set_ylabel('Value')
    ax.set_title('Bar Chart')
    return fig

# 在Streamlit应用中显示柱状图
def main():
    st.title('Bar Chart Example')
    fig = plot_bar_chart()
    st.pyplot(fig)

if __name__ == '__main__':
    main()
# 运行以上代码后，你将在Streamlit应用中看到一个标题为"Bar Chart Example"的页面，并显示了三个柱状图，每个柱状图表示一个类别的值。你可以根据自己的数据和需求进行修改和扩展。
#
# 确保在运行代码之前已经安装了Streamlit和相关的依赖库。你可以使用pip install streamlit pandas matplotlib命令来安装所需的库。运行应用时，使用streamlit run your_script.py命令启动Streamlit服务器，然后在浏览器中访问生成的URL即可查看应用程序。
#
# 注意：在此示例中，使用了Pandas和Matplotlib来处理数据和绘制图表。你可以根据自己的数据和喜好选择适合的数据处理和可视化库。


