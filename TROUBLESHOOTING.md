# Решение проблем

## Docker не запускается

### Проблема: "failed to connect to the docker API"

**Решение:**
1. Убедитесь, что Docker Desktop установлен и запущен
2. Проверьте, что Docker Desktop работает (иконка в системном трее)
3. Если Docker Desktop не запущен:
   - Запустите Docker Desktop из меню Пуск
   - Дождитесь полной загрузки (иконка перестанет мигать)
   - Попробуйте снова запустить `docker-compose up --build`

### Проверка Docker

```bash
# Проверка версии Docker
docker --version

# Проверка статуса Docker
docker ps

# Если Docker не запущен, вы увидите ошибку подключения
```

## Ошибки при сборке

### Проблема: "Cannot connect to Docker daemon"

**Решение:**
1. Запустите Docker Desktop
2. Убедитесь, что Docker Desktop полностью загружен
3. Перезапустите терминал/PowerShell

### Проблема: "Port already in use"

**Решение:**
Если порты 3000 или 8000 заняты:

1. Найдите процесс, использующий порт:
```powershell
# Windows PowerShell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

2. Остановите процесс или измените порты в `docker-compose.yml`:
```yaml
ports:
  - "3001:80"  # вместо 3000:80
  - "8001:8000"  # вместо 8000:8000
```

## Ошибки базы данных

### Проблема: "could not connect to server"

**Решение:**
1. Убедитесь, что контейнер базы данных запущен:
```bash
docker-compose ps
```

2. Проверьте логи базы данных:
```bash
docker-compose logs db
```

3. Пересоздайте контейнеры:
```bash
docker-compose down -v
docker-compose up --build
```

## Ошибки фронтенда

### Проблема: "Cannot GET /"

**Решение:**
1. Убедитесь, что фронтенд контейнер запущен:
```bash
docker-compose ps frontend
```

2. Проверьте логи:
```bash
docker-compose logs frontend
```

3. Пересоберите фронтенд:
```bash
docker-compose build frontend
docker-compose up frontend
```

## Ошибки бэкенда

### Проблема: "ModuleNotFoundError"

**Решение:**
1. Пересоберите контейнер:
```bash
docker-compose build web
docker-compose up web
```

### Проблема: "No such file or directory: manage.py"

**Решение:**
Убедитесь, что вы находитесь в корневой директории проекта при запуске docker-compose.

## Ошибки миграций

### Проблема: "django.db.utils.OperationalError"

**Решение:**
1. Убедитесь, что база данных запущена:
```bash
docker-compose up db
```

2. Выполните миграции вручную:
```bash
docker-compose exec web python manage.py migrate
```

## Общие решения

### Полная переустановка

Если ничего не помогает:

```bash
# Остановить и удалить все контейнеры и volumes
docker-compose down -v

# Удалить образы (опционально)
docker-compose rm -f

# Пересобрать и запустить
docker-compose up --build
```

### Очистка Docker

```bash
# Удалить неиспользуемые контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Удалить неиспользуемые volumes
docker volume prune
```

## Проверка логов

Для диагностики проблем всегда проверяйте логи:

```bash
# Все сервисы
docker-compose logs

# Конкретный сервис
docker-compose logs web
docker-compose logs frontend
docker-compose logs db

# Следить за логами в реальном времени
docker-compose logs -f
```

## Полезные команды

```bash
# Статус всех контейнеров
docker-compose ps

# Перезапуск сервиса
docker-compose restart web

# Остановка всех сервисов
docker-compose stop

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр использования ресурсов
docker stats
```

