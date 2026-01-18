"""
Тесты для сериализаторов (форм).
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from game_app.serializers import (
    RegisterSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    GameSessionSerializer, GameSessionCreateSerializer,
    LeaderboardSerializer, AchievementSerializer, UserAchievementSerializer,
    FriendSerializer, FriendCreateSerializer, ChallengeSerializer,
    ChallengeCreateSerializer
)
from game_app.models import (
    UserProfile, GameSession, Leaderboard, Achievement,
    UserAchievement, Friend, Challenge
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class RegisterSerializerTest(TestCase):
    """Тесты для сериализатора регистрации."""
    
    def test_valid_registration(self):
        """Проверка валидной регистрации."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_password_mismatch(self):
        """Проверка несовпадения паролей."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'differentpass'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_weak_password(self):
        """Проверка слабого пароля."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123',
            'password2': '123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_missing_fields(self):
        """Проверка отсутствующих полей."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_email_validation(self):
        """Проверка валидации email."""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class UserProfileSerializerTest(TestCase):
    """Тесты для сериализатора профиля пользователя."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
    
    def test_serialize_profile(self):
        """Проверка сериализации профиля."""
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['total_score'], 0)
        self.assertEqual(data['games_played'], 0)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_read_only_fields(self):
        """Проверка, что read_only поля не могут быть изменены."""
        data = {
            'total_score': 9999,
            'games_played': 9999
        }
        serializer = UserProfileSerializer(self.profile, data=data, partial=True)
        # Сериализатор должен игнорировать read_only поля
        serializer.is_valid()
        # Но при сохранении они не должны измениться
        if serializer.is_valid():
            serializer.save()
            self.profile.refresh_from_db()
            self.assertNotEqual(self.profile.total_score, 9999)


class UserProfileUpdateSerializerTest(TestCase):
    """Тесты для сериализатора обновления профиля."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
    
    def test_update_bio(self):
        """Проверка обновления bio."""
        data = {'bio': 'New bio text'}
        serializer = UserProfileUpdateSerializer(self.profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'New bio text')
    
    def test_update_date_of_birth(self):
        """Проверка обновления date_of_birth."""
        from datetime import date
        data = {'date_of_birth': date(1990, 1, 1)}
        serializer = UserProfileUpdateSerializer(self.profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.date_of_birth, date(1990, 1, 1))
    
    def test_cannot_update_read_only_fields(self):
        """Проверка, что нельзя обновить read_only поля."""
        data = {'total_score': 9999}
        serializer = UserProfileUpdateSerializer(self.profile, data=data, partial=True)
        # total_score не входит в fields сериализатора
        serializer.is_valid()
        if serializer.is_valid():
            serializer.save()
            self.profile.refresh_from_db()
            self.assertNotEqual(self.profile.total_score, 9999)


class GameSessionSerializerTest(TestCase):
    """Тесты для сериализатора игровой сессии."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = GameSession.objects.create(
            user=self.user,
            game_state={'ball': {'x': 400, 'y': 300}},
            score=1000,
            level=2,
            difficulty='medium'
        )
    
    def test_serialize_session(self):
        """Проверка сериализации сессии."""
        serializer = GameSessionSerializer(self.session)
        data = serializer.data
        self.assertEqual(data['score'], 1000)
        self.assertEqual(data['level'], 2)
        self.assertEqual(data['difficulty'], 'medium')
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_user_read_only(self):
        """Проверка, что user является read_only."""
        data = {'user': 999}
        serializer = GameSessionSerializer(self.session, data=data, partial=True)
        serializer.is_valid()
        # user не должен измениться
        if serializer.is_valid():
            serializer.save()
            self.session.refresh_from_db()
            self.assertEqual(self.session.user, self.user)


class GameSessionCreateSerializerTest(TestCase):
    """Тесты для сериализатора создания игровой сессии."""
    
    def test_valid_create_data(self):
        """Проверка валидных данных для создания."""
        data = {
            'game_state': {'ball': {'x': 400, 'y': 300}},
            'score': 1000,
            'level': 2,
            'time_played': 120,
            'is_completed': False,
            'difficulty': 'medium'
        }
        serializer = GameSessionCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_score(self):
        """Проверка невалидного score."""
        data = {
            'score': -1,
            'level': 1
        }
        serializer = GameSessionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_level(self):
        """Проверка невалидного level."""
        data = {
            'score': 100,
            'level': 0
        }
        serializer = GameSessionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_difficulty(self):
        """Проверка невалидной difficulty."""
        data = {
            'score': 100,
            'level': 1,
            'difficulty': 'invalid'
        }
        serializer = GameSessionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class FriendCreateSerializerTest(TestCase):
    """Тесты для сериализатора создания запроса в друзья."""
    
    def test_valid_friend_request(self):
        """Проверка валидного запроса в друзья."""
        data = {'to_username': 'friend'}
        serializer = FriendCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_status_read_only(self):
        """Проверка, что status является read_only."""
        data = {'to_username': 'friend', 'status': 'accepted'}
        serializer = FriendCreateSerializer(data=data)
        serializer.is_valid()
        # status не должен быть установлен через сериализатор
        if serializer.is_valid():
            validated_data = serializer.validated_data
            self.assertNotIn('status', validated_data)


class ChallengeCreateSerializerTest(TestCase):
    """Тесты для сериализатора создания вызова."""
    
    def test_valid_challenge(self):
        """Проверка валидного вызова."""
        data = {
            'challenged_username': 'opponent',
            'target_score': 1000,
            'expires_at': (timezone.now() + timedelta(days=7)).isoformat()
        }
        serializer = ChallengeCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_target_score(self):
        """Проверка невалидного target_score."""
        data = {
            'challenged_username': 'opponent',
            'target_score': 0
        }
        serializer = ChallengeCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_missing_challenged_username(self):
        """Проверка отсутствующего challenged_username."""
        data = {'target_score': 1000}
        serializer = ChallengeCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())


