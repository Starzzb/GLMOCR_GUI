@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    uv venv
    uv pip install PyQt5 Pillow PyYAML requests
)
.venv\Scripts\python.exe main.py
pause