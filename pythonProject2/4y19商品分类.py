import pandas as pd
#万里牛数据集
#注意文件路劲,按需求修改
#输入路劲:  file_path
#输出路劲:  output_path

# 加载Excel文件
file_path = './data/万里牛测试数据.xlsx'
df = pd.read_excel(file_path)

# 检查“商品概况”列并根据条件添加“品类”列       按需添加
def categorize(description):
    if '胶囊' in description:
        return '保健品'
    elif any(item in description for item in ['鞋', '帽', '裤','衣','外套','短袖','T恤']):
        return '服装'
    elif any(item in description for item in ['肉肠', '玉米', '酒']):
        return '食品'
    else:
        return '其他'

# 应用函数并创建新列
df['【线上】商品标题'] = df['【线上】商品标题'].astype(str)
df['品类'] = df['【线上】商品标题'].apply(categorize)


# 定义输出文件路径
output_path = './data/万里牛测试数据分类后.xlsx'

# 尝试读取已存在的Excel文件，如果不存在则创建一个新的DataFrame
try:
    old_df = pd.read_excel(output_path)
except FileNotFoundError:
    old_df = pd.DataFrame()

# 将新数据追加到旧数据中
combined_df = pd.concat([old_df, df], ignore_index=True)

# 去重，根据需要可以指定subset参数来定义哪些列用来判定重复
combined_df = combined_df.drop_duplicates()

# 以追加模式写入Excel文件
with pd.ExcelWriter(output_path, mode='w', engine='openpyxl') as writer:
    combined_df.to_excel(writer, index=False)

print("修改完成，文件已追加并保存。")
