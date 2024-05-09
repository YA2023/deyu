from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql.functions import col, when

# 初始化Spark
spark = SparkSession.builder.appName("ALSExample").getOrCreate()

# 创建一些模拟数据
data = {
    "user": [0, 0, 1, 1, 2, 2, 3, 3],
    "item": [0, 1, 0, 1, 0, 1, 0, 1],
    "rating": [1, 2, 2, 3, 3, 4, 4, 5]
}
df = spark.createDataFrame(data)

# 将评分转化为二分类指标
df = df.withColumn("label", when(col("rating") >= 3, 1).otherwise(0))

# 划分训练集和测试集
(train, test) = df.randomSplit([0.8, 0.2])

# 设置ALS模型
als = ALS(maxIter=5, regParam=0.01, userCol="user", itemCol="item", ratingCol="rating", coldStartStrategy="drop")
model = als.fit(train)

# 进行预测
predictions = model.transform(test)

# 评估模型
evaluator = BinaryClassificationEvaluator()
auc = evaluator.evaluate(predictions)

print("AUC:", auc)

# 为用户推荐Top 3 items
userRecs = model.recommendForAllUsers(3)
userRecs.show()

# 关闭Spark会话
spark.stop()
