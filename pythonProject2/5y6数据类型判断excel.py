import pandas as pd

# 读取 Excel 文件
excel_file = './data/万里牛测试数据分类后.xlsx'
df = pd.read_excel(excel_file)

# 获取第一行数据
row_data = df.iloc[0]

# 遍历每个单元格并输出数据类型
for column, value in row_data.items():
    data_type = type(value).__name__
    print(f'{column}: {value} - {data_type}')
