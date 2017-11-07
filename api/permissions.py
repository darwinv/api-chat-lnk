from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # solo puede crear categorias si es admin.
        return request.user and request.user.is_staff

class IsAdminOnList(permissions.BasePermission):

    def has_permission(self, request, view):
        # solo puede listar clientes si es admin.
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        
        return True
