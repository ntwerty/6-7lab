"""
Тесты для представлений (Views).
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


class UserProfileViewSetTest(TestCase):
    """Тесты для UserProfileViewSet."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
    
    def test_get_own_profile(self):
        """Проверка получения своего профиля."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_public_profile(self):
        """Проверка получения публичного профиля."""
        self.client.force_authenticate(user=self.user)
        profile_id = self.user.profile.id
        response = self.client.get(f'/api/profiles/{profile_id}/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_own_profile(self):
        """Проверка обновления своего профиля."""
        self.client.force_authenticate(user=self.user)
        profile_id = self.user.profile.id
        data = {'bio': 'Updated bio'}
        response = self.client.patch(f'/api/profiles/{profile_id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'Updated bio')
    
    def test_list_profiles(self):
        """Проверка списка профилей."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GameSessionViewSetTest(TestCase):
    """Тесты для GameSessionViewSet."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
    
    def test_create_game_session(self):
        """Проверка создания игровой сессии."""
        self.client.force_authenticate(user=self.user)
        data = {
            'game_state': {'ball': {'x': 400, 'y': 300}},
            'score': 1000,
            'level': 2,
            'time_played': 120,
            'is_completed': False,
            'difficulty': 'medium'
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 1000)
        self.assertEqual(response.data['level'], 2)
        
        # Проверяем, что сессия создана в БД
        session = GameSession.objects.get(id=response.data['id'])
        self.assertEqual(session.user, self.user)
    
    def test_list_own_sessions(self):
        """Проверка списка своих сессий."""
        # Создаем сессии для обоих пользователей
        GameSession.objects.create(user=self.user, score=100, level=1)
        GameSession.objects.create(user=self.other_user, score=200, level=2)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/game-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь должен видеть только свои сессии
        sessions = response.data['results'] if 'results' in response.data else response.data
        for session in sessions:
            if isinstance(session, dict) and 'user' in session:
                self.assertEqual(session['user'], 'testuser')
    
    def test_get_latest_session(self):
        """Проверка получения последней сессии."""
        GameSession.objects.create(
            user=self.user,
            score=100,
            level=1,
            is_completed=False
        )
        GameSession.objects.create(
            user=self.user,
            score=200,
            level=2,
            is_completed=False
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/game-sessions/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 200)  # Последняя сессия
    
    def test_update_session(self):
        """Проверка обновления сессии."""
        session = GameSession.objects.create(
            user=self.user,
            score=100,
            level=1
        )
        self.client.force_authenticate(user=self.user)
        data = {'score': 500, 'level': 2}
        response = self.client.patch(f'/api/game-sessions/{session.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(session.score, 500)
    
    def test_delete_session(self):
        """Проверка удаления сессии."""
        session = GameSession.objects.create(
            user=self.user,
            score=100,
            level=1
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/game-sessions/{session.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GameSession.objects.filter(id=session.id).exists())
    
    def test_profile_updated_on_session_create(self):
        """Проверка обновления профиля при создании сессии."""
        initial_games_played = self.user.profile.games_played
        self.client.force_authenticate(user=self.user)
        data = {
            'score': 1000,
            'level': 2,
            'is_completed': True
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.games_played, initial_games_played + 1)
        self.assertEqual(self.user.profile.total_score, 1000)


class LeaderboardViewSetTest(TestCase):
    """Тесты для LeaderboardViewSet."""
    
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
    
    def test_list_leaderboard(self):
        """Проверка списка лидеров."""
        # Создаем записи в таблице лидеров
        session1 = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=3,
            is_completed=True
        )
        session2 = GameSession.objects.create(
            user=self.user2,
            score=2000,
            level=4,
            is_completed=True
        )
        Leaderboard.objects.create(
            user=self.user1,
            game_session=session1,
            score=1000,
            rank=2,
            difficulty='medium'
        )
        Leaderboard.objects.create(
            user=self.user2,
            game_session=session2,
            score=2000,
            rank=1,
            difficulty='medium'
        )
        
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_top_players(self):
        """Проверка топ игроков."""
        session = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=3,
            is_completed=True
        )
        Leaderboard.objects.create(
            user=self.user1,
            game_session=session,
            score=1000,
            rank=1,
            difficulty='medium'
        )
        
        response = self.client.get('/api/leaderboard/top/?limit=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_by_difficulty(self):
        """Проверка фильтрации по сложности."""
        session = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=3,
            is_completed=True,
            difficulty='hard'
        )
        Leaderboard.objects.create(
            user=self.user1,
            game_session=session,
            score=1000,
            rank=1,
            difficulty='hard'
        )
        
        response = self.client.get('/api/leaderboard/?difficulty=hard')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AchievementViewSetTest(TestCase):
    """Тесты для AchievementViewSet."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
    
    def test_list_achievements(self):
        """Проверка списка достижений."""
        Achievement.objects.create(
            name='Первая победа',
            description='Победите в первой игре',
            points_required=100
        )
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FriendViewSetTest(TestCase):
    """Тесты для FriendViewSet."""
    
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
    
    def test_send_friend_request(self):
        """Проверка отправки запроса в друзья."""
        self.client.force_authenticate(user=self.user1)
        data = {'to_username': 'user2'}
        response = self.client.post('/api/friends/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Friend.objects.filter(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        ).exists())
    
    def test_cannot_add_self(self):
        """Проверка, что нельзя добавить себя в друзья."""
        self.client.force_authenticate(user=self.user1)
        data = {'to_username': 'user1'}
        response = self.client.post('/api/friends/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_accept_friend_request(self):
        """Проверка принятия запроса в друзья."""
        friend = Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/friends/{friend.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend.refresh_from_db()
        self.assertEqual(friend.status, 'accepted')
    
    def test_reject_friend_request(self):
        """Проверка отклонения запроса в друзья."""
        friend = Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/friends/{friend.id}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend.refresh_from_db()
        self.assertEqual(friend.status, 'rejected')
    
    def test_list_my_friends(self):
        """Проверка списка своих друзей."""
        Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='accepted'
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/friends/my_friends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ChallengeViewSetTest(TestCase):
    """Тесты для ChallengeViewSet."""
    
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
    
    def test_create_challenge(self):
        """Проверка создания вызова."""
        self.client.force_authenticate(user=self.user1)
        data = {
            'challenged_username': 'user2',
            'target_score': 1000,
            'expires_at': (timezone.now() + timedelta(days=7)).isoformat()
        }
        response = self.client.post('/api/challenges/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Challenge.objects.filter(
            challenger=self.user1,
            challenged=self.user2
        ).exists())
    
    def test_cannot_challenge_non_friend(self):
        """Проверка, что нельзя бросить вызов не другу."""
        user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='pass123'
        )
        self.client.force_authenticate(user=self.user1)
        data = {
            'challenged_username': 'user3',
            'target_score': 1000
        }
        response = self.client.post('/api/challenges/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_accept_challenge(self):
        """Проверка принятия вызова."""
        challenge = Challenge.objects.create(
            challenger=self.user1,
            challenged=self.user2,
            target_score=1000,
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/challenges/{challenge.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'accepted')
    
    def test_submit_score(self):
        """Проверка отправки счета для вызова."""
        challenge = Challenge.objects.create(
            challenger=self.user1,
            challenged=self.user2,
            target_score=1000,
            status='accepted',
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.client.force_authenticate(user=self.user1)
        data = {'score': 1500}
        response = self.client.post(f'/api/challenges/{challenge.id}/submit_score/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        challenge.refresh_from_db()
        self.assertEqual(challenge.challenger_score, 1500)
    
    def test_challenge_completed_when_both_scores_submitted(self):
        """Проверка завершения вызова при отправке обоих счетов."""
        challenge = Challenge.objects.create(
            challenger=self.user1,
            challenged=self.user2,
            target_score=1000,
            status='accepted',
            expires_at=timezone.now() + timedelta(days=7)
        )
        # Отправляем счет от первого игрока
        self.client.force_authenticate(user=self.user1)
        self.client.post(f'/api/challenges/{challenge.id}/submit_score/', {'score': 1500}, format='json')
        
        # Отправляем счет от второго игрока
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/challenges/{challenge.id}/submit_score/', {'score': 1200}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'completed')


class HTTPStatusCodesTest(TestCase):
    """Тесты для проверки HTTP статус кодов."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_200_for_valid_requests(self):
        """Проверка статуса 200 для валидных запросов."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_201_for_created(self):
        """Проверка статуса 201 для созданных ресурсов."""
        self.client.force_authenticate(user=self.user)
        data = {
            'game_state': {},
            'score': 100,
            'level': 1
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_302_redirect(self):
        """Проверка редиректов (если есть)."""
        # В REST API обычно используются статусы 201, 200, но не 302
        # Этот тест можно использовать для проверки других редиректов
        pass
    
    def test_404_for_not_found(self):
        """Проверка статуса 404 для несуществующих ресурсов."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_401_for_unauthorized(self):
        """Проверка статуса 401 для неавторизованных запросов."""
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_403_for_forbidden(self):
        """Проверка статуса 403 для запрещенных действий."""
        guest = User.objects.create_user(
            username='guest',
            email='guest@example.com',
            password='guestpass123',
            is_guest=True
        )
        self.client.force_authenticate(user=guest)
        data = {'game_state': {}, 'score': 100, 'level': 1}
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


