#在这里,我要利用RFM特性,进行客户分析
#RFM(Recency Frequency Monetary)
#现需实现 [用户名,购买频率(一年内),购买总金额(一年内),最近一次购买时间,预测的下次购买时间]
#需从表格中提取出   用户名    购买时间     购买金额   商品id
#此版本需要加入 预测的下次购买时间
import pandas as pd
import math
from datetime import datetime, timedelta

import numpy as np
from statsmodels.tsa.arima.model import ARIMA   #也是一种时间预测法,自回归积分移动平均模型
from statsmodels.tsa.holtwinters import ExponentialSmoothing#指数平滑法预测时间
from datetime import datetime, timedelta #移动平均法预测时间(最后用的这个)

import matplotlib.pyplot as plt

#从excle中只提取对应的几列并且重命名-----------------------------------------------------------------------------------------
df = pd.read_excel('./data/保健品部分订单.xlsx')
#首先提取需要的列,注意这里是全部用户的那些后期涉及到处理和计算的列
# 提取并重命名指定列数据   原始列名   改名后的列名
selected_columns = {'买家ID(客户昵称)': '买家ID(客户昵称)','下单时间': '下单时间','买家实付': '买家实付','【线上】宝贝ID': '【线上】宝贝ID'}  # 替换为实际的列名和新列名
df_selected = df[list(selected_columns.keys())].rename(columns=selected_columns)
#保存为列表
data_lists = df_selected.values.tolist()
#看看能遍历不,是不是列表  ,在遍历的时候把交易金额转换成数字型的,要不然后面列表里会出现nan的非数字型数据
for oneperson_data_list in data_lists:
    # print(oneperson_data_list)  #可以遍历,成功洗成列表
    if isinstance(oneperson_data_list[2], float) and math.isnan(oneperson_data_list[2]):
        oneperson_data_list[2] = 0  # 将 "nan" 替换为 0，您可以根据需要修改为其他数字值



#利用用户的历史购买时间预测此用户的下次被购买时间 peoples_buy_times [用户名,预测下次的购买时间]   小例子,改改吧---------------------------------------------------------------------
# 读取Excel文件
df_people = pd.read_excel("./data/保健品部分订单.xlsx")  # 替换为您的Excel文件路径
# 提取用户名和购买时间列
user_column = '买家ID(客户昵称)'  # 替换为用户名所在列的列名
time_column = '下单时间'  # 替换为购买时间所在列的列名
user_purchase_times = {}  # 用于存储每个用户的购买时间列表
# 遍历每一行数据
for index, row in df.iterrows():
    user = row[user_column]
    purchase_time = pd.to_datetime(row[time_column])  # 将购买时间转换为日期时间类型

    # 将购买时间添加到对应用户的时间列表中
    if user in user_purchase_times:
        user_purchase_times[user].append(purchase_time)
    else:
        user_purchase_times[user] = [purchase_time]

user_next_purchase = []  # 存储每个用户的预测下一次购买时间

# 计算每个用户的购买时间平均间隔并预测下一次购买时间
for user, purchase_times in user_purchase_times.items():
    if len(purchase_times) >= 2:
        # 计算购买时间间隔
        time_diffs = pd.Series(purchase_times).diff().dropna()

        # 计算平均间隔
        average_interval = time_diffs.mean()

        # 预测下一次购买时间
        last_purchase_time = purchase_times[-1]
        next_purchase_time = last_purchase_time + average_interval

        # 格式化时间为目标格式
        next_purchase_time = next_purchase_time.strftime("%Y/%m/%d %H:%M:%S")

        # 将用户名和预测下一次购买时间添加到列表     包含多个元组的列表
        user_next_purchase.append((user, next_purchase_time))

# 打印每个用户的预测下一次购买时间
# for user, next_purchase_time in user_next_purchase:
#     print("用户:", user)
#     print("预测下一次购买时间(用户):", next_purchase_time)
#     print()
#利用列表推导式,把包含多个元组的列表转换成列表套列表
peoples_buy_times = [[user, str(next_purchase_time)] for user, next_purchase_time in user_next_purchase]
#这个列表现在是这样的[用户名,预测下次的购买时间]
# for people_buy_time in peoples_buy_times:
#     print(people_buy_time)



#在这里处理商品名,是些id,在这里计算每个id的平均购买时间吧,搁外头求吧,给里面省省复杂度
#利用商品的历史购买时间预测此商品的下次被购买时间------------------------------------------------------------------------------------------------------
goods_buy_times=[]  #[商品id,[历史购买时间列表],预测下次购买时间]
#先根据商品id把此商品的历史购买时间取出来
for oneperson_data_list in data_lists:#[用户名,交易时间,交易金额,商品id]
    goods_id=oneperson_data_list[3] #遍历每一个用户,拿到商品id
    # print("用户订单里的商品id",goods_id)
    for good_buy_time in goods_buy_times:#遍历上面的列表,拿到里面的商品id
        if good_buy_time[0]==goods_id:#如果id一致,就更新列表里的数据
            #先把历史购买时间新增一个
            good_buy_time[1].append(oneperson_data_list[1])#交易时间增加,不太清楚列表里面直接用append是不是能生成一个小列表
            # print("商品编号",goods_id,"的历史购买时间列表:",good_buy_time[1])
            #根据列表里的历史时间预测下一次的时间??每多加一个就预测一次??,算了不管了,代码现在已经是一坨屎了
            #例子   改改
            # 已发生的事件时间列表
            # good_buy_time[1] = ['2024/01/01 00:00:00', '2024/02/01 00:00:00', '2024/03/01 00:00:00', '2024/04/01 00:00:00']
            # 历史事件发生的时间数据

            # 历史事件发生的时间戳列表
            timestamps = good_buy_time[1]
            # 将时间戳字符串转换为 datetime 对象
            timestamps = [datetime.strptime(ts, "%Y/%m/%d %H:%M:%S") for ts in timestamps]
            # 计算历史时间间隔的平均值
            avg_time_delta = sum((timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))),
                                 timedelta()) / (len(timestamps) - 1)
            # 预测下一次事件的时间戳
            next_timestamp = timestamps[-1] + avg_time_delta
            # 将预测的时间戳转换为字符串形式
            predicted_timestamp_str = next_timestamp.strftime("%Y/%m/%d %H:%M:%S")
            good_buy_time[2] = predicted_timestamp_str   # 再把新的预测时间替换进去
            # print("预测的下一次事件时间戳(商品)：",goods_id, predicted_timestamp_str)

            # historical_data = good_buy_time[1]
            # # 将时间数据转换为日期时间类型
            # timestamps = pd.to_datetime(historical_data, format='%Y/%m/%d %H:%M:%S')
            # # 创建带有时间索引的Series对象
            # series = pd.Series(range(len(timestamps)), index=timestamps)
            # # 拟合指数平滑模型
            # model = ExponentialSmoothing(series)
            # model_fit = model.fit()
            # # 预测下一次事件发生的时间
            # prediction = model_fit.predict(start=len(series), end=len(series))
            # if not prediction.empty:
            #     # 将 numpy 数组中的值转换为 Python 的 datetime 对象
            #     prediction_datetime = pd.to_datetime(prediction.iloc[0], unit='D', origin='unix')
            #     # 进行日期格式的转换
            #     formatted_prediction = prediction_datetime.strftime('%Y/%m/%d %H:%M:%S')
            #     good_buy_time[2] = formatted_prediction   # 再把新的预测时间替换进去
            #     print("下一次事件预测时间：", formatted_prediction)
            # else:
            #     print("无法进行预测。请检查模型拟合和预测过程。")


            # 里循环结束,上面是假设这个商品id存在的
    #遍历结束,商品id不存在,就在这里append一个新的
    tmp_liebiao=[]#记得上面那个需要列表套列表的历史购买时间吗,没错就是它的初始化
    tmp_liebiao.append(oneperson_data_list[1])#这次的购买时间
    yuce_xiaci_buy_time=oneperson_data_list[1]#下一次的预测购买时间先初始值为这次的购买时间,因为这件商品在这里是第一次购买嘛
    goods_buy_times.append([goods_id, tmp_liebiao, yuce_xiaci_buy_time])  #[商品id,[历史购买时间列表],预测下次购买时间]
    # print("此商品首次出现",goods_id, tmp_liebiao, yuce_xiaci_buy_time)
#大遍历结束了,每一件商品的下一次购买时间也就出来了
# for good_buy_time in goods_buy_times:# [商品id,[历史购买时间列表],预测下次购买时间]
#     print(good_buy_time)
#-------------------------------------------------------------------------------------------------------------------------
#后续遍历列表的用户名,如果相同,说明是同一人多次购买,重新设一个列表,用来记录[用户名,购买频率也就是一年内的购买次数,一年内的总计购买金额,最近的一次购买时间]
persons_rfm=[]  #列表初始空    [用户名,一年内购买频率,一年内购买金额,最近的一次购买时间,预测下一次的购买时间] 每人共5个数据
for oneperson_data_list in data_lists:#用户的订单信息列表,一次交易的 [用户名,交易时间,交易金额,商品id]
    for person_rfm in persons_rfm:
        # print(person_rfm)
        #如果用户名相同,说明这个人之前购买过,给他的购买频率加1,购买金额累加就行
        if person_rfm[0]==oneperson_data_list[0]:#老用户要判断交易时间是否在一年内,在一年内再进行后续的频率相加和金额相加操作,不在一年内就当他是老用户了
            #更新前的时间存储位置oneperson_data_list[1],更行后的时间存储位置person_rfm[3]
            gengxin_xin = oneperson_data_list[1]  # 时间字符串'2023/12/30 09:37:15' 新时间
            time_format = '%Y/%m/%d %H:%M:%S'  # 时间格式
            gengxin_xin = datetime.strptime(gengxin_xin, time_format)  # 转换为 datetime 新时间
            gengxin_jiu=person_rfm[3]#旧时间
            gengxin_jiu = datetime.strptime(gengxin_jiu, time_format)  # 转换为 datetime 旧时间
            # datetime 类型时间比大小,如果时间新,就更新person_rfm[3]里的时间数据
            #datetime类型时间数据能直接比较,并且是否时间差在一年以内,理论上只有时间差在一年内的时间数据才有必要更新
            if gengxin_xin > gengxin_jiu and abs(gengxin_xin.year - gengxin_jiu.year)<=1:
                #先转换成字符串再更新
                gengxin_xin = gengxin_xin.strftime('%Y/%m/%d %H:%M:%S')
                person_rfm[3]=gengxin_xin #打入时间
                person_rfm[1] = person_rfm[1] + 1  # 购买频率+1
                person_rfm[2] = person_rfm[2] + oneperson_data_list[2]  # 交易额累加
    #用户名,购买频率(初始为1),购买金额,购买时间
    #不需要比较时间就不需要转化,直接插入就可
    time=oneperson_data_list[1]#读取时间
    next_buy=''#预测下次购买时间打入初始化为空字符串
    for goods_buy_time in goods_buy_times:#[商品id,[历史购买时间列表],预测下次购买时间]
        if oneperson_data_list[3]==goods_buy_time[0]:
            next_buy=goods_buy_time[2]#预测下次购买时间打入,这个时间是在前面另外计算的,这里每遍历到一个新用户只需要打入就好了,计算用的该商品的全部历史购买时间预测的
            #现在有两个预测的时间,一个是根据用户预测的下次购买时间,一个是根据商品预测的下次购买时间
            #如果此用户有预测的下次购买时间,则给用户预测的下次购买时间加80%的权重,给商品的那个20%权重
            #预测购买时间重新合成
            #当然如果没有用户有预测的下次购买时间,就直接使用根据商品预测的下次购买时间了,所以这里有一个if判断
            for people_buy_time in peoples_buy_times:#遍历根据用户预测的下次购买时间列表
                if people_buy_time[0]==oneperson_data_list[0]:
                    time_next_buy_people=people_buy_time[1]#这个加80%的权
                    time_next_buy_good=next_buy  #这个加20%的权

                    #小例子,改改"
                    # 将时间字符串转换为datetime对象
                    # gengxin_xin = datetime.strptime(gengxin_xin, time_format)  # 转换为 datetime 新时间
                    dt1 = datetime.strptime(time_next_buy_people, "%Y/%m/%d %H:%M:%S")
                    dt2 = datetime.strptime(time_next_buy_good, "%Y/%m/%d %H:%M:%S")
                    # 计算时间差
                    time_diff = dt2 - dt1
                    # 计算加权平均时间
                    # weighted_time = dt1 + (time_diff * timedelta(days=0.2))
                    weighted_time = dt1 + (time_diff * 0.2)
                    # 将加权平均时间格式化为目标格式
                    next_buy = weighted_time.strftime("%Y/%m/%d %H:%M:%S")
                    # print("加权平均时间:", next_buy)
    persons_rfm.append([oneperson_data_list[0],1,oneperson_data_list[2],time,next_buy])#用户第一次出现,购买频率初始为1

#目前代码未报错,遍历一下最终的persons_rfm列表,看看里面的数据是否是我想要的
for person_rfm in persons_rfm:#OK了
    print(person_rfm)


#下面开始展示数据,写成函数吧
def plot_user_data_histogram(user_data, column_index):
    """
    绘制用户数据直方图

    参数:
    - user_data: 双层列表，外层是用户，内层是每个用户的数据
    - column_index: 要展示的数据列索引

    """

    # 提取指定列的数据
    data = [user[column_index] for user in user_data]

    # 绘制直方图
    plt.hist(data, bins=10, edgecolor='black')

    # 设置标签和标题
    column_labels = ['Username', 'Purchase Frequency', 'Purchase Amount', 'Last Purchase Time', 'Next Purchase Time']
    plt.xlabel(column_labels[column_index])
    plt.ylabel('Count')
    plt.title(column_labels[column_index] + ' Distribution')

    plt.show()

#函数的使用
# 示例数据
user_data = persons_rfm
# 绘制购买金额的直方图
plot_user_data_histogram(user_data, 2)
# 绘制购买频率的直方图
plot_user_data_histogram(user_data, 1)
# plot_user_data_histogram(user_data, 3)
# plot_user_data_histogram(user_data, 4)




