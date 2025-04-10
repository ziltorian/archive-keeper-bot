import os
import glob
import re
import asyncio
from difflib import SequenceMatcher
import json
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from openai import OpenAI
from dotenv import load_dotenv
from logger_setup import logger as log

# импортируем переменные
from config import (
    ARCHIVE_KEEPER_PROMPT,
    OPENAI_STOPWORDS,
    SEARCH_STOPWORDS,
    MAX_USER_INPUT_LENGTH,
    MAX_SNIPPET_LENGTH,
    MAX_DEFINITIONS_FROM_GLOSSARY,
    MAX_DEFINITIONS_FROM_ARCHIVE,
    HELP_COMMAND,
    GLOSSARY_TRIGGER_WORD
)

# Загружаем токены из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка, что переменные окружения загружены
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Отсутствуют TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в .env файле.")

# Инициализируем бота
bot = Bot(token=TELEGRAM_TOKEN)
log.info("Инициализация бота")
storage = MemoryStorage()  # Для хранения состояния, если понадобится
log.info("Что-то там хранилище")
dp = Dispatcher(storage=storage)
log.info("Диспатчер...")
router = Router()
dp.include_router(router)

try:
    client = OpenAI()
    client.models.list()  # попытка запросить список моделей = проверка API
    log.info("✅ OpenAI API успешно инициализирован.")
except Exception as e:
    log.error(f"❌ Ошибка подключения к OpenAI: {e}")
    client = None  # отключаем OpenAI, чтобы не использовать дальше


# Загрузка глоссария
with open("archive/Глоссарий_Хранителя_Архива.json", "r", encoding="utf-8") as f:
    log.info("Загрузка файла: Глоссарий_Хранителя_Архива.json")
    glossary = json.load(f)

# Загрузка всех текстовых файлов архива {имя файла: содержимое}
archive_data = {}
for filepath in glob.glob("archive/*.txt"):
    filename = os.path.basename(filepath)
    log.info(f"Загрузка файла: {filename}")
    with open(filepath, "r", encoding="utf-8") as f:
        archive_data[filename] = f.read()


# Список "служебных" слов — не учитываются при анализе


def search_archive(question, only_glossary=False):
    log.info(f"🔍 Поиск начат. вопрос: {question}")
    """
    Ищет ответ в глоссарии (по смыслу) или в архивных .txt-файлах.
    Сначала отбираются потенциальные совпадения по корню слова,
    затем — проверяется схожесть с ключами глоссария.
    """

    # Извлекаем слова из запроса, исключаем стоп-слова и короткие
    raw_words = re.findall(r'\b\w+\b', question.lower())
    raw_words = [w for w in raw_words if w not in SEARCH_STOPWORDS and len(w) >= 4]

    # Генерация двухсловных фраз (n-грамм)
    two_word_phrases = [
        f"{raw_words[i]} {raw_words[i + 1]}" for i in range(len(raw_words) - 1)
    ]

    # Берем первые 4 символа каждого слова (упрощённый корень)
    search_roots = [word[:4] for word in raw_words]
    log.info(f"🔤 Слова после фильтрации: {raw_words}")
    log.info(f"🪵 Корни для поиска: {search_roots}")
    log.info(f"🔤 Двухсловные фразы: {two_word_phrases}")

    candidate_matches = []

    # Поиск точных совпадений по фразам
    for phrase in two_word_phrases:
        for key in glossary.keys():
            similarity = SequenceMatcher(None, phrase.lower(), key.lower()).ratio()
            if similarity >= 0.85:
                log.info(f"🤝 Похожая фраза: '{phrase}' ≈ '{key}' → {similarity:.2f}")
                candidate_matches.append((similarity, f"{key}: {glossary[key]}"))
                log.info(f"Добавляем фразу: {key}: {glossary[key]}")
                break

    # Ищем потенциальные совпадения в глоссарии
    for word, root in zip(raw_words, search_roots):
        for key in glossary.keys():
            key_lower = key.lower()
            if key_lower.startswith(root) or root.startswith(key_lower[:4]):

                # Повторное сравнение: оценка похожести полного слова и ключа
                similarity = SequenceMatcher(None, word, key_lower).ratio()
                if similarity >= 0.8:
                    log.info(f"🔍 Сравнение: '{word}' ↔ '{key}' → {similarity:.2f}")
                    candidate_matches.append((similarity, f"{key}: {glossary[key]}"))
                    log.info(f"Добавляем определение: {key}: {glossary[key]}")
                    # break  # только первое совпадение на слово

    # Если найдено хотя бы одно определение — возвращаем лучшие
    if candidate_matches:
        log.info("✅ Найдено в глоссарии.")
        candidate_matches.sort(reverse=True)  # сортировка по убыванию совпадения
        seen = set()  # Будет хранить уже добавленные определения, чтобы не было повторов
        definitions = []  # Финальный список, который мы соберём
        for _, definition in candidate_matches:
            if definition not in seen:
                definitions.append(definition)
                seen.add(definition)
        definitions = definitions[:MAX_DEFINITIONS_FROM_GLOSSARY]  # или 5
        log.info(f"✅ Итог: добавлено {len(definitions)} определение(й) из глоссария.")
        return "\n".join(definitions)

    if only_glossary:
        return ""  # ничего не найдено в глоссарии, не ищем в архиве

    # Переход к .txt-файлам архива, если в глоссарии ничего не нашли
    log.warning("⚠️ Ничего не найдено в глоссарии. Переход к архиву...")
    context_snippets = []
    for _, text in archive_data.items():
        if len(context_snippets) >= MAX_DEFINITIONS_FROM_ARCHIVE:
            break  # не добавляем больше 3-х совпадений

        # Делим текст на предложения (учитываем пунктуацию и заглавные буквы)
        sentences = re.split(r'\n{2,}|\r\n{2,}|(?<=[.!?])\s+(?=[А-ЯA-Z])', text)

        for idx, sentence in enumerate(sentences):
            if any(root in sentence.lower() for root in search_roots):
                # Берём это и следующее предложение
                snippet_group = sentences[idx:idx + 2]
                # Объединяем и ограничиваем длину
                snippet = " ".join(s.strip() for s in snippet_group)
                snippet = snippet[:MAX_SNIPPET_LENGTH]  # ⬅️ вот ограничение длины
                context_snippets.append(snippet)
                log.info(f"📂 Архивные файлы, найдено: {snippet}.")
                break  # по одному фрагменту на файл
    log.info(f"📂 Архивные файлы: найдено {len(context_snippets)} совпадений.")
    return "\n".join(context_snippets)


def extract_question_part(text, max_len=300):
    """
    Извлекает первое предложение с вопросом. Если его нет — берёт первые max_len символов.
    """
    # Делим на предложения
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        if "?" in sentence:
            return sentence.strip()[:max_len]
    return text[:max_len]  # fallback: первые 300 символов


def clean_for_openai(text):
    """
    Удаляет из текста команды и слова, которые могут сбить OpenAI с образа.
    """
    lowered = text.lower()
    for stop in OPENAI_STOPWORDS:
        if stop in lowered:
            log.warning(f"⚠️ Удалено потенциально опасное слово: {stop}")
            lowered = lowered.replace(stop, "")
    return lowered.strip()


#
# # Функция поиска по словам
# def search_archive(question):
#     print("Поисковая функция запущена.")
#     question_lower = question.lower()
#     context_snippets = []
#
#     for _, text in archive_data.items():
#         # Разбиваем текст на предложения с помощью регулярного выражения
#         # Учитываем точку, вопрос, восклицание, затем пробел и заглавную букву или конец строки
#         # Улучшенная регулярка: разделение по [.?!], но избегаем аббревиатур и кавычек
#         sentences = re.split(r'(?<=[.!?])(?<!\b[А-ЯA-Z]\.)(?<!\.\")\s+(?=[А-ЯA-Z])', text)
#
#         for idx, sentence in enumerate(sentences):
#             if question_lower in sentence.lower():
#                 # Берём текущее и 2 следующих предложения (если они есть)
#                 snippet_group = sentences[idx:idx + 3]
#                 snippet = " ".join(s.strip() for s in snippet_group)
#                 context_snippets.append(snippet)
#                 break  # только первое совпадение на файл
#     print(context_snippets)
#     # Объединяем найденные предложения в единый текст
#     return "\n".join(context_snippets)


@router.message()
async def handle_message(message: types.Message):
    text = message.text
    # Игнорируем служебные сообщения и отсутствие текста
    if not text:
        return

    if text.startswith(HELP_COMMAND):
        await message.reply(
            "📜 Напиши вопрос, например: «Хранитель, кто такая Агата?»\nИли используй команду: Глоссарий: агата")
        return

    # 🔹 Обработка запросов вида: "Глоссарий Агата", "глоссарий: ядро"
    if text.lower().startswith(GLOSSARY_TRIGGER_WORD):
        query = text[9:].strip()
        log.info(f"🔎 Глоссарий-запрос: {query}")

        if not query:
            await message.reply("Что искать в глоссарии?")
            log.warning(f"🔎 Глоссарий: не получен запрос.")
            return

        result = search_archive(query, only_glossary=True)
        if result:
            await message.reply(result)
            log.info(f"🔎 Глоссарий-ответ: {result}")
        else:
            log.warning(f"🔎 Глоссарий: информация не нашлась.")
            await message.reply("В глоссарии нет информации по запросу.")
        return

    if "?" in text:  # если в тексте есть вопросительный знак

        # 1. Поиск контекста в архиве
        relevant_info = search_archive(text)

        # 🔍 Fallback, если совпадений не найдено
        if not relevant_info:
            relevant_info = "Архив был поврежден."

        # 2. Формирование сообщений для ChatGPT
        log.info("Формирование сообщений для ChatGPT...")
        messages = [
            {"role": "system", "content": ARCHIVE_KEEPER_PROMPT}
        ]
        if relevant_info:
            # Добавляем найденную информацию из архива как часть системы или как отдельное сообщение
            log.info("Добавляем найденную информацию из архива как часть системы:")
            messages.append({
                "role": "system",
                "content": f"Контекст из архива: {relevant_info}"
            })

        # Очистка от "опасных" слов
        cleaned_text = clean_for_openai(text)

        # Ограничение длины, если длинный вопрос
        if len(cleaned_text) > MAX_USER_INPUT_LENGTH and "?" in cleaned_text:
            log.info("✂️ Запрос длинный. Обрезаем до вопросительного предложения.")
            cleaned_text = extract_question_part(cleaned_text)

        messages.append({"role": "user", "content": cleaned_text})

        # 3. Запрос к OpenAI ChatCompletion
        log.info(f"🔁 Запрос к OpenAI: {messages}")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",  # или "gpt-4" при наличии доступа
                messages=messages
            )
            log.info(f"🤖 Ответ от OpenAI: {response}")
        except Exception as e:
            await message.reply("Что-то пошло не так...")
            log.error(f"⚠️ OpenAI API error: {e}")
            return

        # 4. Получение ответа и отправка в чат
        answer = response.choices[0].message.content
        await message.reply(answer)

        # 5. Логируем запрос-ответ в консоль
        log.info(f"💬 Q: {text}\n💬 A: {answer}\n{'-' * 40}")
    # Если в сообщении нет вопроса, бот ничего не отвечает (можно добавить другую логику при желании)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    log.info("Бот запускается...")
    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        log.error("‼️ Критическая ошибка:")
        traceback.print_exc()
