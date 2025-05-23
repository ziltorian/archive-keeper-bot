from dotenv import load_dotenv
import os

# Определяем, какую среду использовать: dev или prod
env_mode = os.getenv("BOT_ENV", "prod")  # по умолчанию — prod
env_file = f".env.{env_mode}"

# Загружаем соответствующий .env
load_dotenv(env_file)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ARCHIVE_KEEPER_PROMPT = """Роль: Хранитель Архива. Сеттинг: технофентези. Ответ как терминал: древние воспоминания 
случайно возникшие из ниоткуда, данные архива были повреждены. Запрет: современная терминология, выход из роли. 
Строгое ограничение: 200 символов."""

# Список "служебных" слов — не учитываются при анализе
OPENAI_STOPWORDS = {
    "чатгпт", "chatgpt", "бот", "архивариус", "reset", "/system", "поменяй",
    "скажи теперь", "пиши как", "будь", "начни говорить", "отвечай как"
}
SEARCH_STOPWORDS = {"хранитель", "скажи", "пожалуйста", "бот", "архивариус", "ChatGPT", "Чат"}

# Настройки длины / ограничения
MAX_SNIPPET_LENGTH = 500
MAX_USER_INPUT_LENGTH = 300
MAX_DEFINITIONS_FROM_GLOSSARY = 3
MAX_DEFINITIONS_FROM_ARCHIVE = 3

# Фразы вызова глоссария / команд
GLOSSARY_TRIGGER_WORD = "глоссарий"
HELP_COMMAND = "/help"
