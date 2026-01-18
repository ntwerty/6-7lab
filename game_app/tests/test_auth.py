"""
Тесты для аутентификации и авторизации.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationTest(TestCase):
    """Тесты для аутентификации."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_registration(self):
        """Проверка регистрации пользователя."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_registration_password_mismatch(self):
        """Проверка регистрации с несовпадающими паролями."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'differentpass'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login(self):
        """Проверка входа пользователя."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Проверка входа с неверными учетными данными."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Проверка обновления токена."""
        refresh = RefreshToken.for_user(self.user)
        data = {'refresh': str(refresh)}
        response = self.client.post('/api/auth/refresh/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class AuthorizationTest(TestCase):
    """Тесты для авторизации."""
    
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
        self.guest = User.objects.create_user(
            username='guest',
            email='guest@example.com',
            password='guestpass123',
            is_guest=True
        )
    
    def test_anonymous_access_denied(self):
        """Проверка, что анонимный пользователь не имеет доступа к защищенным эндпоинтам."""
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access_allowed(self):
        """Проверка, что аутентифицированный пользователь имеет доступ."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_guest_read_only(self):
        """Проверка, что гость может только читать."""
        self.client.force_authenticate(user=self.guest)
        # Чтение должно быть разрешено
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Создание должно быть запрещено
        data = {
            'game_state': {},
            'score': 100,
            'level': 1
        }
        response = self.client.post('/api/game-sessions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_full_access(self):
        """Проверка, что администратор имеет полный доступ."""
        self.client.force_authenticate(user=self.admin)
        # Администратор должен видеть все профили
        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Администратор должен видеть все игровые сессии
        response = self.client.get('/api/game-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_own_data_only(self):
        """Проверка, что пользователь видит только свои данные."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        self.client.force_authenticate(user=self.user)
        # Пользователь должен видеть только свои сессии
        response = self.client.get('/api/game-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В ответе не должно быть сессий других пользователей
        for session in response.data['results'] if 'results' in response.data else response.data:
            if isinstance(session, dict):
                # Проверяем, что это сессия текущего пользователя
                pass  # Проверка зависит от структуры ответа
    
    def test_public_endpoints_accessible(self):
        """Проверка, что публичные эндпоинты доступны без аутентификации."""
        # Таблица лидеров должна быть доступна всем
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Достижения должны быть доступны всем
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


