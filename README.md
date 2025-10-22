# Telegram Bot GradeUp

## Установка и запуск

1. Клонирование репозитория:

```bash
  git clone https://github.com/dergunovmxm/lang-courses-tg-bot.git
  cd lang-courses-tg-bot
```

2. Установка зависимостей:

```bash
  pip install -r requirements.txt
```

3. Настройка окружения:

```bash
  cp .env.example .env
```

4. Запуск бота:

```bash
  python main.py
```

## Команды бота
* /start - Запустить бота
* /info - Информация о пользователе
* /timer - Запустить минутный таймер
* /status - Статус бота


## Структура проекта

lang-courses-tg-bot/
├── main.py                 # Точка входа, инициализация бота
├── config.py              # Конфигурация, загрузка переменных окружения
├── requirements.txt       # Зависимости проекта
├── .env.example          # Пример файла окружения
├── utils/                # Утилиты и вспомогательные модули
│   ├── __init__.py
│   ├── logging_config.py # Настройка логирования
│   ├── time_utils.py     # Функции для работы с временем
│   ├── startup_utils.py  # Сообщения при запуске/остановке
│   └── cmd_logger_utils.py # Команды бота и логика
└── app/                  # Основное приложение
    └── handlers/         # Обработчики сообщений
        ├── start.py      # Обработчик команды /start
        ├── info.py       # Обработчик команды /info
        └── timer.py      # Обработчик команды /timer