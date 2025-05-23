
# 🗝️ Archive Keeper Bot

**Телеграм-бот в образе загадочного Хранителя Архива**, который отвечает на вопросы, используя фрагменты из архива, глоссарий понятий и силу OpenAI.  
Идеален для текстовых RPG, мастеров, мира с лором и любителей атмосферного взаимодействия.

---

## 🔮 Возможности

- 🧠 **Ответы от имени "Хранителя Архива"** — кратко, образно, метафорично
- 📜 **Глоссарий терминов** — мгновенный локальный ответ без нейросети
- 📂 **Поиск в текстовых архивах** — если терминов нет в глоссарии
- 🔐 **Фильтрация вредных команд** — защита от сброса промпта и вмешательства
- ✂️ **Обрезка длинных запросов** — только суть, только вопрос
- 📝 **Ротация логов** — лог-файлы по дням, максимум 10 штук

---

## 🚀 Быстрый старт

### 💾 Установка

```bash
git clone https://github.com/ziltorian/archive-keeper-bot.git
cd archive-keeper-bot
python -m venv .venv
.venv\Scripts\activate        # Windows
# или
source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

---

### 🔧 Настройка

Создай файл `.env` (на основе `.env.example`):

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
OPENAI_API_KEY=your-openai-api-key
```

Убедись, что у тебя есть папка `archive/` с текстами и `Глоссарий_Хранителя_Архива.json`.

---

### 🟢 Запуск

```bash
python bot.py
```

---

## ✏️ Примеры команд

```
Хранитель, что ты знаешь о Разломе?
Глоссарий: Цикл
Я хочу услышать про Агату.
```

---

## ⚙️ Структура проекта

```
archive-keeper-bot/         ← корневая папка проекта
├── bot.py                  ← главный файл, запуск бота
├── config.py               ← настройки и параметры
├── logger_setup.py         ← логгер, работает во всех модулях
├── requirements.txt        ← список библиотек
├── .env.example            ← пример конфигурации без токенов
├── archive/                ← текстовые архивы (глоссарий, тексты)
│   └── Глоссарий_Хранителя_Архива.json
├── logs/                   ← авто-создаётся, лог-файлы
├── .gitignore              ← игнорируем лишние файлы при пуше в Git
```

---

## 🧙‍♂️ О проекте

Этот бот создаёт иллюзию "живой памяти" — он не просто отвечает, а **вспоминает**.  
Подходит для атмосферных чатов, сюжета, ролевых диалогов или как прототип DM-бота для DnD.

---

## 🛡 Автор

Разработан с душой и вниманием к стилю:  
**Alex Ziltorian** ✨  
GitHub: [@ziltorian](https://github.com/ziltorian)

---

## ⭐ Хочешь помочь?

- Поставь ⭐ звезду репозиторию
- Сделай форк и предложи улучшения
- Поделись ботом с друзьями!