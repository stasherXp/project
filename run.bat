@echo off
echo Starting application...
if not exist "data" mkdir data
python main.py
pause