# logger_setup.py

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta

# Создаём директорию logs/ если не существует
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Название файла по дате
log_filename = os.path.join(log_dir, f"bot-{datetime.now().strftime('%Y-%m-%d')}.log")

# Настройка логгера
logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

# Хендлер для записи в файл с ротацией
file_handler = TimedRotatingFileHandler(
    filename=log_filename,
    when='midnight',            # новая дата — новый файл
    backupCount=10,             # максимум 10 логов
    encoding='utf-8',
    delay=False,
    utc=False
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Хендлер для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Очистка логов старше 10 дней (дополнительно к backupCount)
def clean_old_logs(days=10):
    now = datetime.now()
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            created = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - created).days > days:
                os.remove(filepath)
                logger.info(f"🗑 Удалён старый лог: {filename}")

clean_old_logs()
