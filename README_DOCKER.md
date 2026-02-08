# Lang Courses Telegram Bot - Docker Deployment

## 📦 Структура контейнеров

Проект состоит из 4 Docker контейнеров:

1. **postgres** - База данных PostgreSQL
2. **admin** - Admin Panel (Node.js backend + React frontend)
3. **bot** - Telegram Bot (Python)
4. **intelligence** - AI модули (Python)

## 🚀 Быстрый старт

### 1. Подготовка

Убедитесь, что у вас установлены:
- Docker (20.10+)
- Docker Compose (2.0+)

### 2. Настройка переменных окружения

Скопируйте файл с примером и заполните его:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `POSTGRES_PASSWORD` - надёжный пароль для БД
- API ключи для AI сервисов
- Другие необходимые переменные

### 3. Сборка и запуск

```bash
# Собрать все контейнеры
docker-compose build

# Запустить все сервисы
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Посмотреть логи конкретного сервиса
docker-compose logs -f bot
docker-compose logs -f admin
```

### 4. Проверка работы

- **Admin Panel**: http://localhost:3001
- **PostgreSQL**: localhost:5432
- **Bot**: Проверьте в Telegram

## 🛠 Полезные команды

```bash
# Остановить все контейнеры
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v

# Перезапустить конкретный сервис
docker-compose restart bot

# Просмотр запущенных контейнеров
docker-compose ps

# Выполнить команду внутри контейнера
docker-compose exec bot python -m bot.some_command
docker-compose exec admin npm run migrate

# Пересобрать контейнер после изменений
docker-compose build --no-cache admin
docker-compose up -d admin
```

## 📁 Структура файлов

```
.
├── admin-panel/
│   ├── backend/
│   └── frontend/
├── bot/
├── intelligence/
├── Dockerfile.admin        # Dockerfile для admin panel
├── Dockerfile.bot          # Dockerfile для бота
├── Dockerfile.intelligence # Dockerfile для AI модулей
├── docker-compose.yml      # Конфигурация всех сервисов
├── .dockerignore          # Исключения при сборке
├── .env                   # Переменные окружения (НЕ КОММИТИТЬ!)
├── .env.example          # Пример переменных
└── requirements.txt      # Python зависимости
```

## 🔧 Продакшн рекомендации

### Безопасность

1. **Никогда не коммитьте .env файл!** Добавьте его в .gitignore
2. Используйте сильные пароли для БД
3. Ограничьте доступ к портам через firewall
4. Используйте HTTPS для admin panel (добавьте nginx reverse proxy)

### Оптимизация

1. **Multi-stage builds** уже используются для admin panel
2. Рассмотрите использование `.dockerignore` для уменьшения размера образов
3. Используйте volume для логов и данных, которые нужно сохранить

### Мониторинг

```bash
# Просмотр использования ресурсов
docker stats

# Проверка здоровья контейнеров
docker-compose ps
```

## 📝 Примечания

### Backend Admin Panel должен отдавать статику Frontend

Убедитесь, что в вашем backend есть middleware для отдачи статических файлов из папки `public`:

```typescript
// В admin-panel/backend/src/index.ts
import express from 'express';
import path from 'path';

const app = express();

// Отдача статики frontend
app.use(express.static(path.join(__dirname, '../public')));

// API routes
app.use('/api', apiRouter);

// Для SPA - все остальные запросы отдают index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});
```

### Intelligence контейнер

Если `intelligence` используется только как библиотека для импорта ботом, то его можно не запускать как отдельный сервис. В этом случае просто включите код intelligence в bot контейнер.

Текущая конфигурация оставляет intelligence запущенным для возможности будущего расширения (например, если захотите сделать из него отдельный API сервис).

## 🐛 Troubleshooting

### Ошибка подключения к БД

```bash
# Проверьте, что postgres запущен
docker-compose ps postgres

# Проверьте логи
docker-compose logs postgres

# Проверьте переменные окружения
docker-compose exec bot env | grep DATABASE
```

### Ошибки сборки admin panel

```bash
# Убедитесь, что package.json и package-lock.json есть в обеих папках
ls -la admin-panel/backend/package.json
ls -la admin-panel/frontend/package.json

# Пересоберите без кэша
docker-compose build --no-cache admin
```

### Bot не запускается

```bash
# Проверьте логи
docker-compose logs bot

# Убедитесь, что .env файл на месте и содержит TELEGRAM_BOT_TOKEN
cat .env | grep TELEGRAM_BOT_TOKEN
```

## 📮 Деплой на сервер

1. Скопируйте все файлы на сервер:
```bash
scp -r . user@your-server:/path/to/project
```

2. На сервере выполните:
```bash
cd /path/to/project
cp .env.example .env
nano .env  # Заполните переменные
docker-compose up -d
```

3. Настройте nginx reverse proxy для admin panel (опционально):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📄 Лицензия

Укажите вашу лицензию здесь.
