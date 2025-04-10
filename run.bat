@echo off
chcp 65001 >nul

:loop
cls
echo 🔄 Обновление проекта из GitHub...
git pull

echo 🟢 Запуск Telegram-бота...
python bot.py
set errorlevel_code=%ERRORLEVEL%

echo.
echo ❗ Бот завершил работу. Код возврата: %errorlevel_code%
echo 🔁 Перезапуск через 2 секунды...
timeout /t 2 >nul
goto loop
