# Инструкция по развертыванию

## Быстрый старт с Docker

1. **Клонируйте проект или скопируйте файлы**

2. **Создайте файл `.env`**:
```bash
cp .env.example .env
```

Отредактируйте `.env` и установите:
- `SECRET_KEY` - секретный ключ Django (можно сгенерировать командой: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG=True` для разработки, `False` для продакшена
- `ALLOWED_HOSTS` - список разрешенных хостов через запятую

3. **Запустите контейнеры**:
```bash
docker-compose up --build
```

4. **Создайте суперпользователя** (в другом терминале):
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Приложение готово к использованию!**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

## Локальное развертывание (без Docker)

### Требования
- Python 3.11+
- PostgreSQL 12+

### Шаги

1. **Создайте виртуальное окружение**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. **Установите зависимости**:
```bash
pip install -r requirements.txt
```

3. **Настройте PostgreSQL**:
```sql
CREATE DATABASE game_db;
CREATE USER game_user WITH PASSWORD 'your_password';
ALTER ROLE game_user SET client_encoding TO 'utf8';
ALTER ROLE game_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE game_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE game_db TO game_user;
```

4. **Создайте файл `.env`** с настройками базы данных:
```
DB_NAME=game_db
DB_USER=game_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

5. **Выполните миграции**:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Создайте суперпользователя**:
```bash
python manage.py createsuperuser
```

7. **Соберите статические файлы**:
```bash
python manage.py collectstatic
```

8. **Запустите сервер**:
```bash
python manage.py runserver
```

## Настройка для продакшена

### Рекомендации по безопасности

1. **Измените SECRET_KEY** в `.env` на случайный ключ
2. **Установите DEBUG=False**
3. **Настройте ALLOWED_HOSTS** с вашим доменом
4. **Используйте HTTPS** (настройте nginx/apache как reverse proxy)
5. **Настройте CORS_ALLOWED_ORIGINS** в `settings.py` для вашего фронтенда

### Пример настройки nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
```

### Использование Gunicorn

Для продакшена используйте Gunicorn вместо встроенного сервера Django:

```bash
pip install gunicorn
gunicorn game_backend.wsgi:application --bind 0.0.0.0:8000
```

Или в docker-compose.yml:
```yaml
command: gunicorn game_backend.wsgi:application --bind 0.0.0.0:8000
```

## Резервное копирование базы данных

### Экспорт
```bash
docker-compose exec db pg_dump -U postgres game_db > backup.sql
```

### Импорт
```bash
docker-compose exec -T db psql -U postgres game_db < backup.sql
```

## Мониторинг и логи

Просмотр логов Docker:
```bash
docker-compose logs -f web
docker-compose logs -f db
```

## Обновление приложения

1. Остановите контейнеры:
```bash
docker-compose down
```

2. Обновите код

3. Пересоберите и запустите:
```bash
docker-compose up --build -d
```

4. Выполните миграции (если есть новые):
```bash
docker-compose exec web python manage.py migrate
```

