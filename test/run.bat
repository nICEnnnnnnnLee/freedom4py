@echo off
if "%1" == "h" goto begin
rem mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit

:begin
rem 设置标题
title=mycmd
rem 将任务写入task.txt
tasklist /v /fo table | findstr /i "mycmd" > task.txt
rem 读取并解析task.txt
set /p task=<task.txt
for /f "tokens=2 delims= " %%a in ("%task%") do (
    echo %%a > task.txt
)
rem python server_local.py