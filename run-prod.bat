@echo off
chcp 65001 >nul


:loop
cls
echo 🔄 Обновление проекта из GitHub...
git pull

echo 🟢 Запуск Telegram-бота...
set BOT_ENV=prod
python bot.py
set errorlevel_code=%ERRORLEVEL%

echo.
echo ❗ Бот завершил работу. Код возврата: %errorlevel_code%
echo 🔁 Перезапуск через 10 секунд...
timeout /t 10 >nul
goto loop
