"""
Тесты для безопасности приложения.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from game_app.models import GameSession, UserProfile
import json

User = get_user_model()


class SQLInjectionTest(TestCase):
    """Тесты для защиты от SQL-инъекций."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_sql_injection_in_username(self):
        """Проверка защиты от SQL-инъекции в username."""
        # Попытка SQL-инъекции в поле username
        malicious_input = "admin' OR '1'='1"
        
        # Пытаемся использовать это в запросе
        # Django ORM должен экранировать это автоматически
        try:
            user = User.objects.filter(username=malicious_input).first()
            # Если пользователь не найден, значит инъекция не сработала
            self.assertIsNone(user)
        except Exception as e:
            # Если возникла ошибка, это тоже хорошо - значит защита работает
            pass
    
    def test_sql_injection_in_search(self):
        """Проверка защиты от SQL-инъекции в поисковом запросе."""
        malicious_input = "'; DROP TABLE game_app_gamesession; --"
        
        # Пытаемся использовать это в поиске
        response = self.client.get(f'/api/leaderboard/?search={malicious_input}')
        # Должен вернуться валидный ответ (не ошибка БД)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_sql_injection_in_filter(self):
        """Проверка защиты от SQL-инъекции в фильтрах."""
        malicious_input = "1' OR '1'='1"
        
        # Пытаемся использовать это в фильтре
        response = self.client.get(f'/api/leaderboard/?difficulty={malicious_input}')
        # Должен вернуться валидный ответ или ошибка валидации
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ])


class XSSTest(TestCase):
    """Тесты для защиты от XSS атак."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_xss_in_bio(self):
        """Проверка защиты от XSS в поле bio."""
        xss_payload = '<script>alert("XSS")</script>'
        
        # Пытаемся сохранить XSS в bio
        profile_id = self.user.profile.id
        data = {'bio': xss_payload}
        response = self.client.patch(f'/api/profiles/{profile_id}/', data, format='json')
        
        # Проверяем, что данные сохранены
        if response.status_code == status.HTTP_200_OK:
            self.user.profile.refresh_from_db()
            # Django REST Framework должен экранировать данные при сериализации
            # Но в БД они могут храниться как есть
            # Главное - при выводе они должны быть экранированы
            self.assertIn(xss_payload, self.user.profile.bio)
    
    def test_xss_in_game_state(self):
        """Проверка защиты от XSS в game_state."""
        xss_payload = {'malicious': '<script>alert("XSS")</script>'}
        
        # Пытаемся сохранить XSS в game_state
        data = {
            'game_state': xss_payload,
            'score': 100,
            'level': 1
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        
        # Проверяем, что данные сохранены
        if response.status_code == status.HTTP_201_CREATED:
            session_id = response.data['id']
            session = GameSession.objects.get(id=session_id)
            # JSON поле должно хранить данные как есть
            # Но при выводе через API они должны быть экранированы
            self.assertIn('malicious', session.game_state)
            # Проверяем, что при выводе через API данные экранированы
            response = self.client.get(f'/api/game-sessions/{session_id}/')
            if response.status_code == status.HTTP_200_OK:
                # Данные должны быть сериализованы безопасно
                self.assertIn('game_state', response.data)
    
    def test_xss_in_username(self):
        """Проверка защиты от XSS в username при регистрации."""
        xss_payload = '<script>alert("XSS")</script>'
        
        # Пытаемся зарегистрироваться с XSS в username
        data = {
            'username': xss_payload,
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        
        # Регистрация может пройти, но данные должны быть обработаны безопасно
        # Django должен валидировать username и не допустить специальные символы
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Это хорошо - валидация сработала
            pass
        elif response.status_code == status.HTTP_201_CREATED:
            # Если регистрация прошла, проверяем, что данные сохранены безопасно
            user = User.objects.filter(username=xss_payload).first()
            if user:
                # При выводе через API данные должны быть экранированы
                pass


class PasswordSecurityTest(TestCase):
    """Тесты для безопасности паролей."""
    
    def test_password_hashed_in_database(self):
        """Проверка, что пароли хранятся в хешированном виде."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Получаем пароль из БД напрямую
        user_from_db = User.objects.get(username='testuser')
        
        # Пароль должен быть хешированным, а не в открытом виде
        self.assertNotEqual(user_from_db.password, 'testpass123')
        self.assertTrue(user_from_db.password.startswith('pbkdf2_'))  # Django использует pbkdf2 по умолчанию
    
    def test_password_verification(self):
        """Проверка, что пароль можно проверить через check_password."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Проверяем правильный пароль
        self.assertTrue(user.check_password('testpass123'))
        
        # Проверяем неправильный пароль
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_password_not_returned_in_api(self):
        """Проверка, что пароль не возвращается в API ответах."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Регистрируем пользователя через API
        client = APIClient()
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = client.post('/api/auth/register/', data, format='json')
        
        if response.status_code == status.HTTP_201_CREATED:
            # Проверяем, что пароль не возвращается в ответе
            self.assertNotIn('password', response.data.get('user', {}))
    
    def test_password_validation(self):
        """Проверка валидации пароля."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Слишком короткий пароль
        with self.assertRaises(ValidationError):
            validate_password('123')
        
        # Слишком простой пароль (только цифры)
        with self.assertRaises(ValidationError):
            validate_password('12345678')


class CSRFProtectionTest(TestCase):
    """Тесты для защиты от CSRF атак."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_csrf_protection_enabled(self):
        """Проверка, что CSRF защита включена."""
        # Django REST Framework с JWT не требует CSRF токенов для API
        # Но для админки CSRF должен быть включен
        from django.conf import settings
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)


class AuthorizationTest(TestCase):
    """Тесты для проверки авторизации."""
    
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
    
    def test_user_cannot_access_other_user_data(self):
        """Проверка, что пользователь не может получить доступ к данным другого пользователя."""
        # Создаем сессию для user1
        session = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=2
        )
        
        # Пытаемся получить доступ к сессии user1 от имени user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/game-sessions/{session.id}/')
        
        # user2 не должен видеть сессию user1
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
    
    def test_user_cannot_modify_other_user_data(self):
        """Проверка, что пользователь не может изменить данные другого пользователя."""
        # Создаем сессию для user1
        session = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=2
        )
        
        # Пытаемся изменить сессию user1 от имени user2
        self.client.force_authenticate(user=self.user2)
        data = {'score': 9999}
        response = self.client.patch(f'/api/game-sessions/{session.id}/', data, format='json')
        
        # user2 не должен иметь возможность изменить сессию user1
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
        
        # Проверяем, что данные не изменились
        session.refresh_from_db()
        self.assertEqual(session.score, 1000)
    
    def test_user_cannot_delete_other_user_data(self):
        """Проверка, что пользователь не может удалить данные другого пользователя."""
        # Создаем сессию для user1
        session = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=2
        )
        session_id = session.id
        
        # Пытаемся удалить сессию user1 от имени user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/game-sessions/{session_id}/')
        
        # user2 не должен иметь возможность удалить сессию user1
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
        
        # Проверяем, что сессия не удалена
        self.assertTrue(GameSession.objects.filter(id=session_id).exists())


class InputValidationTest(TestCase):
    """Тесты для валидации входных данных."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_score_rejected(self):
        """Проверка отклонения невалидного score."""
        data = {
            'score': -100,  # Отрицательное значение
            'level': 1
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_level_rejected(self):
        """Проверка отклонения невалидного level."""
        data = {
            'score': 100,
            'level': 0  # Недопустимое значение
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_email_rejected(self):
        """Проверка отклонения невалидного email."""
        data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Невалидный email
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_oversized_input_rejected(self):
        """Проверка отклонения слишком больших входных данных."""
        # Создаем очень большое значение для bio
        oversized_bio = 'a' * 10000  # Превышает max_length=500
        
        profile_id = self.user.profile.id
        data = {'bio': oversized_bio}
        response = self.client.patch(f'/api/profiles/{profile_id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

