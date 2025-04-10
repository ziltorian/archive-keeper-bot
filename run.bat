@echo off
:loop
cls
echo Запуск Telegram-бота...
python bot.py

echo.
echo ❗ Бот завершил работу (или произошла ошибка).
echo 🔁 Перезапуск через 2 секунды...
timeout /t 2 >nul
goto loop
