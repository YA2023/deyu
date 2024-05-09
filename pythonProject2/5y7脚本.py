import subprocess

# 定义要运行的 Python 文件路径
file1_path = "4y19商品分类.py"
file2_path = "5y6全部数据存储es.py"

# 执行第一个 Python 文件
process1 = subprocess.Popen(["python", file1_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output1, error1 = process1.communicate()

# 打印第一个文件的输出结果和错误信息
print("Output of 4y19商品分类.py:", output1.decode("utf-8"))
print("Error from 4y19商品分类.py:", error1.decode("utf-8"))

# 执行第二个 Python 文件
process2 = subprocess.Popen(["python", file2_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output2, error2 = process2.communicate()

# 打印第二个文件的输出结果和错误信息
print("Output of 5y6全部数据存储es.py:", output2.decode("utf-8"))
print("Error from 5y6全部数据存储es.py:", error2.decode("utf-8"))
