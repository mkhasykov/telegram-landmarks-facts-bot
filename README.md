# Telegram Location Bot

Telegram-бот "Факты о месте по геолокации" — находит интересные факты о достопримечательностях рядом с отправленной геолокацией.

## 🚀 Возможности

- 📍 Обработка геолокации от пользователя
- 🔍 Поиск ближайших достопримечательностей через Wikipedia API
- 🤖 Генерация интересных фактов через GPT-4o-mini
- 📊 Логирование для анализа качества работы

## 📋 Требования

- Python 3.12+
- Telegram Bot Token
- OpenAI API Key

## 🛠 Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/mkhasykov/telegram-landmarks-facts-bot.git
cd telegram-landmarks-facts-bot
```

2. **Создайте виртуальное окружение:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -e .
```

4. **Настройте переменные окружения:**
Создайте файл `.env` в корне проекта:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
DEBUG=false
LOG_LEVEL=INFO
```

5. **Создайте тестовые данные:**
```bash
python -m src.wikipedia_parser --categories all --limit 10 --output data/landmarks_dataset.json --verbose
```

## 🚀 Запуск

### Локальный запуск (polling):
```bash
python -m src.main
```

### Docker (production):
```bash
docker build -t telegram-location-bot .
docker run -d --env-file .env telegram-location-bot
```

### Webhook (production):
Установите переменную окружения:
```env
WEBHOOK_URL=https://your-server.com/webhook
```

## 📊 Использование

1. Найдите бота в Telegram
2. Отправьте команду `/start`
3. Поделитесь своей геолокацией
4. Получите интересный факт о ближайшей достопримечательности!

## 🧪 Тестирование

Создание тестовых данных:
```bash
# Только российские достопримечательности
python -m src.wikipedia_parser --categories russian --limit 15 --output data/russian_landmarks.json

# Только мировые достопримечательности  
python -m src.wikipedia_parser --categories world --limit 15 --output data/world_landmarks.json

# Все категории
python -m src.wikipedia_parser --categories all --limit 10 --output data/all_landmarks.json
```

## 📁 Структура проекта

```
telegram-landmarks-facts-bot/
├── src/
│   ├── __init__.py
│   ├── main.py              # Основной модуль приложения
│   ├── config.py            # Конфигурация
│   ├── bot_handlers.py      # Обработчики Telegram бота
│   ├── location_service.py  # Сервис обработки локации
│   └── wikipedia_parser.py  # Парсер Wikipedia API
├── data/
│   └── landmarks_dataset.json  # Датасет достопримечательностей
├── tests/                   # Тесты
├── docs/                    # Документация
├── prompts/                 # Промпты для разработки
├── pyproject.toml          # Конфигурация проекта
├── Dockerfile              # Docker контейнер
└── README.md               # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | **Обязательно** |
| `OPENAI_API_KEY` | API ключ OpenAI | **Обязательно** |
| `OPENAI_MODEL` | Модель OpenAI | `gpt-4o-mini` |
| `DEBUG` | Режим отладки | `false` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `WEBHOOK_URL` | URL для webhook | `null` (polling) |
| `PORT` | Порт для webhook | `8080` |

### Настройки поиска:

- **Радиус поиска**: 10 км от указанной локации
- **Максимальное количество результатов**: 1 ближайшая достопримечательность
- **Источники данных**: Wikipedia API (русский и английский)

## 📈 Логирование

Бот логирует:
- Входящие запросы от пользователей
- Найденные достопримечательности
- Сгенерированные факты
- Ошибки и исключения

Логи можно использовать для анализа качества работы бота.

## 🛡 Безопасность

- Никогда не коммитьте `.env` файл
- Используйте переменные окружения для чувствительных данных
- Регулярно обновляйте зависимости

## 🤝 Разработка

Для разработки установите дополнительные зависимости:
```bash
pip install -e ".[dev]"
```

Запуск линтеров:
```bash
black src/
ruff check src/
mypy src/
```

## 📄 Лицензия

MIT License

## 🚨 Troubleshooting

### Частые проблемы:

1. **"Configuration error: TELEGRAM_BOT_TOKEN is required"**
   - Убедитесь, что создали файл `.env` с правильными токенами

2. **"No landmarks found near X, Y"**
   - Проверьте, что файл `data/landmarks_dataset.json` существует
   - Создайте тестовые данные: `python -m src.wikipedia_parser --categories all --limit 20`

3. **"Error generating fact with OpenAI"**
   - Проверьте правильность API ключа OpenAI
   - Убедитесь, что у вас есть доступ к модели `gpt-4o-mini`

### Поддержка:

Если у вас возникли проблемы, создайте issue в репозитории. 