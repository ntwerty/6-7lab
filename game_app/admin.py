"""
Административная панель Django.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.utils.html import format_html
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.utils import timezone

from .models import (
    User, UserProfile, GameSession, Leaderboard,
    Achievement, UserAchievement, Friend, Challenge
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей."""
    list_display = ['username', 'email', 'is_staff', 'is_guest', 'date_joined']
    list_filter = ['is_staff', 'is_guest', 'date_joined']
    search_fields = ['username', 'email']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей."""
    list_display = ['user', 'total_score', 'games_played', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['total_score', 'games_played', 'created_at', 'updated_at']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    """Админка для игровых сессий."""
    list_display = ['user', 'score', 'level', 'difficulty', 'is_completed', 'created_at']
    list_filter = ['difficulty', 'is_completed', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_to_xlsx']

    def export_to_xlsx(self, request, queryset):
        """Экспорт игровых сессий в XLSX."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Игровые сессии"

        # Заголовки
        headers = [
            'ID', 'Пользователь', 'Счет', 'Уровень', 'Сложность',
            'Время игры (сек)', 'Завершена', 'Дата создания'
        ]
        ws.append(headers)

        # Стили для заголовков
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # Данные
        for session in queryset:
            ws.append([
                session.id,
                session.user.username,
                session.score,
                session.level,
                session.get_difficulty_display(),
                session.time_played,
                'Да' if session.is_completed else 'Нет',
                session.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Автоматическая ширина колонок
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Создаем HTTP ответ
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=game_sessions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        wb.save(response)
        return response

    export_to_xlsx.short_description = "Экспортировать выбранные сессии в XLSX"


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    """Админка для таблицы лидеров."""
    list_display = ['user', 'score', 'rank', 'difficulty', 'date_achieved']
    list_filter = ['difficulty', 'date_achieved']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-score']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Админка для достижений."""
    list_display = ['name', 'points_required', 'level_required', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    """Админка для достижений пользователей."""
    list_display = ['user', 'achievement', 'unlocked_at']
    list_filter = ['unlocked_at', 'achievement']
    search_fields = ['user__username', 'achievement__name']
    readonly_fields = ['unlocked_at', 'created_at', 'updated_at']
    actions = ['assign_achievement']

    def assign_achievement(self, request, queryset):
        """Назначить достижение пользователям."""
        # Получаем ID достижения из POST запроса
        achievement_id = request.POST.get('achievement_id')
        if not achievement_id:
            from django.contrib import messages
            messages.error(request, "Необходимо выбрать достижение.")
            return
        
        try:
            achievement = Achievement.objects.get(id=achievement_id)
            count = 0
            for user_achievement in queryset:
                if not UserAchievement.objects.filter(
                    user=user_achievement.user,
                    achievement=achievement
                ).exists():
                    UserAchievement.objects.create(
                        user=user_achievement.user,
                        achievement=achievement
                    )
                    count += 1
            self.message_user(request, f"Достижение '{achievement.name}' назначено {count} пользователям.")
        except Achievement.DoesNotExist:
            from django.contrib import messages
            messages.error(request, "Достижение не найдено.")

    assign_achievement.short_description = "Назначить достижение выбранным пользователям"


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    """Админка для друзей."""
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    """Админка для вызовов."""
    list_display = ['challenger', 'challenged', 'target_score', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['challenger__username', 'challenged__username']
    readonly_fields = ['created_at', 'updated_at']

