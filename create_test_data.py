"""
Скрипт для создания тестовых данных.
Запуск: python manage.py shell < create_test_data.py
или: python manage.py shell, затем скопировать содержимое
"""
from django.contrib.auth import get_user_model
from game_app.models import (
    UserProfile, Achievement, UserAchievement,
    GameSession, Leaderboard
)

User = get_user_model()

# Создаем тестовых пользователей
print("Создание тестовых пользователей...")
user1, created = User.objects.get_or_create(
    username='testuser1',
    defaults={'email': 'test1@example.com'}
)
if created:
    user1.set_password('testpass123')
    user1.save()
    print(f"Создан пользователь: {user1.username}")

user2, created = User.objects.get_or_create(
    username='testuser2',
    defaults={'email': 'test2@example.com'}
)
if created:
    user2.set_password('testpass123')
    user2.save()
    print(f"Создан пользователь: {user2.username}")

# Создаем достижения
print("\nСоздание достижений...")
achievements_data = [
    {
        'name': 'Первые шаги',
        'description': 'Наберите 100 очков',
        'points_required': 100,
        'level_required': 1,
    },
    {
        'name': 'Новичок',
        'description': 'Наберите 500 очков',
        'points_required': 500,
        'level_required': 1,
    },
    {
        'name': 'Опытный игрок',
        'description': 'Наберите 1000 очков',
        'points_required': 1000,
        'level_required': 2,
    },
    {
        'name': 'Мастер',
        'description': 'Наберите 5000 очков',
        'points_required': 5000,
        'level_required': 5,
    },
    {
        'name': 'Легенда',
        'description': 'Наберите 10000 очков',
        'points_required': 10000,
        'level_required': 10,
    },
]

for ach_data in achievements_data:
    achievement, created = Achievement.objects.get_or_create(
        name=ach_data['name'],
        defaults=ach_data
    )
    if created:
        print(f"Создано достижение: {achievement.name}")

# Создаем тестовые игровые сессии
print("\nСоздание тестовых игровых сессий...")
import json
from django.utils import timezone

game_state = {
    "ball": {"x": 400, "y": 300, "vx": 5, "vy": -5},
    "paddle": {"x": 350, "width": 100},
    "blocks": [
        {"x": 100, "y": 50, "destroyed": False},
        {"x": 200, "y": 50, "destroyed": True}
    ],
    "lives": 3
}

session1 = GameSession.objects.create(
    user=user1,
    game_state=game_state,
    score=1500,
    level=3,
    time_played=300,
    is_completed=True,
    difficulty='medium'
)
print(f"Создана сессия для {user1.username}: {session1.score} очков")

session2 = GameSession.objects.create(
    user=user2,
    game_state=game_state,
    score=2500,
    level=5,
    time_played=450,
    is_completed=True,
    difficulty='hard'
)
print(f"Создана сессия для {user2.username}: {session2.score} очков")

# Обновляем таблицу лидеров
print("\nОбновление таблицы лидеров...")
from game_app.views import GameSessionViewSet

# Симулируем обновление лидерборда
Leaderboard.objects.update_or_create(
    user=user1,
    game_session=session1,
    defaults={
        'score': session1.score,
        'rank': 2,
        'date_achieved': timezone.now(),
        'difficulty': session1.difficulty,
    }
)

Leaderboard.objects.update_or_create(
    user=user2,
    game_session=session2,
    defaults={
        'score': session2.score,
        'rank': 1,
        'date_achieved': timezone.now(),
        'difficulty': session2.difficulty,
    }
)

print("Тестовые данные созданы успешно!")
print(f"\nТестовые пользователи:")
print(f"  - {user1.username} / testpass123")
print(f"  - {user2.username} / testpass123")

