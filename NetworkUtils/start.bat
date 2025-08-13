@echo off
chcp 65001 >nul
echo ==================================================
echo HISAuto_web - 住院部HIS Agent应用
echo ==================================================
echo.

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境不存在，请先创建虚拟环境
    echo 运行命令: python -m venv .venv
    pause
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 启动应用
python start.py

pause 