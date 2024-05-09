import re
from docx import Document


import jieba
import jieba.posseg as pseg







# 你的文档内容
document = Document("BOT模式介绍.docx")
text = ''
for para in document.paragraphs:
    text += para.text + '\n'



# 使用jieba进行分词和词性标注
words = pseg.cut(text)

# 筛选出人名
person_names1 = [word for word, flag in words if flag == 'nr']

# 输出筛选到的人名
# print("人名:",person_names1)




# 加载自定义的人名词典
jieba.load_userdict("custom_names.txt")
# 使用jieba进行分词和词性标注
words = pseg.cut(text)

# 筛选出人名（排除地名和名词等其他词性）
person_names2 = [word for word, flag in words if flag == 'nr' and len(word) > 1]

# 输出筛选到的人名
# print("人名:",person_names2)
# person_names=[person_name in person_names1 and not in person_names2]
# person_names=person_names1-person_names2
person_names = list(set(person_names1) ^ set(person_names2))
print("人名:",person_names)





# 提取机构名
organizations = re.findall(r'[\u4e00-\u9fa5]+科技有限公司|[\u4e00-\u9fa5]+市教育局', text)
print("机构名:", organizations)

# 提取电话号码
phone_numbers = re.findall(r'\b\d{11}\b|\b0\d{2,3}-\d{7,8}\b', text)
print("电话号码:", phone_numbers)

# 提取地址信息
addresses = re.findall(r'[\u4e00-\u9fa5]+(?:省|自治区|特别行政区|市|自治州|县|区|乡镇|街道)(?:[\u4e00-\u9fa5\d]+号)?', text)
print("地址信息:", addresses)
