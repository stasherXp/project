@echo off
chcp 65001 > nul
echo Проверка и установка зависимостей...
py -m pip install -r requirements.txt

echo Создание папки для базы данных (если её нет)...
if not exist "data" mkdir data

echo Запуск приложения...
python main.py

pause