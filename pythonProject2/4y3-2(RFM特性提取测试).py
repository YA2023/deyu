#在这里,我要利用RFM特性,进行客户分析
#RFM(Recency Frequency Monetary)
#最近购买时间   购买频率    购买金额
#需从表格中提取出 用户名     购买时间     购买金额
#现在需要从excel表格里将每个用户的这3个数据读取出来并进行处理
#此版本加了年份限制
import pandas as pd
import math
from datetime import datetime


#从excle中只提取对应的几列并且重命名
df = pd.read_excel('./data/部分测试订单_anonymized.xlsx')
#首先提取需要的列,注意这里是全部用户的那些后期涉及到处理和计算的列
# 提取并重命名指定列数据   原始列名   改名后的列名
selected_columns = {'买家ID(客户昵称)': '买家ID(客户昵称)','下单时间': '下单时间','买家实付': '买家实付'}  # 替换为实际的列名和新列名
df_selected = df[list(selected_columns.keys())].rename(columns=selected_columns)
#selected_columns.keys()：获取selected_columns字典中的所有键（即原列名），返回一个列表。
# df[list(selected_columns.keys())]：使用切片操作，从DataFrame中提取指定的列数据。
# 通过list(selected_columns.keys())将原列名转换为列表，然后使用该列表作为索引，提取对应的列数据。
# 这样，我们只保留了需要的列，并且保持了原来的顺序。
# .rename(columns=selected_columns)：使用rename方法重命名提取的列。
# columns=selected_columns表示将selected_columns字典中的键值对用于重命名列，其中键是原列名，值是新列名。调用rename方法后，将原列名替换为新列名。

# print(df_selected)
#保存为列表
data_lists = df_selected.values.tolist()
#看看能遍历不,是不是列表  ,在遍历的时候把交易金额转换成数字型的,要不然后面列表里会出现nan的非数字型数据
for oneperson_data_list in data_lists:
    # print(oneperson_data_list)  #可以遍历,成功洗成列表
    if isinstance(oneperson_data_list[2], float) and math.isnan(oneperson_data_list[2]):
        oneperson_data_list[2] = 0  # 将 "nan" 替换为 0，您可以根据需要修改为其他数字值
#后续遍历列表的用户名,如果相同,说明是同一人多次购买,重新设一个列表,用来记录[用户名,购买频率也就是一年内的购买次数,一年内的总计购买金额,最近的一次购买时间]
persons_rfm=[]  #列表初始空    [用户名,一年内购买频率,一年内购买金额,最近的一次购买时间] 每人共4个数据 比上个版本多了一列数据最近的一次购买时间
for oneperson_data_list in data_lists:#用户的订单信息列表,一次交易的 [用户名,交易时间,交易金额]
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
                person_rfm[3]=gengxin_xin
                person_rfm[1] = person_rfm[1] + 1  # 购买频率+1
                person_rfm[2] = person_rfm[2] + oneperson_data_list[2]  # 交易额累加

    #for循环结束,persons_rfm遍历了一遍,发现没有相等的,所以是新用户
    #新用户不用判断时间是否在一年内
    #in出问题了 ,二重列表不能用in!!!!!!!!!!!,in只会比较低维第一个数据一次
    #不能用in,只能用!=和==了,!=和==没问题,先遍历外层是处理前的数据,再和里层遍历的后期数据列表一一比较,如果发现相等就怎么这么样
    #用户名,购买频率(初始为1),购买金额,购买时间
    #不需要比较时间就不需要转化,直接插入就可
    time=oneperson_data_list[1]#读取时间
    persons_rfm.append([oneperson_data_list[0],1,oneperson_data_list[2],time])#用户第一次出现,购买频率初始为1

#目前代码未报错,遍历一下最终的persons_rfm列表,看看里面的数据是否是我想要的
for person_rfm in persons_rfm:#OK了
    print(person_rfm)

