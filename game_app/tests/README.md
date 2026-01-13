# Инструкция по запуску тестов

## Быстрый старт

### Запуск всех тестов

```bash
python manage.py test
```

### Запуск с подробным выводом

```bash
python manage.py test --verbosity=2
```

## Запуск отдельных модулей тестов

### Тесты моделей
```bash
python manage.py test game_app.tests.test_models
```

### Тесты сериализаторов
```bash
python manage.py test game_app.tests.test_serializers
```

### Тесты представлений
```bash
python manage.py test game_app.tests.test_views
```

### Тесты аутентификации
```bash
python manage.py test game_app.tests.test_auth
```

### Интеграционные тесты
```bash
python manage.py test game_app.tests.test_integration
```

### Тесты админки
```bash
python manage.py test game_app.tests.test_admin
```

### Тесты безопасности
```bash
python manage.py test game_app.tests.test_security
```

## Запуск конкретного теста

```bash
python manage.py test game_app.tests.test_models.UserModelTest.test_create_user
```

## Запуск с покрытием кода

### Установка coverage
```bash
pip install coverage
```

### Запуск тестов с покрытием
```bash
coverage run --source='.' manage.py test
```

### Просмотр отчета
```bash
coverage report
```

### HTML отчет
```bash
coverage html
# Откройте htmlcov/index.html в браузере
```

## Структура тестов

```
game_app/tests/
├── __init__.py
├── test_models.py          # Тесты моделей
├── test_serializers.py     # Тесты сериализаторов/форм
├── test_views.py          # Тесты представлений
├── test_auth.py           # Тесты аутентификации и авторизации
├── test_integration.py    # Интеграционные тесты
├── test_admin.py          # Тесты административной панели
└── test_security.py       # Тесты безопасности
```

## Что тестируется

### Модели
- Создание и сохранение моделей в БД
- Корректность работы связей (ForeignKey, OneToOne)
- Автоматическое заполнение created_at и updated_at
- Валидация данных на уровне моделей

### Сериализаторы/Формы
- Валидность форм с корректными данными
- Невалидность форм с некорректными данными
- Формы регистрации и логина

### Представления
- HTTP-ответы (200, 201, 404, 401, 403)
- Редиректы
- CRUD-операции
- Доступ для разных типов пользователей

### Аутентификация и авторизация
- Регистрация пользователя
- Вход в систему
- Права доступа для гостей, пользователей и администраторов

### Интеграционные тесты
- Полный цикл игровой сессии
- Система друзей
- Завершение вызовов
- Сохранение данных в БД
- Изменения состояния системы

### Административная панель
- Доступ к админ-панели
- Экспорт в XLSX
- Структура и содержимое файла

### Безопасность
- Защита от SQL-инъекций
- Защита от XSS
- Хеширование паролей
- Авторизация и доступ к данным

## Требования

- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL (для тестов используется тестовая БД SQLite)

## Примечания

- Тесты используют тестовую базу данных (SQLite по умолчанию)
- Каждый тест выполняется в изолированной транзакции
- Тестовые данные создаются в методе `setUp()` каждого теста
- После выполнения теста все данные автоматически удаляются

