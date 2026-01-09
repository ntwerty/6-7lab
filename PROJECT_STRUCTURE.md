# Структура проекта

## Обзор

Проект представляет собой полнофункциональный backend для браузерной игры "Арканоид" на Django и Django REST Framework.

## Структура файлов

```
game/
├── game_backend/              # Основной проект Django
│   ├── __init__.py
│   ├── settings.py           # Настройки проекта
│   ├── urls.py               # Главные URL маршруты
│   ├── wsgi.py               # WSGI конфигурация
│   └── asgi.py               # ASGI конфигурация
│
├── game_app/                 # Основное приложение
│   ├── __init__.py
│   ├── admin.py             # Административная панель
│   ├── apps.py              # Конфигурация приложения
│   ├── models.py            # Модели данных
│   ├── views.py             # API представления
│   ├── serializers.py       # Сериализаторы DRF
│   ├── urls.py              # URL маршруты API
│   ├── permissions.py       # Кастомные разрешения
│   └── signals.py            # Django сигналы
│
├── manage.py                # Django management script
├── requirements.txt         # Зависимости Python
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose конфигурация
├── .env.example            # Пример файла переменных окружения
├── .gitignore              # Git ignore правила
│
├── README.md               # Основная документация
├── API_EXAMPLES.md         # Примеры использования API
├── DEPLOYMENT.md           # Инструкции по развертыванию
├── PROJECT_STRUCTURE.md     # Этот файл
└── create_test_data.py     # Скрипт для создания тестовых данных
```

## Модели данных

### TimeStampedModel (абстрактная)
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### User (расширенная модель пользователя)
- Наследуется от `AbstractUser`
- `email` - Email (уникальный)
- `is_guest` - Флаг гостевого аккаунта

### UserProfile
- `user` - Связь с User (OneToOne)
- `avatar` - Аватар пользователя
- `bio` - Биография
- `date_of_birth` - Дата рождения
- `total_score` - Общий счет
- `games_played` - Количество игр

### GameSession
- `user` - Пользователь (ForeignKey)
- `game_state` - JSON с состоянием игры
- `score` - Счет
- `level` - Уровень
- `time_played` - Время игры в секундах
- `is_completed` - Завершена ли игра
- `difficulty` - Сложность (easy/medium/hard)

### Leaderboard
- `user` - Пользователь (ForeignKey)
- `game_session` - Игровая сессия (ForeignKey)
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

### UserAchievement
- `user` - Пользователь (ForeignKey)
- `achievement` - Достижение (ForeignKey)
- `unlocked_at` - Дата получения

### Friend
- `from_user` - Отправитель запроса (ForeignKey)
- `to_user` - Получатель запроса (ForeignKey)
- `status` - Статус (pending/accepted/rejected)

### Challenge
- `challenger` - Бросающий вызов (ForeignKey)
- `challenged` - Принимающий вызов (ForeignKey)
- `target_score` - Целевой счет
- `status` - Статус (pending/accepted/completed/declined)
- `challenger_score` - Счет бросающего вызов
- `challenged_score` - Счет принимающего вызов
- `expires_at` - Дата истечения

## API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `POST /api/auth/refresh/` - Обновление токена

### Профили
- `GET /api/profiles/` - Список профилей
- `GET /api/profiles/me/` - Мой профиль
- `GET /api/profiles/{id}/public/` - Публичный профиль
- `PUT/PATCH /api/profiles/{id}/` - Обновление профиля

### Игровые сессии
- `GET /api/game-sessions/` - Список сессий
- `POST /api/game-sessions/` - Создать сессию
- `GET /api/game-sessions/latest/` - Последнее сохранение
- `GET /api/game-sessions/{id}/` - Детали сессии

### Таблица лидеров
- `GET /api/leaderboard/` - Таблица лидеров
- `GET /api/leaderboard/top/` - Топ игроков

### Достижения
- `GET /api/achievements/` - Список достижений
- `GET /api/user-achievements/` - Достижения пользователя
- `GET /api/user-achievements/my_achievements/` - Мои достижения

### Друзья
- `GET /api/friends/` - Список друзей
- `POST /api/friends/` - Отправить запрос
- `POST /api/friends/{id}/accept/` - Принять запрос
- `POST /api/friends/{id}/reject/` - Отклонить запрос
- `GET /api/friends/my_friends/` - Мои друзья

### Вызовы
- `GET /api/challenges/` - Список вызовов
- `POST /api/challenges/` - Создать вызов
- `POST /api/challenges/{id}/accept/` - Принять вызов
- `POST /api/challenges/{id}/submit_score/` - Отправить счет

## Уровни доступа

1. **Гость** - Только чтение (таблица лидеров, публичные профили)
2. **Авторизованный пользователь** - Полный доступ к своему контенту
3. **Администратор** - Полный доступ через Django Admin

## Безопасность

- Пароли хранятся в виде хешей (PBKDF2)
- Защита от SQL-инъекций через ORM Django
- Защита от XSS через экранирование в шаблонах
- JWT аутентификация
- CORS настройки для фронтенда

## Особенности реализации

- Автоматическое создание профиля при регистрации (сигналы)
- Автоматическая проверка и выдача достижений при сохранении сессии
- Автоматическое обновление таблицы лидеров
- Экспорт данных в XLSX из админки
- Фильтрация и сортировка в API

