# Frontend для игры Арканоид

React приложение для браузерной игры Арканоид с интеграцией с Django REST API.

## Технологии

- React 18.2
- React Router 6
- Axios для HTTP запросов
- CSS3 для стилизации

## Структура проекта

```
frontend/
├── public/           # Статические файлы
├── src/
│   ├── components/  # React компоненты
│   ├── contexts/    # React контексты (AuthContext)
│   ├── pages/       # Страницы приложения
│   ├── services/    # API сервисы
│   ├── App.js       # Главный компонент
│   └── index.js     # Точка входа
├── Dockerfile       # Docker образ для продакшена
├── nginx.conf       # Конфигурация Nginx
└── package.json     # Зависимости
```

## Локальная разработка

### Установка зависимостей
```bash
npm install
```

### Запуск в режиме разработки
```bash
npm start
```

Приложение будет доступно по адресу http://localhost:3000

### Сборка для продакшена
```bash
npm run build
```

## Docker

### Сборка образа
```bash
docker build -t arkanoid-frontend .
```

### Запуск контейнера
```bash
docker run -p 3000:80 arkanoid-frontend
```

## Переменные окружения

- `REACT_APP_API_URL` - URL бэкенд API (по умолчанию `/api`)

## Функциональность

- ✅ Регистрация и авторизация
- ✅ Игра Арканоид с Canvas
- ✅ Сохранение/загрузка игрового прогресса
- ✅ Таблица лидеров
- ✅ Система достижений
- ✅ Система друзей
- ✅ Профиль пользователя

