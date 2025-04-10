@echo off
chcp 65001 >nul

:loop
cls
echo 🔄 Обновление проекта из GitHub...

echo 🟢 Запуск Telegram-бота...
set BOT_ENV=dev
python bot.py
set errorlevel_code=%ERRORLEVEL%

echo.
echo ❗ Бот завершил работу. Код возврата: %errorlevel_code%
echo 🔁 Перезапуск через 10 секунды...
timeout /t 10 >nul
goto loop
