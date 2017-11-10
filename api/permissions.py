from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # solo puede crear categorias si es admin.
        return request.user and request.user.is_staff

# Solo puede verlo el propio user
class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        client = request.query_params['client']
        return request.user.id == client

# Solo el admin y/o el user
class IsAdminOrOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.user and request.user.is_staff) or request.user.id == obj.id


# En listado solo el admin
class IsAdminOnList(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff

        return True
