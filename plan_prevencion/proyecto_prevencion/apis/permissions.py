from rest_framework.permissions import BasePermission

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class IsRegularApprovedUser(BasePermission):
    """
    Permite acceso solo a usuarios autenticados, no superusuarios y aprobados.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            not request.user.is_superuser and
            request.user.aprobado
        )
