@echo off
REM 接收定时任务传递的参数
set param=%1
REM 调用 Python 程序并传递参数
python D:\pythonProject2\5y11爬虫.py %param%
pause
