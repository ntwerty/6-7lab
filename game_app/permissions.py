"""
Кастомные разрешения для API.
"""
from rest_framework import permissions


class IsGuestOrReadOnly(permissions.BasePermission):
    """
    Разрешение для гостей: только чтение.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return not request.user.is_guest if request.user.is_authenticated else False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только владелец может редактировать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только администратор может редактировать.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff if request.user.is_authenticated else False

