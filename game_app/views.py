"""
Представления API для игрового приложения.
"""
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    UserProfile, GameSession, Leaderboard, Achievement,
    UserAchievement, Friend, Challenge
)
from .serializers import (
    UserSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    RegisterSerializer, GameSessionSerializer, GameSessionCreateSerializer,
    LeaderboardSerializer, AchievementSerializer, UserAchievementSerializer,
    FriendSerializer, FriendCreateSerializer, ChallengeSerializer,
    ChallengeCreateSerializer
)
from .permissions import IsGuestOrReadOnly, IsOwnerOrReadOnly

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация пользователя."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Генерируем токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserProfileViewSet(viewsets.ModelViewSet):
    """Управление профилем пользователя."""
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        if self.action == 'list':
            # Все могут видеть профили
            return UserProfile.objects.all()
        # Для остальных действий - только свой профиль
        return UserProfile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить свой профиль."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def public(self, request, pk=None):
        """Публичный профиль пользователя (доступен гостям)."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class GameSessionViewSet(viewsets.ModelViewSet):
    """Управление игровыми сессиями."""
    permission_classes = [IsAuthenticated, IsGuestOrReadOnly]
    serializer_class = GameSessionSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return GameSession.objects.all()
        return GameSession.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return GameSessionCreateSerializer
        return GameSessionSerializer
    
    def create(self, request, *args, **kwargs):
        """Переопределяем create для возврата полного объекта."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Возвращаем полный объект через GameSessionSerializer
        instance = serializer.instance
        response_serializer = GameSessionSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        game_session = serializer.save(user=self.request.user)
        # Обновляем профиль пользователя
        profile = self.request.user.profile
        profile.total_score = max(profile.total_score, game_session.score)
        profile.games_played += 1
        profile.save()
        
        # Проверяем достижения
        self._check_achievements(self.request.user, serializer.validated_data)
        
        # Обновляем таблицу лидеров
        self._update_leaderboard(self.request.user, game_session)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Получить последнее сохранение."""
        latest_session = self.get_queryset().filter(
            user=request.user,
            is_completed=False
        ).order_by('-created_at').first()
        
        if not latest_session:
            return Response(
                {'detail': 'Сохранений не найдено.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(latest_session)
        return Response(serializer.data)

    def _check_achievements(self, user, game_data):
        """Проверка и выдача достижений."""
        score = game_data.get('score', 0)
        level = game_data.get('level', 1)
        
        achievements = Achievement.objects.filter(
            points_required__lte=score,
            level_required__lte=level
        )
        
        for achievement in achievements:
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )

    def _update_leaderboard(self, user, game_session):
        """Обновление таблицы лидеров."""
        if game_session.is_completed:
            # Вычисляем ранг
            higher_scores = Leaderboard.objects.filter(
                score__gt=game_session.score,
                difficulty=game_session.difficulty
            ).count()
            rank = higher_scores + 1
            
            Leaderboard.objects.update_or_create(
                user=user,
                game_session=game_session,
                defaults={
                    'score': game_session.score,
                    'rank': rank,
                    'date_achieved': timezone.now(),
                    'difficulty': game_session.difficulty,
                }
            )
            
            # Обновляем ранги остальных записей
            Leaderboard.objects.filter(
                score__lte=game_session.score,
                difficulty=game_session.difficulty
            ).exclude(user=user).update(rank=F('rank') + 1)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """Таблица лидеров."""
    queryset = Leaderboard.objects.all()
    permission_classes = [AllowAny]
    serializer_class = LeaderboardSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['difficulty']
    ordering_fields = ['score', 'rank', 'date_achieved']
    ordering = ['-score']
    search_fields = ['user__username']

    @action(detail=False, methods=['get'])
    def top(self, request):
        """Топ игроков."""
        difficulty = request.query_params.get('difficulty', None)
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset()
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        top_players = queryset[:limit]
        serializer = self.get_serializer(top_players, many=True)
        return Response(serializer.data)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Достижения."""
    queryset = Achievement.objects.all()
    permission_classes = [AllowAny]
    serializer_class = AchievementSerializer


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """Достижения пользователя."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id and self.request.user.is_staff:
            return UserAchievement.objects.filter(user_id=user_id)
        return UserAchievement.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """Мои достижения."""
        achievements = self.get_queryset()
        serializer = self.get_serializer(achievements, many=True)
        return Response(serializer.data)


class FriendViewSet(viewsets.ModelViewSet):
    """Система друзей."""
    permission_classes = [IsAuthenticated, IsGuestOrReadOnly]
    serializer_class = FriendSerializer

    def get_queryset(self):
        user = self.request.user
        # Возвращаем все дружеские связи, где пользователь участвует
        return Friend.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return FriendCreateSerializer
        return FriendSerializer

    def create(self, request, *args, **kwargs):
        """Отправить запрос в друзья."""
        serializer = FriendCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        to_username = serializer.validated_data['to_username']
        try:
            to_user = User.objects.get(username=to_username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if to_user == request.user:
            return Response(
                {'detail': 'Нельзя добавить себя в друзья.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, не существует ли уже связь
        existing = Friend.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()
        
        if existing:
            return Response(
                {'detail': 'Запрос в друзья уже существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        friend = Friend.objects.create(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        )
        
        serializer = FriendSerializer(friend)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Принять запрос в друзья."""
        friend = self.get_object()
        if friend.to_user != request.user:
            return Response(
                {'detail': 'Вы не можете принять этот запрос.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        friend.status = 'accepted'
        friend.save()
        serializer = self.get_serializer(friend)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Отклонить запрос в друзья."""
        friend = self.get_object()
        if friend.to_user != request.user:
            return Response(
                {'detail': 'Вы не можете отклонить этот запрос.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        friend.status = 'rejected'
        friend.save()
        serializer = self.get_serializer(friend)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_friends(self, request):
        """Мои друзья."""
        friends = Friend.objects.filter(
            Q(from_user=request.user, status='accepted') |
            Q(to_user=request.user, status='accepted')
        )
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)


class ChallengeViewSet(viewsets.ModelViewSet):
    """Вызовы между друзьями."""
    permission_classes = [IsAuthenticated, IsGuestOrReadOnly]
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        user = self.request.user
        return Challenge.objects.filter(
            Q(challenger=user) | Q(challenged=user)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return ChallengeCreateSerializer
        return ChallengeSerializer

    def create(self, request, *args, **kwargs):
        """Создать вызов."""
        serializer = ChallengeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenged_username = serializer.validated_data['challenged_username']
        try:
            challenged = User.objects.get(username=challenged_username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем, что пользователи друзья
        is_friend = Friend.objects.filter(
            Q(from_user=request.user, to_user=challenged, status='accepted') |
            Q(from_user=challenged, to_user=request.user, status='accepted')
        ).exists()
        
        if not is_friend:
            return Response(
                {'detail': 'Вы можете бросать вызов только друзьям.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        challenge = Challenge.objects.create(
            challenger=request.user,
            challenged=challenged,
            target_score=serializer.validated_data['target_score'],
            expires_at=serializer.validated_data.get('expires_at', timezone.now() + timedelta(days=7))
        )
        
        serializer = ChallengeSerializer(challenge)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Принять вызов."""
        challenge = self.get_object()
        if challenge.challenged != request.user:
            return Response(
                {'detail': 'Вы не можете принять этот вызов.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        challenge.status = 'accepted'
        challenge.save()
        serializer = self.get_serializer(challenge)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_score(self, request, pk=None):
        """Отправить счет для вызова."""
        challenge = self.get_object()
        score = request.data.get('score')
        
        if not score:
            return Response(
                {'detail': 'Не указан счет.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user == challenge.challenger:
            challenge.challenger_score = score
        elif request.user == challenge.challenged:
            challenge.challenged_score = score
        else:
            return Response(
                {'detail': 'Вы не участвуете в этом вызове.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Если оба счета отправлены, завершаем вызов
        if challenge.challenger_score is not None and challenge.challenged_score is not None:
            challenge.status = 'completed'
        
        challenge.save()
        serializer = self.get_serializer(challenge)
        return Response(serializer.data)

