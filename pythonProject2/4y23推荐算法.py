import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import implicit
from sklearn.metrics import roc_auc_score

def loadData():
    return {
        'A': {'Alice': 5.0, 'user1': 3.0, 'user2': 4.0, 'user3': 3.0, 'user4': 1.0},
        'B': {'Alice': 3.0, 'user1': 1.0, 'user2': 3.0, 'user3': 3.0, 'user4': 5.0},
        'C': {'Alice': 4.0, 'user1': 2.0, 'user2': 4.0, 'user3': 1.0, 'user4': 5.0},
        'D': {'Alice': 4.0, 'user1': 3.0, 'user2': 3.0, 'user3': 5.0, 'user4': 2.0},
        'E': {'user1': 3.0, 'user2': 5.0, 'user3': 4.0, 'user4': 1.0}
    }

def build_user_item_matrix(item_data):
    users = set()
    for item, ratings in item_data.items():
        users.update(ratings.keys())
    users = list(users)
    items = list(item_data.keys())

    user_map = {user: idx for idx, user in enumerate(users)}
    item_map = {item: idx for idx, item in enumerate(items)}

    data = []
    row_indices = []
    col_indices = []

    for user in users:
        for item in items:
            user_idx = user_map[user]
            item_idx = item_map[item]
            rating = item_data.get(item, {}).get(user, 0)
            data.append(rating)
            row_indices.append(user_idx)
            col_indices.append(item_idx)

    # 构建完整的用户-物品评分矩阵
    full_user_item_matrix = csr_matrix((data, (row_indices, col_indices)), shape=(len(users), len(items)))
    return full_user_item_matrix, user_map, item_map

item_data = loadData()
full_user_item_matrix, user_map, item_map = build_user_item_matrix(item_data)

model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=50)
model.fit(full_user_item_matrix)


def recommend_items(model, user_id, user_map, item_map, num_items=5):
    user_idx = user_map.get(user_id)
    if user_idx is None:
        return []
    # 使用完整的用户-物品评分矩阵
    user_items = full_user_item_matrix[user_idx]
    if user_items.nnz == 0:
        return []  # 用户没有评分记录，无法推荐
    recommended = model.recommend(user_idx, user_items, N=num_items)

    print("Recommended:", recommended)  # 打印推荐结果，查看索引类型

    # 将索引数组转换为普通的 Python 列表
    recommended_indices = recommended[0].tolist()
    recommended_scores = recommended[1].tolist()

    # 确保推荐结果的索引类型是整数
    recommended_items = [(list(item_map.keys())[int(item)], score) for item, score in
                         zip(recommended_indices, recommended_scores)]

    return recommended_items


recommended_items = recommend_items(model, 'Alice', user_map, item_map, num_items=2)
print("推荐给Alice的物品:", recommended_items)

# AUC计算示例
def calculate_auc(y_true, y_scores):
    return roc_auc_score(y_true, y_scores)

y_true = [0, 1, 1, 0, 1]
y_scores = [0.1, 0.4, 0.35, 0.03, 0.9]
auc_score = calculate_auc(y_true, y_scores)
print("AUC Score:", auc_score)
