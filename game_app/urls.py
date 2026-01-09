"""
URL маршруты для API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView, UserProfileViewSet, GameSessionViewSet,
    LeaderboardViewSet, AchievementViewSet, UserAchievementViewSet,
    FriendViewSet, ChallengeViewSet
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'game-sessions', GameSessionViewSet, basename='gamesession')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'user-achievements', UserAchievementViewSet, basename='userachievement')
router.register(r'friends', FriendViewSet, basename='friend')
router.register(r'challenges', ChallengeViewSet, basename='challenge')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

