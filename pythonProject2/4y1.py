import numpy as np
import scipy.sparse as sparse
from implicit.als import AlternatingLeastSquares
from sklearn.preprocessing import LabelEncoder
#使用python实战开发基于隐式反馈(点击，点赞，浏览，收藏，评论)的协同过滤的推荐系统(implicit库),写一个小例子出来
#有bug,不能运行
# 创建用户-物品矩阵
users = ["User1", "User2", "User3","User4"]
items = ["Item1", "Item2", "Item3", "Item4"]
ratings = [1, 0, 1, 0]  # 隐式反馈，1表示用户有行为，0表示没有行为
print("编码前的users和items",users,items)

# 构建用户-物品矩阵
#直接构建会出错,试试先编码再构建
# data = sparse.csr_matrix((ratings, (users, items)))

# 使用LabelEncoder进行编码
user_encoder = LabelEncoder()
item_encoder = LabelEncoder()
encoded_users = user_encoder.fit_transform(users)
encoded_items = item_encoder.fit_transform(items)
print("编码后的users和items",encoded_users,encoded_items)

# 构建用户-物品矩阵
data = sparse.csr_matrix((ratings, (encoded_users, encoded_items)))

# 输出稀疏矩阵
print(data)

# 初始化模型
model = AlternatingLeastSquares(factors=50, regularization=0.01)
#factors参数：这个参数指定了模型中的潜在因子的数量，也称为隐语义因子。
# 潜在因子可以理解为在用户和物品之间建立联系的特征向量。
# 这个参数控制了模型的复杂度和表示能力。
# 较小的factors值会降低模型的复杂度，但可能会丢失一些重要的特征；较大的factors值会增加模型的复杂度，但可能会导致过拟合。
# 通常，factors的取值一般在10到200之间，具体取值需要根据数据集的大小和特征的复杂性进行调整。

#regularization参数：这个参数控制了模型的正则化程度，用于防止过拟合。
# 正则化是通过在模型训练过程中引入一个惩罚项，使模型的权重不会过大。
# 较小的regularization值会降低正则化的强度，可能会导致过拟合；较大的regularization值会增加正则化的强度，可能会导致欠拟合。
# 通常，regularization的取值一般在0.01到0.1之间，具体取值需要根据数据集的特征和模型的表现进行调整。

# 训练模型
model.fit(data)

# # 为用户1进行推荐
user_id = "User1"
# recommendations = model.recommend(user_id, data, N=3)
#
# # 打印推荐结果
# print("Recommendations for {}: ".format(user_id))
# for item, score in recommendations:
#     print("Item: {}, Score: {}".format(item, score))

# 转换user_id为整数编码
encoded_user_id = user_encoder.transform([user_id])[0]

# 获取推荐结果
recommendations = model.recommend(encoded_user_id, data, N=3)

# 输出推荐结果
for item_id, score in recommendations:
    item = item_encoder.inverse_transform([item_id])[0]
    print(f"Recommended item: {item}, Score: {score}")