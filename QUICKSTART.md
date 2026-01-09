# Быстрый старт

## Запуск с Docker (5 минут)

1. **Создайте файл `.env`**:
```bash
cp .env.example .env
```

2. **Запустите все контейнеры** (backend, frontend, database):
```bash
docker-compose up --build
```

3. **Создайте администратора** (в новом терминале):
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Готово!** Откройте:
   - **Игра (Frontend)**: http://localhost:3000
   - **API**: http://localhost:8000/api/
   - **Admin**: http://localhost:8000/admin/

## Создание тестовых данных

```bash
docker-compose exec web python manage.py shell < create_test_data.py
```

Или вручную:
```bash
docker-compose exec web python manage.py shell
# Затем скопируйте содержимое create_test_data.py
```

## Тестирование API

### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

### Вход
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Сохранение игровой сессии (требует токен)
```bash
curl -X POST http://localhost:8000/api/game-sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "game_state": {"ball": {"x": 400, "y": 300}},
    "score": 1000,
    "level": 2,
    "time_played": 120,
    "is_completed": false,
    "difficulty": "medium"
  }'
```

## Полезные команды

### Просмотр логов
```bash
docker-compose logs -f web
```

### Выполнение миграций
```bash
docker-compose exec web python manage.py migrate
```

### Создание миграций
```bash
docker-compose exec web python manage.py makemigrations
```

### Доступ к shell Django
```bash
docker-compose exec web python manage.py shell
```

### Остановка контейнеров
```bash
docker-compose down
```

### Остановка с удалением данных
```bash
docker-compose down -v
```

## Следующие шаги

1. Изучите [API_EXAMPLES.md](API_EXAMPLES.md) для подробных примеров API
2. Прочитайте [README.md](README.md) для полной документации
3. Ознакомьтесь с [DEPLOYMENT.md](DEPLOYMENT.md) для продакшн развертывания

