# Примеры использования API

## Аутентификация

### Регистрация
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "player1",
  "email": "player1@example.com",
  "password": "securepassword123",
  "password2": "securepassword123"
}

Response:
{
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "date_joined": "2024-01-01T12:00:00Z",
    "is_guest": false
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Вход
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "player1",
  "password": "securepassword123"
}

Response:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Обновление токена
```bash
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Профили

### Получить свой профиль
```bash
GET /api/profiles/me/
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "date_joined": "2024-01-01T12:00:00Z",
    "is_guest": false
  },
  "username": "player1",
  "avatar": null,
  "bio": "",
  "date_of_birth": null,
  "total_score": 0,
  "games_played": 0,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Обновить профиль
```bash
PATCH /api/profiles/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "bio": "Люблю играть в арканоид!",
  "date_of_birth": "1990-01-01"
}
```

## Игровые сессии

### Сохранить игровую сессию
```bash
POST /api/game-sessions/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "game_state": {
    "ball": {"x": 400, "y": 300, "vx": 5, "vy": -5},
    "paddle": {"x": 350, "width": 100},
    "blocks": [
      {"x": 100, "y": 50, "destroyed": false},
      {"x": 200, "y": 50, "destroyed": true}
    ],
    "lives": 3
  },
  "score": 1250,
  "level": 3,
  "time_played": 180,
  "is_completed": false,
  "difficulty": "medium"
}

Response:
{
  "id": 1,
  "user": "player1",
  "game_state": {...},
  "score": 1250,
  "level": 3,
  "time_played": 180,
  "is_completed": false,
  "difficulty": "medium",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Загрузить последнее сохранение
```bash
GET /api/game-sessions/latest/
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "user": "player1",
  "game_state": {...},
  "score": 1250,
  "level": 3,
  "time_played": 180,
  "is_completed": false,
  "difficulty": "medium",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Таблица лидеров

### Получить таблицу лидеров
```bash
GET /api/leaderboard/?difficulty=medium&ordering=-score
Authorization: Bearer {access_token}  # Опционально для гостей

Response:
{
  "count": 100,
  "next": "http://localhost:8000/api/leaderboard/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "username": "player1",
      "score": 5000,
      "rank": 1,
      "date_achieved": "2024-01-01T12:00:00Z",
      "difficulty": "medium",
      "created_at": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

### Получить топ игроков
```bash
GET /api/leaderboard/top/?limit=10&difficulty=hard

Response:
[
  {
    "id": 1,
    "user": 1,
    "username": "player1",
    "score": 10000,
    "rank": 1,
    "date_achieved": "2024-01-01T12:00:00Z",
    "difficulty": "hard",
    "created_at": "2024-01-01T12:00:00Z"
  },
  ...
]
```

## Достижения

### Получить все достижения
```bash
GET /api/achievements/

Response:
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Первые шаги",
      "description": "Наберите 100 очков",
      "icon": "/media/achievements/first_steps.png",
      "points_required": 100,
      "level_required": 1,
      "created_at": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

### Получить свои достижения
```bash
GET /api/user-achievements/my_achievements/
Authorization: Bearer {access_token}

Response:
[
  {
    "id": 1,
    "achievement": {
      "id": 1,
      "name": "Первые шаги",
      "description": "Наберите 100 очков",
      "icon": "/media/achievements/first_steps.png",
      "points_required": 100,
      "level_required": 1,
      "created_at": "2024-01-01T12:00:00Z"
    },
    "unlocked_at": "2024-01-01T12:05:00Z",
    "created_at": "2024-01-01T12:05:00Z",
    "updated_at": "2024-01-01T12:05:00Z"
  },
  ...
]
```

## Друзья

### Отправить запрос в друзья
```bash
POST /api/friends/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "to_username": "player2"
}

Response:
{
  "id": 1,
  "from_user": 1,
  "to_user": 2,
  "from_username": "player1",
  "to_username": "player2",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Принять запрос в друзья
```bash
POST /api/friends/{id}/accept/
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "from_user": 1,
  "to_user": 2,
  "from_username": "player1",
  "to_username": "player2",
  "status": "accepted",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### Получить список друзей
```bash
GET /api/friends/my_friends/
Authorization: Bearer {access_token}

Response:
[
  {
    "id": 1,
    "from_user": 1,
    "to_user": 2,
    "from_username": "player1",
    "to_username": "player2",
    "status": "accepted",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:05:00Z"
  },
  ...
]
```

## Вызовы

### Создать вызов
```bash
POST /api/challenges/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "challenged_username": "player2",
  "target_score": 2000,
  "expires_at": "2024-01-08T12:00:00Z"
}

Response:
{
  "id": 1,
  "challenger": 1,
  "challenged": 2,
  "challenger_username": "player1",
  "challenged_username": "player2",
  "target_score": 2000,
  "status": "pending",
  "challenger_score": null,
  "challenged_score": null,
  "expires_at": "2024-01-08T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Принять вызов
```bash
POST /api/challenges/{id}/accept/
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "challenger": 1,
  "challenged": 2,
  "challenger_username": "player1",
  "challenged_username": "player2",
  "target_score": 2000,
  "status": "accepted",
  "challenger_score": null,
  "challenged_score": null,
  "expires_at": "2024-01-08T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

### Отправить счет для вызова
```bash
POST /api/challenges/{id}/submit_score/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "score": 2500
}

Response:
{
  "id": 1,
  "challenger": 1,
  "challenged": 2,
  "challenger_username": "player1",
  "challenged_username": "player2",
  "target_score": 2000,
  "status": "completed",
  "challenger_score": 2500,
  "challenged_score": 1800,
  "expires_at": "2024-01-08T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:10:00Z"
}
```

