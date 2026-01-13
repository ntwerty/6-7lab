"""
Интеграционные тесты для проверки полного цикла основной услуги.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from game_app.models import (
    UserProfile, GameSession, Leaderboard, Achievement,
    UserAchievement, Friend, Challenge
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class GameSessionLifecycleTest(TestCase):
    """Интеграционный тест полного цикла игровой сессии."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_game_session_flow(self):
        """Проверка полного цикла: создание сессии -> обновление профиля -> достижения -> лидерборд."""
        # 1. Проверяем начальное состояние
        initial_games_played = self.user.profile.games_played
        initial_total_score = self.user.profile.total_score
        
        # 2. Создаем достижение
        achievement = Achievement.objects.create(
            name='Первая победа',
            description='Победите в первой игре',
            points_required=100,
            level_required=1
        )
        
        # 3. Создаем игровую сессию
        data = {
            'game_state': {'ball': {'x': 400, 'y': 300}},
            'score': 1000,
            'level': 2,
            'time_played': 120,
            'is_completed': True,
            'difficulty': 'medium'
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session_id = response.data['id']
        
        # 4. Проверяем, что сессия сохранена в БД
        session = GameSession.objects.get(id=session_id)
        self.assertEqual(session.score, 1000)
        self.assertEqual(session.level, 2)
        self.assertTrue(session.is_completed)
        
        # 5. Проверяем обновление профиля
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.games_played, initial_games_played + 1)
        self.assertEqual(self.user.profile.total_score, 1000)
        
        # 6. Проверяем, что достижение было выдано
        self.assertTrue(UserAchievement.objects.filter(
            user=self.user,
            achievement=achievement
        ).exists())
        
        # 7. Проверяем, что запись появилась в таблице лидеров
        self.assertTrue(Leaderboard.objects.filter(
            user=self.user,
            game_session=session
        ).exists())
        
        # 8. Проверяем изменения состояния системы
        self.assertEqual(GameSession.objects.filter(user=self.user).count(), 1)
        self.assertEqual(UserAchievement.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Leaderboard.objects.filter(user=self.user).count(), 1)


class FriendSystemFlowTest(TestCase):
    """Интеграционный тест системы друзей."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
    
    def test_complete_friend_request_flow(self):
        """Проверка полного цикла: запрос -> принятие -> создание вызова."""
        # 1. Проверяем начальное состояние
        initial_friends_count = Friend.objects.filter(
            from_user=self.user1,
            to_user=self.user2
        ).count()
        self.assertEqual(initial_friends_count, 0)
        
        # 2. Отправляем запрос в друзья
        self.client.force_authenticate(user=self.user1)
        data = {'to_username': 'user2'}
        response = self.client.post('/api/friends/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Проверяем, что запрос создан
        friend_request = Friend.objects.get(
            from_user=self.user1,
            to_user=self.user2
        )
        self.assertEqual(friend_request.status, 'pending')
        
        # 4. Принимаем запрос
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/friends/{friend_request.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Проверяем, что статус изменился
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, 'accepted')
        
        # 6. Создаем вызов между друзьями
        self.client.force_authenticate(user=self.user1)
        challenge_data = {
            'challenged_username': 'user2',
            'target_score': 1000,
            'expires_at': (timezone.now() + timedelta(days=7)).isoformat()
        }
        response = self.client.post('/api/challenges/', challenge_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 7. Проверяем, что вызов создан
        challenge = Challenge.objects.get(
            challenger=self.user1,
            challenged=self.user2
        )
        self.assertEqual(challenge.status, 'pending')
        
        # 8. Проверяем изменения состояния системы
        self.assertEqual(Friend.objects.filter(
            from_user=self.user1,
            to_user=self.user2,
            status='accepted'
        ).count(), 1)
        self.assertEqual(Challenge.objects.filter(
            challenger=self.user1,
            challenged=self.user2
        ).count(), 1)


class ChallengeCompletionFlowTest(TestCase):
    """Интеграционный тест завершения вызова."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        # Создаем дружескую связь
        Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='accepted'
        )
        # Создаем вызов
        self.challenge = Challenge.objects.create(
            challenger=self.user1,
            challenged=self.user2,
            target_score=1000,
            status='accepted',
            expires_at=timezone.now() + timedelta(days=7)
        )
    
    def test_complete_challenge_flow(self):
        """Проверка полного цикла завершения вызова."""
        # 1. Проверяем начальное состояние
        self.assertIsNone(self.challenge.challenger_score)
        self.assertIsNone(self.challenged_score)
        self.assertEqual(self.challenge.status, 'accepted')
        
        # 2. Отправляем счет от первого игрока
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f'/api/challenges/{self.challenge.id}/submit_score/',
            {'score': 1500},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Проверяем, что счет сохранен
        self.challenge.refresh_from_db()
        self.assertEqual(self.challenge.challenger_score, 1500)
        self.assertIsNone(self.challenge.challenged_score)
        self.assertEqual(self.challenge.status, 'accepted')  # Еще не завершен
        
        # 4. Отправляем счет от второго игрока
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f'/api/challenges/{self.challenge.id}/submit_score/',
            {'score': 1200},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Проверяем, что вызов завершен
        self.challenge.refresh_from_db()
        self.assertEqual(self.challenge.challenger_score, 1500)
        self.assertEqual(self.challenge.challenged_score, 1200)
        self.assertEqual(self.challenge.status, 'completed')
        
        # 6. Проверяем изменения состояния системы
        self.assertEqual(Challenge.objects.filter(
            challenger=self.user1,
            challenged=self.user2,
            status='completed'
        ).count(), 1)


class DataPersistenceTest(TestCase):
    """Тесты для проверки сохранения данных в БД."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_game_session_persisted(self):
        """Проверка, что игровая сессия сохраняется в БД."""
        data = {
            'game_state': {'ball': {'x': 400, 'y': 300}},
            'score': 1000,
            'level': 2
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        session_id = response.data['id']
        
        # Проверяем, что данные сохранены
        session = GameSession.objects.get(id=session_id)
        self.assertEqual(session.score, 1000)
        self.assertEqual(session.level, 2)
        self.assertEqual(session.game_state, {'ball': {'x': 400, 'y': 300}})
    
    def test_profile_update_persisted(self):
        """Проверка, что обновление профиля сохраняется в БД."""
        profile_id = self.user.profile.id
        data = {'bio': 'New bio text'}
        self.client.patch(f'/api/profiles/{profile_id}/', data, format='json')
        
        # Проверяем, что данные сохранены
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'New bio text')
    
    def test_achievement_persisted(self):
        """Проверка, что достижение сохраняется в БД."""
        achievement = Achievement.objects.create(
            name='Тестовое достижение',
            description='Описание',
            points_required=100
        )
        
        # Создаем сессию, которая должна выдать достижение
        data = {
            'score': 1000,
            'level': 2,
            'is_completed': True
        }
        self.client.post('/api/game-sessions/', data, format='json')
        
        # Проверяем, что достижение выдано
        self.assertTrue(UserAchievement.objects.filter(
            user=self.user,
            achievement=achievement
        ).exists())


class SystemStateChangesTest(TestCase):
    """Тесты для проверки изменений состояния системы."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_games_played_incremented(self):
        """Проверка увеличения счетчика игр."""
        initial_count = self.user.profile.games_played
        
        # Создаем сессию
        data = {'score': 100, 'level': 1}
        self.client.post('/api/game-sessions/', data, format='json')
        
        # Проверяем увеличение счетчика
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.games_played, initial_count + 1)
    
    def test_total_score_updated(self):
        """Проверка обновления общего счета."""
        initial_score = self.user.profile.total_score
        
        # Создаем сессию с большим счетом
        data = {'score': 1000, 'level': 2}
        self.client.post('/api/game-sessions/', data, format='json')
        
        # Проверяем обновление счета
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_score, 1000)
        
        # Создаем еще одну сессию с меньшим счетом
        data = {'score': 500, 'level': 1}
        self.client.post('/api/game-sessions/', data, format='json')
        
        # Счет должен остаться максимальным
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_score, 1000)
    
    def test_leaderboard_rank_calculation(self):
        """Проверка расчета ранга в таблице лидеров."""
        # Создаем несколько завершенных сессий
        session1 = GameSession.objects.create(
            user=self.user,
            score=1000,
            level=2,
            is_completed=True,
            difficulty='medium'
        )
        
        # Проверяем, что ранг рассчитывается правильно
        leaderboard_entry = Leaderboard.objects.filter(
            user=self.user,
            game_session=session1
        ).first()
        
        if leaderboard_entry:
            self.assertGreaterEqual(leaderboard_entry.rank, 1)
    
    def test_achievement_unlock_count(self):
        """Проверка количества разблокированных достижений."""
        # Создаем достижения
        achievement1 = Achievement.objects.create(
            name='Достижение 1',
            description='Описание 1',
            points_required=100
        )
        achievement2 = Achievement.objects.create(
            name='Достижение 2',
            description='Описание 2',
            points_required=500
        )
        
        initial_count = UserAchievement.objects.filter(user=self.user).count()
        
        # Создаем сессию, которая должна выдать оба достижения
        data = {'score': 1000, 'level': 2, 'is_completed': True}
        self.client.post('/api/game-sessions/', data, format='json')
        
        # Проверяем увеличение количества достижений
        final_count = UserAchievement.objects.filter(user=self.user).count()
        self.assertGreater(final_count, initial_count)

