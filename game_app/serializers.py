"""
Сериализаторы для API.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import (
    UserProfile, GameSession, Leaderboard, Achievement,
    UserAchievement, Friend, Challenge
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_guest']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'username', 'avatar', 'bio', 'date_of_birth',
            'total_score', 'games_played', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_score', 'games_played', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля."""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'date_of_birth']


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Профиль создается автоматически через сигнал
        return user


class GameSessionSerializer(serializers.ModelSerializer):
    """Сериализатор игровой сессии."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GameSession
        fields = [
            'id', 'user', 'game_state', 'score', 'level', 'time_played',
            'is_completed', 'difficulty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class GameSessionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания игровой сессии."""
    class Meta:
        model = GameSession
        fields = [
            'id', 'game_state', 'score', 'level', 'time_played',
            'is_completed', 'difficulty'
        ]
        read_only_fields = ['id']


class LeaderboardSerializer(serializers.ModelSerializer):
    """Сериализатор таблицы лидеров."""
    user = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Leaderboard
        fields = [
            'id', 'user', 'username', 'score', 'rank', 'date_achieved',
            'difficulty', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'rank', 'date_achieved', 'created_at']


class AchievementSerializer(serializers.ModelSerializer):
    """Сериализатор достижения."""
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'icon', 'points_required',
            'level_required', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    """Сериализатор достижения пользователя."""
    achievement = AchievementSerializer(read_only=True)
    achievement_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement', 'achievement_id', 'unlocked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unlocked_at', 'created_at', 'updated_at']


class FriendSerializer(serializers.ModelSerializer):
    """Сериализатор друзей."""
    from_user = serializers.StringRelatedField(read_only=True)
    to_user = serializers.StringRelatedField(read_only=True)
    from_username = serializers.CharField(source='from_user.username', read_only=True)
    to_username = serializers.CharField(source='to_user.username', read_only=True)

    class Meta:
        model = Friend
        fields = [
            'id', 'from_user', 'to_user', 'from_username', 'to_username',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'from_user', 'created_at', 'updated_at']


class FriendCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания запроса в друзья."""
    to_username = serializers.CharField(write_only=True)

    class Meta:
        model = Friend
        fields = ['to_username', 'status']
        read_only_fields = ['status']


class ChallengeSerializer(serializers.ModelSerializer):
    """Сериализатор вызова."""
    challenger = serializers.StringRelatedField(read_only=True)
    challenged = serializers.StringRelatedField(read_only=True)
    challenger_username = serializers.CharField(source='challenger.username', read_only=True)
    challenged_username = serializers.CharField(source='challenged.username', read_only=True)

    class Meta:
        model = Challenge
        fields = [
            'id', 'challenger', 'challenged', 'challenger_username',
            'challenged_username', 'target_score', 'status',
            'challenger_score', 'challenged_score', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'challenger', 'created_at', 'updated_at']


class ChallengeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вызова."""
    challenged_username = serializers.CharField(write_only=True)

    class Meta:
        model = Challenge
        fields = ['challenged_username', 'target_score', 'expires_at']

