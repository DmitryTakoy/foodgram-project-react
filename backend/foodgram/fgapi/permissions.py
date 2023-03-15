from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """
    Allows read-only access to any request.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class Admin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class AuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Allows access to author and admin users for write operations.
    Allows read-only access to any request.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if user.is_authenticated:
            return user.is_superuser or obj.author == user

        return False