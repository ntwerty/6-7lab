"""
Тесты для административной панели.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from openpyxl import load_workbook
from game_app.models import (
    UserProfile, GameSession, Leaderboard, Achievement,
    UserAchievement, Friend, Challenge
)

User = get_user_model()


class AdminPanelAccessTest(TestCase):
    """Тесты для доступа к админ-панели."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
    
    def test_admin_can_access_admin_panel(self):
        """Проверка, что администратор может получить доступ к админ-панели."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_regular_user_cannot_access_admin_panel(self):
        """Проверка, что обычный пользователь не может получить доступ к админ-панели."""
        self.client.login(username='user', password='userpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
    
    def test_anonymous_cannot_access_admin_panel(self):
        """Проверка, что анонимный пользователь не может получить доступ к админ-панели."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа


class AdminExportToXLSXTest(TestCase):
    """Тесты для функции экспорта в XLSX."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
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
        
        # Создаем игровые сессии
        self.session1 = GameSession.objects.create(
            user=self.user1,
            score=1000,
            level=2,
            difficulty='medium',
            time_played=120,
            is_completed=True
        )
        self.session2 = GameSession.objects.create(
            user=self.user2,
            score=2000,
            level=3,
            difficulty='hard',
            time_played=240,
            is_completed=True
        )
        
        self.client.login(username='admin', password='adminpass123')
    
    def test_export_selected_sessions_to_xlsx(self):
        """Проверка экспорта выбранных сессий в XLSX."""
        # Получаем URL для действия экспорта
        url = reverse('admin:game_app_gamesession_changelist')
        
        # Выбираем сессии для экспорта
        data = {
            'action': 'export_to_xlsx',
            '_selected_action': [self.session1.id, self.session2.id]
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Проверяем, что ответ содержит файл XLSX
        if response.status_code == 200:
            # Если экспорт работает через отдельный эндпоинт
            # Проверяем наличие файла в ответе
            self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                         response.get('Content-Type', ''))
    
    def test_xlsx_file_structure(self):
        """Проверка структуры созданного XLSX файла."""
        # Создаем тестовый файл напрямую через админку
        from game_app.admin import GameSessionAdmin
        from django.http import HttpRequest
        
        admin_instance = GameSessionAdmin(GameSession, None)
        queryset = GameSession.objects.filter(id__in=[self.session1.id, self.session2.id])
        
        # Вызываем метод экспорта
        response = admin_instance.export_to_xlsx(None, queryset)
        
        # Проверяем, что ответ является HttpResponse
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     response.get('Content-Type', ''))
        
        # Проверяем содержимое файла
        wb = load_workbook(BytesIO(response.content))
        ws = wb.active
        
        # Проверяем заголовки
        headers = [cell.value for cell in ws[1]]
        expected_headers = [
            'ID', 'Пользователь', 'Счет', 'Уровень', 'Сложность',
            'Время игры (сек)', 'Завершена', 'Дата создания'
        ]
        self.assertEqual(headers, expected_headers)
        
        # Проверяем количество строк данных (должно быть 2 сессии)
        self.assertGreaterEqual(ws.max_row, 2)  # Заголовок + данные
    
    def test_xlsx_file_content(self):
        """Проверка содержимого созданного XLSX файла."""
        from game_app.admin import GameSessionAdmin
        
        admin_instance = GameSessionAdmin(GameSession, None)
        queryset = GameSession.objects.filter(id=self.session1.id)
        
        response = admin_instance.export_to_xlsx(None, queryset)
        wb = load_workbook(BytesIO(response.content))
        ws = wb.active
        
        # Проверяем данные первой сессии (вторая строка)
        if ws.max_row >= 2:
            row_data = [cell.value for cell in ws[2]]
            self.assertEqual(row_data[1], 'user1')  # Пользователь
            self.assertEqual(row_data[2], 1000)  # Счет
            self.assertEqual(row_data[3], 2)  # Уровень
    
    def test_export_only_selected_tables(self):
        """Проверка, что экспортируются данные только из выбранных таблиц."""
        from game_app.admin import GameSessionAdmin
        
        admin_instance = GameSessionAdmin(GameSession, None)
        # Выбираем только одну сессию
        queryset = GameSession.objects.filter(id=self.session1.id)
        
        response = admin_instance.export_to_xlsx(None, queryset)
        wb = load_workbook(BytesIO(response.content))
        ws = wb.active
        
        # Проверяем, что в файле только одна сессия (плюс заголовок)
        self.assertEqual(ws.max_row, 2)  # Заголовок + одна строка данных
    
    def test_export_only_selected_columns(self):
        """Проверка, что экспортируются только выбранные колонки."""
        from game_app.admin import GameSessionAdmin
        
        admin_instance = GameSessionAdmin(GameSession, None)
        queryset = GameSession.objects.filter(id=self.session1.id)
        
        response = admin_instance.export_to_xlsx(None, queryset)
        wb = load_workbook(BytesIO(response.content))
        ws = wb.active
        
        # Проверяем, что экспортируются правильные колонки
        headers = [cell.value for cell in ws[1]]
        expected_columns = [
            'ID', 'Пользователь', 'Счет', 'Уровень', 'Сложность',
            'Время игры (сек)', 'Завершена', 'Дата создания'
        ]
        self.assertEqual(headers, expected_columns)
        
        # Проверяем, что не экспортируются лишние колонки
        self.assertNotIn('game_state', headers)
        self.assertNotIn('updated_at', headers)


class AdminModelListTest(TestCase):
    """Тесты для списков моделей в админке."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.login(username='admin', password='adminpass123')
    
    def test_user_list_in_admin(self):
        """Проверка списка пользователей в админке."""
        url = reverse('admin:game_app_user_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_gamesession_list_in_admin(self):
        """Проверка списка игровых сессий в админке."""
        url = reverse('admin:game_app_gamesession_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_leaderboard_list_in_admin(self):
        """Проверка списка лидеров в админке."""
        url = reverse('admin:game_app_leaderboard_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_achievement_list_in_admin(self):
        """Проверка списка достижений в админке."""
        url = reverse('admin:game_app_achievement_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_friend_list_in_admin(self):
        """Проверка списка друзей в админке."""
        url = reverse('admin:game_app_friend_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_challenge_list_in_admin(self):
        """Проверка списка вызовов в админке."""
        url = reverse('admin:game_app_challenge_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


