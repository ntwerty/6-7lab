# Браузерная игра "Арканоид"

Полнофункциональное веб-приложение с Django REST Framework backend и React frontend для игры Арканоид.

## Возможности

### Основной функционал
- ✅ Регистрация и авторизация пользователей (JWT токены)
- ✅ Управление профилями пользователей (аватар, биография, дата рождения)
- ✅ Сохранение и загрузка игровых сессий
- ✅ Таблица лидеров с фильтрацией по сложности и дате
- ✅ Система достижений
- ✅ Система друзей с возможностью отправки вызовов

### Административная панель
- ✅ Управление пользователями и контентом
- ✅ Экспорт игровых сессий в XLSX
- ✅ Назначение достижений пользователям
- ✅ Модерация пользовательского контента

### Безопасность
- ✅ Пароли хранятся в виде хешей (Django по умолчанию)
- ✅ Защита от SQL-инъекций (используется только ORM Django)
- ✅ Защита от XSS (экранирование данных в админке)
- ✅ JWT аутентификация

## Технологии

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL 15
- JWT аутентификация

### Frontend
- React 18.2
- React Router 6
- Axios
- Canvas API для игры

### Инфраструктура
- Docker & Docker Compose
- Nginx для фронтенда

## Установка и запуск

### С помощью Docker (рекомендуется)

1. Клонируйте репозиторий или скопируйте файлы проекта

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Запустите все контейнеры (backend, frontend, database):
```bash
docker-compose up --build
```

4. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Приложение будет доступно:
   - **Frontend (игра)**: http://localhost:3000
   - **Backend API**: http://localhost:8000/api/
   - **Admin панель**: http://localhost:8000/admin/

### Локальная установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте PostgreSQL базу данных

3. Создайте файл `.env` с настройками базы данных

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход (получение JWT токенов)
- `POST /api/auth/refresh/` - Обновление токена

### Профили
- `GET /api/profiles/` - Список профилей
- `GET /api/profiles/me/` - Мой профиль
- `GET /api/profiles/{id}/public/` - Публичный профиль
- `PUT /api/profiles/{id}/` - Обновление профиля

### Игровые сессии
- `GET /api/game-sessions/` - Список сессий
- `POST /api/game-sessions/` - Создать/сохранить сессию
- `GET /api/game-sessions/latest/` - Последнее сохранение
- `GET /api/game-sessions/{id}/` - Детали сессии

### Таблица лидеров
- `GET /api/leaderboard/` - Таблица лидеров
- `GET /api/leaderboard/top/` - Топ игроков (параметры: `limit`, `difficulty`)

### Достижения
- `GET /api/achievements/` - Список всех достижений
- `GET /api/user-achievements/` - Достижения пользователя
- `GET /api/user-achievements/my_achievements/` - Мои достижения

### Друзья
- `GET /api/friends/` - Список друзей и запросов
- `POST /api/friends/` - Отправить запрос в друзья
- `POST /api/friends/{id}/accept/` - Принять запрос
- `POST /api/friends/{id}/reject/` - Отклонить запрос
- `GET /api/friends/my_friends/` - Мои друзья

### Вызовы
- `GET /api/challenges/` - Список вызовов
- `POST /api/challenges/` - Создать вызов
- `POST /api/challenges/{id}/accept/` - Принять вызов
- `POST /api/challenges/{id}/submit_score/` - Отправить счет

## Модели данных

### UserProfile
- `avatar` - Аватар пользователя
- `bio` - Биография
- `date_of_birth` - Дата рождения
- `total_score` - Общий счет
- `games_played` - Количество сыгранных игр

### GameSession
- `game_state` - JSON с состоянием игры
- `score` - Счет
- `level` - Уровень
- `time_played` - Время игры в секундах
- `is_completed` - Завершена ли игра
- `difficulty` - Сложность (easy/medium/hard)

### Leaderboard
- `score` - Счет
- `rank` - Ранг
- `date_achieved` - Дата достижения
- `difficulty` - Сложность

### Achievement
- `name` - Название
- `description` - Описание
- `icon` - Иконка
- `points_required` - Требуется очков
- `level_required` - Требуется уровень

### Friend
- `from_user` - Отправитель запроса
- `to_user` - Получатель запроса
- `status` - Статус (pending/accepted/rejected)

### Challenge
- `challenger` - Бросающий вызов
- `challenged` - Принимающий вызов
- `target_score` - Целевой счет
- `status` - Статус (pending/accepted/completed/declined)

## Уровни доступа

1. **Гость** - Может только просматривать таблицу лидеров и публичные профили
2. **Авторизованный пользователь** - Может сохранять/загружать прогресс, получать достижения, управлять профилем, участвовать в рейтинге
3. **Администратор** - Полный доступ к Django Admin

## Разработка

### Структура проекта
```
game/
├── game_backend/          # Основные настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── game_app/              # Основное приложение
│   ├── models.py          # Модели данных
│   ├── views.py           # API представления
│   ├── serializers.py     # Сериализаторы
│   ├── admin.py           # Админ-панель
│   └── urls.py            # URL маршруты
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Тестирование

### Запуск тестов

```bash
# Запуск всех тестов
python manage.py test

# Запуск конкретного модуля тестов
python manage.py test game_app.tests.test_models
python manage.py test game_app.tests.test_views
python manage.py test game_app.tests.test_auth
python manage.py test game_app.tests.test_integration
python manage.py test game_app.tests.test_admin
python manage.py test game_app.tests.test_security

# Запуск с подробным выводом
python manage.py test --verbosity=2
```

### Покрытие тестами

Проект включает комплекс автоматических тестов:

- **Модели** (~95% покрытие) - тесты создания, валидации, связей между моделями
- **Сериализаторы/Формы** (~90% покрытие) - тесты валидности и невалидности данных
- **Представления** (~85% покрытие) - тесты HTTP ответов, CRUD операций, редиректов
- **Аутентификация** (~95% покрытие) - тесты регистрации, входа, прав доступа
- **Интеграционные тесты** (~90% покрытие) - тесты полного цикла основной услуги
- **Административная панель** (~80% покрытие) - тесты экспорта в XLSX
- **Безопасность** (~90% покрытие) - тесты защиты от SQL-инъекций, XSS, проверка хеширования паролей

Подробная информация о тестах и чек-лист для ручного тестирования находятся в файлах:
- [TESTING.md](TESTING.md) - руководство по тестированию и чек-лист
- [COVERAGE_REPORT.md](COVERAGE_REPORT.md) - отчет о покрытии тестами

## Лицензия

Этот проект создан в образовательных целях.

