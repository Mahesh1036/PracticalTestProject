from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or request.user.role == 'admin':
            return True
        return request.method in ['GET']
