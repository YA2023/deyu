#在这里,我要利用RFM特性,进行客户分析
#RFM(Recency Frequency Monetary)
# 最近购买时间  购买频率   购买金额
#现在需要从excel表格里将每个用户的这3个数据读取出来并展示在前台
#可以跑了,但是没有年份限制,比如规定一年内的数据
import pandas as pd
import math

# 读取Excel表格数据
df = pd.read_excel('./data/部分测试订单_anonymized.xlsx')

# 打印数据
# print(df)
#需要从中筛选出 [ 用户  购买频率   购买金额  ]  这3列数据


#从excle中只提取对应的几列并且重命名
# 读取Excel表格数据
df = pd.read_excel('./data/部分测试订单_anonymized.xlsx')
#由于涉及计算,需要一个一个用户的来
#首先提取需要的列,注意这里是全部用户的那些后期涉及到处理和计算的列
# 提取并重命名指定列数据   原始列名   改名后的列名
selected_columns = {'买家ID(客户昵称)': '买家ID(客户昵称)', '下单时间': '下单时间','买家实付': '买家实付'}  # 替换为实际的列名和新列名
df_selected = df[list(selected_columns.keys())].rename(columns=selected_columns)
#selected_columns.keys()：获取selected_columns字典中的所有键（即原列名），返回一个列表。
# df[list(selected_columns.keys())]：使用切片操作，从DataFrame中提取指定的列数据。
# 通过list(selected_columns.keys())将原列名转换为列表，然后使用该列表作为索引，提取对应的列数据。
# 这样，我们只保留了需要的列，并且保持了原来的顺序。
# .rename(columns=selected_columns)：使用rename方法重命名提取的列。
# columns=selected_columns表示将selected_columns字典中的键值对用于重命名列，其中键是原列名，值是新列名。调用rename方法后，将原列名替换为新列名。

# 打印提取的数据
# print(df_selected)
#保存为列表
data_lists = df_selected.values.tolist()
#看看能遍历不,是不是列表  ,在遍历的时候把交易金额转换成数字型的,要不然要不然后面列表里会出现nan的非数字型数据
for oneperson_data_list in data_lists:
    # print(oneperson_data_list)  #可以遍历,成功洗成列表
    if isinstance(oneperson_data_list[2], float) and math.isnan(oneperson_data_list[2]):
        oneperson_data_list[2] = 0  # 将 "nan" 替换为 0，您可以根据需要修改为其他数字值
#后续遍历列表的用户名,如果相同,说明是同一人多次购买,重新设一个列表,用来记录[用户名,购买频率也就是一年内的购买次数,一年内的总计购买金额]
persons_rfm=[]  #列表初始空    [用户名,一年内购买频率,一年内购买金额,最近的一次购买时间] 每人共4个数据
for oneperson_data_list in data_lists:#用户的订单信息列表,一次交易的 [用户名,交易时间,交易金额]
    #列表oneperson_data_list的第一个元素在列表person_rfm里判断有无,若没有,则将他的信息打入person_rfm里
    # print(oneperson_data_list)
    for person_rfm in persons_rfm:
        # print(person_rfm)
        #如果用户名相同,说明这个人之前购买过,给他的购买频率加1,购买金额累加就行
        if person_rfm[0]==oneperson_data_list[0]:#老用户要判断交易时间是否在一年内,在一年内再进行后续的频率相加和金额相加操作,不在一年内就当他是老用户了
            # time_difference = current_datetime - datetime_obj
            # if time_difference.days <= 365:
            #     print(f"{datetime_str} 与当前日期时间相差在一年内")
            person_rfm[1]=person_rfm[1]+1   #购买频率+1
            person_rfm[2]=person_rfm[2]+oneperson_data_list[2]#交易额累加
            #最近一次购买时间更新,那就说明persons_rfm里需要带购买时间的数据了
    #for循环结束,persons_rfm遍历了一遍,发现没有相等的,所以是新用户
    #新用户不用判断时间是否在一年内,先不考虑
    #没进来,in出问题了
    #不能用in,只能用!=和==了,理论上!=和==没问题,先遍历外层是处理前的数据,再和里层遍历的后期数据列表一一比较,如果发现相等就怎么这么样
    # print(person_rfm[0])
    # print(oneperson_data_list[0])
    persons_rfm.append([oneperson_data_list[0],1,oneperson_data_list[2]])#用户第一次出现,购买频率初始为1

#目前代码未报错,遍历一下最终的persons_rfm列表,看看里面的数据是否是我想要的
for person_rfm in persons_rfm:#有值了,频率的年份限制之后再看,先让它们全部相加能跑起来
    print(person_rfm)

