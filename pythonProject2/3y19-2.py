#include <stdio.h>
#include <stdlib.h>




import ctypes

# 加载共享库
lib = ctypes.CDLL('libmemory.so')

# 调用 malloc 函数分配内存
size = 10
ptr = lib.allocate_memory(size)

# 使用 initialize_memory 函数初始化内存
lib.initialize_memory(ptr, size)

# 打印初始化后的内存内容
print("Memory after initialization:", ctypes.string_at(ptr, size))

# 调用 free_memory 函数释放内存
lib.free_memory(ptr)