@echo off
chcp 65001 >nul
title GLM-OCR GUI

echo 启动 GLM-OCR GUI...
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [!] 虚拟环境不存在，正在创建...
    call uv venv
    echo [*] 安装依赖中...
    call uv pip install PyQt5 Pillow PyYAML requests
)

echo [*] 启动 GUI...
.venv\Scripts\python.exe main.py

pause