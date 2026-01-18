"""
Тесты для моделей приложения.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from game_app.models import (
    UserProfile, GameSession, Leaderboard, Achievement,
    UserAchievement, Friend, Challenge, TimeStampedModel
)

User = get_user_model()


class TimeStampedModelTest(TestCase):
    """Тесты для абстрактной модели TimeStampedModel."""
    
    def test_created_at_auto_filled(self):
        """Проверка автоматического заполнения created_at."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile = UserProfile.objects.get(user=user)
        self.assertIsNotNone(profile.created_at)
        self.assertIsInstance(profile.created_at, timezone.datetime)
    
    def test_updated_at_auto_filled(self):
        """Проверка автоматического заполнения updated_at."""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        profile = UserProfile.objects.get(user=user)
        initial_updated_at = profile.updated_at
        
        # Обновляем профиль
        profile.bio = 'New bio'
        profile.save()
        
        # updated_at должен обновиться
        profile.refresh_from_db()
        self.assertGreater(profile.updated_at, initial_updated_at)


class UserModelTest(TestCase):
    """Тесты для модели User."""
    
    def test_create_user(self):
        """Проверка создания пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_guest)
        self.assertFalse(user.is_staff)
    
    def test_email_unique(self):
        """Проверка уникальности email."""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='testpass123'
        )
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='testpass123'
            )
    
    def test_is_guest_default(self):
        """Проверка значения по умолчанию для is_guest."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertFalse(user.is_guest)


class UserProfileModelTest(TestCase):
    """Тесты для модели UserProfile."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_created_automatically(self):
        """Проверка автоматического создания профиля."""
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
    
    def test_one_to_one_relationship(self):
        """Проверка связи OneToOne между User и UserProfile."""
        profile = self.user.profile
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user, self.user)
    
    def test_total_score_default(self):
        """Проверка значения по умолчанию для total_score."""
        profile = self.user.profile
        self.assertEqual(profile.total_score, 0)
    
    def test_total_score_min_value(self):
        """Проверка валидации минимального значения total_score."""
        profile = self.user.profile
        profile.total_score = -1
        with self.assertRaises(ValidationError):
            profile.full_clean()
    
    def test_games_played_default(self):
        """Проверка значения по умолчанию для games_played."""
        profile = self.user.profile
        self.assertEqual(profile.games_played, 0)
    
    def test_games_played_min_value(self):
        """Проверка валидации минимального значения games_played."""
        profile = self.user.profile
        profile.games_played = -1
        with self.assertRaises(ValidationError):
            profile.full_clean()
    
    def test_bio_max_length(self):
        """Проверка максимальной длины bio."""
        profile = self.user.profile
        profile.bio = 'a' * 501  # Превышает max_length=500
        with self.assertRaises(ValidationError):
            profile.full_clean()


class GameSessionModelTest(TestCase):
    """Тесты для модели GameSession."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_game_session(self):
        """Проверка создания игровой сессии."""
        session = GameSession.objects.create(
            user=self.user,
            game_state={'ball': {'x': 400, 'y': 300}},
            score=1000,
            level=2,
            time_played=120,
            is_completed=False,
            difficulty='medium'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.score, 1000)
        self.assertEqual(session.level, 2)
        self.assertEqual(session.difficulty, 'medium')
        self.assertFalse(session.is_completed)
    
    def test_foreign_key_relationship(self):
        """Проверка связи ForeignKey с User."""
        session = GameSession.objects.create(
            user=self.user,
            score=500,
            level=1
        )
        self.assertEqual(session.user, self.user)
        self.assertIn(session, self.user.game_sessions.all())
    
    def test_score_min_value(self):
        """Проверка валидации минимального значения score."""
        session = GameSession(user=self.user, score=-1, level=1)
        with self.assertRaises(ValidationError):
            session.full_clean()
    
    def test_level_min_value(self):
        """Проверка валидации минимального значения level."""
        session = GameSession(user=self.user, score=100, level=0)
        with self.assertRaises(ValidationError):
            session.full_clean()
    
    def test_time_played_min_value(self):
        """Проверка валидации минимального значения time_played."""
        session = GameSession(user=self.user, score=100, level=1, time_played=-1)
        with self.assertRaises(ValidationError):
            session.full_clean()
    
    def test_difficulty_choices(self):
        """Проверка выбора сложности."""
        for difficulty in ['easy', 'medium', 'hard']:
            session = GameSession.objects.create(
                user=self.user,
                score=100,
                level=1,
                difficulty=difficulty
            )
            self.assertEqual(session.difficulty, difficulty)
    
    def test_game_state_json_field(self):
        """Проверка JSON поля game_state."""
        game_state = {
            'ball': {'x': 400, 'y': 300},
            'blocks': [{'x': 100, 'y': 100, 'destroyed': False}],
            'platform': {'x': 350, 'y': 550}
        }
        session = GameSession.objects.create(
            user=self.user,
            game_state=game_state,
            score=100,
            level=1
        )
        self.assertEqual(session.game_state, game_state)
    
    def test_ordering(self):
        """Проверка сортировки по created_at."""
        session1 = GameSession.objects.create(
            user=self.user,
            score=100,
            level=1
        )
        session2 = GameSession.objects.create(
            user=self.user,
            score=200,
            level=2
        )
        sessions = list(GameSession.objects.all())
        # Последняя созданная должна быть первой (ordering = ['-created_at'])
        self.assertEqual(sessions[0], session2)


class LeaderboardModelTest(TestCase):
    """Тесты для модели Leaderboard."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.game_session = GameSession.objects.create(
            user=self.user,
            score=1000,
            level=3,
            is_completed=True
        )
    
    def test_create_leaderboard_entry(self):
        """Проверка создания записи в таблице лидеров."""
        entry = Leaderboard.objects.create(
            user=self.user,
            game_session=self.game_session,
            score=1000,
            rank=1,
            difficulty='medium'
        )
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.score, 1000)
        self.assertEqual(entry.rank, 1)
    
    def test_foreign_key_to_user(self):
        """Проверка связи ForeignKey с User."""
        entry = Leaderboard.objects.create(
            user=self.user,
            game_session=self.game_session,
            score=1000,
            rank=1
        )
        self.assertIn(entry, self.user.leaderboard_entries.all())
    
    def test_foreign_key_to_game_session(self):
        """Проверка связи ForeignKey с GameSession."""
        entry = Leaderboard.objects.create(
            user=self.user,
            game_session=self.game_session,
            score=1000,
            rank=1
        )
        self.assertEqual(entry.game_session, self.game_session)
    
    def test_score_min_value(self):
        """Проверка валидации минимального значения score."""
        entry = Leaderboard(user=self.user, score=-1, rank=1)
        with self.assertRaises(ValidationError):
            entry.full_clean()
    
    def test_rank_min_value(self):
        """Проверка валидации минимального значения rank."""
        entry = Leaderboard(user=self.user, score=1000, rank=0)
        with self.assertRaises(ValidationError):
            entry.full_clean()
    
    def test_unique_together(self):
        """Проверка уникальности комбинации user и game_session."""
        Leaderboard.objects.create(
            user=self.user,
            game_session=self.game_session,
            score=1000,
            rank=1
        )
        with self.assertRaises(Exception):  # IntegrityError
            Leaderboard.objects.create(
                user=self.user,
                game_session=self.game_session,
                score=2000,
                rank=2
            )
    
    def test_ordering(self):
        """Проверка сортировки."""
        entry1 = Leaderboard.objects.create(
            user=self.user,
            game_session=self.game_session,
            score=500,
            rank=2
        )
        entry2 = Leaderboard.objects.create(
            user=self.user,
            game_session=GameSession.objects.create(
                user=self.user,
                score=1000,
                level=2
            ),
            score=1000,
            rank=1
        )
        entries = list(Leaderboard.objects.all())
        # Должны быть отсортированы по score (убывание)
        self.assertEqual(entries[0], entry2)


class AchievementModelTest(TestCase):
    """Тесты для модели Achievement."""
    
    def test_create_achievement(self):
        """Проверка создания достижения."""
        achievement = Achievement.objects.create(
            name='Первая победа',
            description='Победите в первой игре',
            points_required=100,
            level_required=1
        )
        self.assertEqual(achievement.name, 'Первая победа')
        self.assertEqual(achievement.points_required, 100)
        self.assertEqual(achievement.level_required, 1)
    
    def test_points_required_min_value(self):
        """Проверка валидации минимального значения points_required."""
        achievement = Achievement(name='Test', description='Test', points_required=-1)
        with self.assertRaises(ValidationError):
            achievement.full_clean()
    
    def test_level_required_min_value(self):
        """Проверка валидации минимального значения level_required."""
        achievement = Achievement(
            name='Test',
            description='Test',
            points_required=100,
            level_required=0
        )
        with self.assertRaises(ValidationError):
            achievement.full_clean()
    
    def test_ordering(self):
        """Проверка сортировки по points_required."""
        achievement1 = Achievement.objects.create(
            name='Easy',
            description='Easy achievement',
            points_required=100
        )
        achievement2 = Achievement.objects.create(
            name='Hard',
            description='Hard achievement',
            points_required=500
        )
        achievements = list(Achievement.objects.all())
        self.assertEqual(achievements[0], achievement1)


class UserAchievementModelTest(TestCase):
    """Тесты для модели UserAchievement."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.achievement = Achievement.objects.create(
            name='Первая победа',
            description='Победите в первой игре',
            points_required=100
        )
    
    def test_create_user_achievement(self):
        """Проверка создания достижения пользователя."""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        self.assertEqual(user_achievement.user, self.user)
        self.assertEqual(user_achievement.achievement, self.achievement)
        self.assertIsNotNone(user_achievement.unlocked_at)
    
    def test_foreign_key_to_user(self):
        """Проверка связи ForeignKey с User."""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        self.assertIn(user_achievement, self.user.achievements.all())
    
    def test_foreign_key_to_achievement(self):
        """Проверка связи ForeignKey с Achievement."""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        self.assertIn(user_achievement, self.achievement.users.all())
    
    def test_unique_together(self):
        """Проверка уникальности комбинации user и achievement."""
        UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        with self.assertRaises(Exception):  # IntegrityError
            UserAchievement.objects.create(
                user=self.user,
                achievement=self.achievement
            )
    
    def test_unlocked_at_auto_filled(self):
        """Проверка автоматического заполнения unlocked_at."""
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        self.assertIsNotNone(user_achievement.unlocked_at)
        self.assertIsInstance(user_achievement.unlocked_at, timezone.datetime)


class FriendModelTest(TestCase):
    """Тесты для модели Friend."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
    
    def test_create_friend_request(self):
        """Проверка создания запроса в друзья."""
        friend = Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            status='pending'
        )
        self.assertEqual(friend.from_user, self.user1)
        self.assertEqual(friend.to_user, self.user2)
        self.assertEqual(friend.status, 'pending')
    
    def test_foreign_key_relationships(self):
        """Проверка связей ForeignKey."""
        friend = Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )
        self.assertIn(friend, self.user1.friends_sent.all())
        self.assertIn(friend, self.user2.friends_received.all())
    
    def test_status_choices(self):
        """Проверка выбора статуса."""
        for status in ['pending', 'accepted', 'rejected']:
            friend = Friend.objects.create(
                from_user=self.user1,
                to_user=self.user2,
                status=status
            )
            self.assertEqual(friend.status, status)
    
    def test_unique_together(self):
        """Проверка уникальности комбинации from_user и to_user."""
        Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )
        with self.assertRaises(Exception):  # IntegrityError
            Friend.objects.create(
                from_user=self.user1,
                to_user=self.user2
            )
    
    def test_ordering(self):
        """Проверка сортировки по created_at."""
        friend1 = Friend.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )
        friend2 = Friend.objects.create(
            from_user=self.user2,
            to_user=User.objects.create_user(
                username='user3',
                email='user3@example.com',
                password='testpass123'
            )
        )
        friends = list(Friend.objects.all())
        # Последняя созданная должна быть первой
        self.assertEqual(friends[0], friend2)


class ChallengeModelTest(TestCase):
    """Тесты для модели Challenge."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        self.challenger = User.objects.create_user(
            username='challenger',
            email='challenger@example.com',
            password='testpass123'
        )
        self.challenged = User.objects.create_user(
            username='challenged',
            email='challenged@example.com',
            password='testpass123'
        )
    
    def test_create_challenge(self):
        """Проверка создания вызова."""
        challenge = Challenge.objects.create(
            challenger=self.challenger,
            challenged=self.challenged,
            target_score=1000,
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.assertEqual(challenge.challenger, self.challenger)
        self.assertEqual(challenge.challenged, self.challenged)
        self.assertEqual(challenge.target_score, 1000)
        self.assertEqual(challenge.status, 'pending')
    
    def test_foreign_key_relationships(self):
        """Проверка связей ForeignKey."""
        challenge = Challenge.objects.create(
            challenger=self.challenger,
            challenged=self.challenged,
            target_score=1000,
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.assertIn(challenge, self.challenger.challenges_sent.all())
        self.assertIn(challenge, self.challenged.challenges_received.all())
    
    def test_target_score_min_value(self):
        """Проверка валидации минимального значения target_score."""
        challenge = Challenge(
            challenger=self.challenger,
            challenged=self.challenged,
            target_score=0,
            expires_at=timezone.now() + timedelta(days=7)
        )
        with self.assertRaises(ValidationError):
            challenge.full_clean()
    
    def test_challenger_score_min_value(self):
        """Проверка валидации минимального значения challenger_score."""
        challenge = Challenge.objects.create(
            challenger=self.challenger,
            challenged=self.challenged,
            target_score=1000,
            expires_at=timezone.now() + timedelta(days=7)
        )
        challenge.challenger_score = -1
        with self.assertRaises(ValidationError):
            challenge.full_clean()
    
    def test_challenged_score_min_value(self):
        """Проверка валидации минимального значения challenged_score."""
        challenge = Challenge.objects.create(
            challenger=self.challenger,
            challenged=self.challenged,
            target_score=1000,
            expires_at=timezone.now() + timedelta(days=7)
        )
        challenge.challenged_score = -1
        with self.assertRaises(ValidationError):
            challenge.full_clean()
    
    def test_status_choices(self):
        """Проверка выбора статуса."""
        for status in ['pending', 'accepted', 'completed', 'declined']:
            challenge = Challenge.objects.create(
                challenger=self.challenger,
                challenged=self.challenged,
                target_score=1000,
                status=status,
                expires_at=timezone.now() + timedelta(days=7)
            )
            self.assertEqual(challenge.status, status)


