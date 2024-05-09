import pandas as pd
import scipy.sparse as sparse
import numpy as np
import random
import implicit
from sklearn.preprocessing import MinMaxScaler
from sklearn import metrics
#推荐系统最重要的是什么:向量,如果把数据做成一个向量至关重要

#下面是对数据的提取清洗整理----------------------------------------------------------------------------------
articles_df = pd.read_csv('./data/shared_articles.csv')
interactions_df = pd.read_csv('./data/users_interactions.csv')
articles_df.drop(['authorUserAgent', 'authorRegion', 'authorCountry'], axis=1, inplace=True)
interactions_df.drop(['userAgent', 'userRegion', 'userCountry'], axis=1, inplace=True)#同上
articles_df = articles_df.drop_duplicates()
interactions_df = interactions_df.drop_duplicates() #同上
print("在shared_articles表的contentId 列中总共有 %d 个唯一值." % articles_df['contentId'].nunique())
print("在users_interactions表的personId 列中总共有 %d 个唯一值." % interactions_df['personId'].nunique())
articles_df.head()
interactions_df.head()#同上

articles_df['eventType'].value_counts()
articles_df = articles_df[articles_df['eventType'] == 'CONTENT SHARED']
articles_df.drop('eventType', axis=1, inplace=True)
articles_df.info()
interactions_df.info()#同上

df = pd.merge(interactions_df[['contentId','personId', 'eventType']], articles_df[['contentId', 'title']], how = 'inner', on = 'contentId')
df.head()
df.info()
df['eventType'].value_counts()

event_type_strength = {
   'VIEW': 1.0,
   'LIKE': 2.0,
   'BOOKMARK': 3.0,
   'FOLLOW': 4.0,
   'COMMENT CREATED': 5.0,
}

df['eventStrength'] = df['eventType'].apply(lambda x: event_type_strength[x])
df.sample(10)

df = df.drop_duplicates()
grouped_df = df.groupby(['personId', 'contentId', 'title']).sum().reset_index()
grouped_df.sample(10)

grouped_df['title'] = grouped_df['title'].astype("category")
grouped_df['personId'] = grouped_df['personId'].astype("category")
grouped_df['contentId'] = grouped_df['contentId'].astype("category")
grouped_df['person_id'] = grouped_df['personId'].cat.codes
grouped_df['content_id'] = grouped_df['contentId'].cat.codes
grouped_df.sample(10)

grouped_df.dtypes
sparse_content_person = sparse.csr_matrix((grouped_df['eventStrength'].astype(float), (grouped_df['content_id'], grouped_df['person_id'])))
sparse_person_content = sparse.csr_matrix((grouped_df['eventStrength'].astype(float), (grouped_df['person_id'], grouped_df['content_id'])))

print(sparse_content_person.shape)
print(sparse_person_content.shape)

#理论知识完毕,现在开始训练模型------------------------------------------------------
#使用交替最小二乘法（ALS）算法来拟合一个隐式反馈推荐模型
alpha = 15
#alpha 是用于调整数据中的权重的超参数。通过乘以 alpha，可以增加数据中的反馈强度
data = (sparse_content_person * alpha).astype('double')

model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=50)

model.fit(data)

#下面开始推荐内容相似的文章-------------------------------------------------------------------------------------
content_id = 235
n_similar = 10

# print(grouped_df.title.loc[grouped_df.content_id == content_id][0])  #直接你会报错的

try:
    print(grouped_df.title.loc[grouped_df.content_id == content_id].iloc[0])
except IndexError:
    print("没有为 content_id 找到标题:", content_id)
    
print(grouped_df.content_id.dtype)  # 检查 content_id 列的数据类型
print(type(content_id))  # 检查变量 content_id 的数据类型



#获取用户矩阵
person_vecs = model.user_factors
#获取内容矩阵
content_vecs = model.item_factors
#计算内容的向量的范数
content_norms = np.sqrt((content_vecs * content_vecs).sum(axis=1))
#计算指定的content_id 与其他所有文章的相似度
scores = content_vecs.dot(content_vecs[content_id]) / content_norms
#获取相似度最大的10篇文章
top_idx = np.argpartition(scores, -n_similar)[-n_similar:]
#组成content_id和title的元组
similar = sorted(zip(top_idx, scores[top_idx] / content_norms[content_id]), key=lambda x: -x[1])
print(person_vecs.shape)
print(content_vecs.shape)
#下面我们展示这10篇最相似的文章title:
for content in similar:
    idx, score = content
    print(grouped_df.title.loc[grouped_df.content_id == idx].iloc[0],"|",score)

#为用户推荐他可能感兴趣的文章---------------------------------------------------------------------------------
def recommend(person_id, sparse_person_content, person_vecs, content_vecs, num_contents=10):
    # 假设需要为 content_vecs 增加列
    if content_vecs.shape[0] < sparse_person_content.shape[1]:
        # 计算缺少的列数
        num_missing_cols = sparse_person_content.shape[1] - content_vecs.shape[0]
        # 创建额外的列（随机或零初始化）
        additional_cols = np.zeros((content_vecs.shape[0], num_missing_cols))
        # 确保 content_vecs 是二维的
        content_vecs = content_vecs[:, np.newaxis] if content_vecs.ndim == 1 else content_vecs
        # 将额外的列添加到原始矩阵
        content_vecs = np.hstack([content_vecs, additional_cols])

    # 验证 person_id 是否超出用户数量的范围
    if person_id >= sparse_person_content.shape[0]:
        raise IndexError("person_id 超出稀疏矩阵行数范围")

    # 获取指定用户的所有互动信息
    person_interactions = sparse_person_content[person_id, :].toarray().flatten()

    from scipy.sparse import vstack, hstack, csr_matrix

    # 假设需要为 person_vecs 增加行
    if person_vecs.shape[0] < sparse_person_content.shape[0]:
        # 计算缺少的行数
        num_missing_rows = sparse_person_content.shape[0] - person_vecs.shape[0]
        # 创建额外的行（随机或零初始化）
        additional_rows = np.zeros((num_missing_rows, person_vecs.shape[1]))
        # 将额外的行添加到原始矩阵
        person_vecs = np.vstack([person_vecs, additional_rows])

    # 假设需要为 content_vecs 增加列
    if content_vecs.shape[0] < sparse_person_content.shape[1]:
        # 计算缺少的列数
        num_missing_cols = sparse_person_content.shape[1] - content_vecs.shape[0]
        # 创建额外的列（随机或零初始化）
        additional_cols = np.zeros((content_vecs.shape[0], num_missing_cols))
        # 将额外的列添加到原始矩阵
        content_vecs = np.hstack([content_vecs, additional_cols])

    # 确认调整后的尺寸
    print(f"调整后的 person_vecs 尺寸: {person_vecs.shape}")
    print(f"调整后的 content_vecs 尺寸: {content_vecs.shape}")

    # 确保用户因子矩阵和内容因子矩阵尺寸匹配
    if person_vecs.shape[0] != sparse_person_content.shape[0] or content_vecs.shape[0] != sparse_person_content.shape[1]:
        raise ValueError("因子矩阵的维度与稀疏矩阵不匹配")

    # 生成用户的推荐评分向量
    rec_vector = person_vecs[person_id, :].dot(content_vecs.T).toarray().flatten()

    # 确保推荐向量与用户互动向量长度一致
    if len(rec_vector) != len(person_interactions):
        raise ValueError(f"尺寸不匹配: rec_vector（长度 {len(rec_vector)}）和 person_interactions（长度 {len(person_interactions)}）必须具有相同的长度")

    # 过滤掉用户已经互动过的内容
    rec_vector[person_interactions > 0] = 0
    min_max = MinMaxScaler()
    rec_vector_scaled = min_max.fit_transform(rec_vector.reshape(-1, 1)).flatten()

    # 获取评分最高的内容的索引
    content_idx = np.argsort(rec_vector_scaled)[-num_contents:]
    titles = [grouped_df.loc[grouped_df['content_id'] == idx, 'title'].iloc[0] for idx in content_idx]
    scores = rec_vector_scaled[content_idx]

    recommendations = pd.DataFrame({'title': titles, 'score': scores}, index=content_idx)
    return recommendations



#下面我们要为特定的用户推荐他们没有看过的，但可能会感兴趣的10篇文章：----------------------------------------------
# 从model中获取经过训练的用户和内容矩阵,并将它们存储为稀疏矩阵
person_vecs = sparse.csr_matrix(model.user_factors)
content_vecs = sparse.csr_matrix(model.item_factors)



# 为指定用户推荐文章。
person_id = 50

recommendations = recommend(person_id, sparse_person_content, person_vecs, content_vecs)
print(recommendations)

grouped_df.loc[grouped_df['person_id'] == 50].sort_values(by=['eventStrength'],
                                                          ascending=False)[['title', 'person_id', 'eventStrength']].head(10)

person_id = 2
recommendations = recommend(person_id, sparse_person_content, person_vecs, content_vecs)
print(recommendations)

grouped_df.loc[grouped_df['person_id'] == 2].sort_values(by=['eventStrength'],
                                                         ascending=False)[['title', 'eventStrength', 'person_id']]

person_id = 1
recommendations = recommend(person_id, sparse_person_content, person_vecs, content_vecs)
print(recommendations)

grouped_df.loc[grouped_df['person_id'] == 1].sort_values(by=['eventStrength'],
                                                         ascending=False)[['title', 'eventStrength', 'person_id']]

import random


def make_train(ratings, pct_test=0.2):
    test_set = ratings.copy()  # 拷贝一份评分数据当作测试集
    test_set[test_set != 0] = 1  # 将有评分数据置为1，我们要模拟成二分类数据集

    training_set = ratings.copy()  # 拷贝一份评分数据当作训练集

    nonzero_inds = training_set.nonzero()  # 找到有过评分(有交互行为，评分数不为0)的数据的索引。
    nonzero_pairs = list(zip(nonzero_inds[0], nonzero_inds[1]))  # 将它们组成元组并存放在list中

    random.seed(0)  # 设置随机数种子

    num_samples = int(np.ceil(pct_test * len(nonzero_pairs)))  # 获取20%的非0评价的数量
    samples = random.sample(nonzero_pairs, num_samples)  # 随机从非零评价的索引对中抽样20%

    content_inds = [index[0] for index in samples]  # 从样本中得到文章列(第一列)索引值

    person_inds = [index[1] for index in samples]  # 从样本中得到文章列(第二列)索引值

    training_set[content_inds, person_inds] = 0  # 在训练集中将这20%的随机样本的评分值置为0
    training_set.eliminate_zeros()  # 在测试集中删除这0元素

    return training_set, test_set, list(set(person_inds))

content_train, content_test, content_persons_altered = make_train(sparse_content_person, pct_test = 0.2)

#计算AUC分数
def auc_score(predictions, actual):
    fpr, tpr, thresholds = metrics.roc_curve(actual, predictions)
    return metrics.auc(fpr, tpr)


# 计算评价AUC分数
def calc_mean_auc(training_set, altered_persons, predictions, test_set):
    store_auc = []  # 用来存储那些在训练集中被删除评分的用户的AUC
    popularity_auc = []  # 用来存储最受欢迎的文章的AUC
    pop_contents = np.array(test_set.sum(axis=1)).reshape(-1)  # 在测试集中按列合计所有评价分数，以便找出最受欢迎的文章。
    content_vecs = predictions[1]
    for person in altered_persons:  # 迭代那些在训练集中被删除评分的那20%的用户
        training_column = training_set[:, person].toarray().reshape(-1)  # 在训练集中找到对应用户的那一列
        zero_inds = np.where(training_column == 0)  # 找出所有没有发生过交互行为的评分的索引,这其中也包括被删除评分的索引

        # 对用户没有交互过的文章预测用户对它们的评分
        person_vec = predictions[0][person, :]
        print(person_vec.shape)#(1, 20) 就是content_vecs
        pred = person_vec.dot(content_vecs).toarray()[0, zero_inds].reshape(-1)
        print(pred.shape)

        # 获取预测的评分，预测评分包含用户交互过的文章的评分(原评分为0)和那20%被强制置为0的实际评分
        actual = test_set[:, person].toarray()[zero_inds, 0].reshape(-1)

        # 从所有文章评价总和中过滤出过滤出那么没有评价过的文章的合计总分(每篇文章各自的合计总分)
        pop = pop_contents[zero_inds]

        store_auc.append(auc_score(pred, actual))  # 计算当前用户的预测和实际评分的AUC

        popularity_auc.append(auc_score(pop, actual))  # 计算合计总分和实际评分的AUC

    return float('%.3f' % np.mean(store_auc)), float('%.3f' % np.mean(popularity_auc))

calc_mean_auc(content_train, content_persons_altered,
              [person_vecs, content_vecs.T], content_test)