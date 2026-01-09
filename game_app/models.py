"""
Модели данных для игрового приложения.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class TimeStampedModel(models.Model):
    """
    Абстрактная базовая модель с полями created_at и updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    Расширенная модель пользователя.
    """
    email = models.EmailField(unique=True, verbose_name='Email')
    is_guest = models.BooleanField(default=False, verbose_name='Гостевой аккаунт')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class UserProfile(TimeStampedModel):
    """
    Профиль пользователя с дополнительными полями.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Биография'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    total_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Общий счет'
    )
    games_played = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Игр сыграно'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'


class GameSession(TimeStampedModel):
    """
    Сохранение игровой сессии.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='game_sessions',
        verbose_name='Пользователь'
    )
    game_state = models.JSONField(
        default=dict,
        verbose_name='Состояние игры',
        help_text='JSON с текущим состоянием игры (позиция шарика, блоки, платформа и т.д.)'
    )
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Счет'
    )
    level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Уровень'
    )
    time_played = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Время игры (секунды)'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Игра завершена'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Легкий'),
            ('medium', 'Средний'),
            ('hard', 'Сложный'),
        ],
        default='medium',
        verbose_name='Сложность'
    )

    class Meta:
        verbose_name = 'Игровая сессия'
        verbose_name_plural = 'Игровые сессии'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - Уровень {self.level} ({self.score} очков)'


class Leaderboard(TimeStampedModel):
    """
    Таблица лидеров.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries',
        verbose_name='Пользователь'
    )
    game_session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name='leaderboard_entry',
        null=True,
        blank=True,
        verbose_name='Игровая сессия'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Счет'
    )
    rank = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Ранг'
    )
    date_achieved = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата достижения'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Легкий'),
            ('medium', 'Средний'),
            ('hard', 'Сложный'),
        ],
        default='medium',
        verbose_name='Сложность'
    )

    class Meta:
        verbose_name = 'Запись в таблице лидеров'
        verbose_name_plural = 'Таблица лидеров'
        ordering = ['-score', 'date_achieved']
        unique_together = [['user', 'game_session']]

    def __str__(self):
        return f'{self.user.username} - {self.score} очков (Ранг {self.rank})'


class Achievement(TimeStampedModel):
    """
    Достижения игроков.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    icon = models.ImageField(
        upload_to='achievements/',
        null=True,
        blank=True,
        verbose_name='Иконка'
    )
    points_required = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Требуется очков'
    )
    level_required = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Требуется уровень'
    )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['points_required']

    def __str__(self):
        return self.name


class UserAchievement(TimeStampedModel):
    """
    Связь пользователя с достижением.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Пользователь'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Достижение'
    )
    unlocked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата получения'
    )

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = [['user', 'achievement']]
        ordering = ['-unlocked_at']

    def __str__(self):
        return f'{self.user.username} - {self.achievement.name}'


class Friend(TimeStampedModel):
    """
    Система друзей.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friends_sent',
        verbose_name='От пользователя'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friends_received',
        verbose_name='К пользователю'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        unique_together = [['from_user', 'to_user']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username} ({self.status})'


class Challenge(TimeStampedModel):
    """
    Вызовы между друзьями.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принят'),
        ('completed', 'Завершен'),
        ('declined', 'Отклонен'),
    ]

    challenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='challenges_sent',
        verbose_name='Бросающий вызов'
    )
    challenged = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='challenges_received',
        verbose_name='Принимающий вызов'
    )
    target_score = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Целевой счет'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    challenger_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Счет бросающего вызов'
    )
    challenged_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Счет принимающего вызов'
    )
    expires_at = models.DateTimeField(
        verbose_name='Истекает'
    )

    class Meta:
        verbose_name = 'Вызов'
        verbose_name_plural = 'Вызовы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.challenger.username} vs {self.challenged.username}'

