"""Archivo para configurar permisos personalizados."""

from rest_framework import permissions, serializers


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Permiso para el administrador o solo lectura."""

    def has_permission(self, request, view):
        """Redefinido Has Permission."""
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # solo puede crear categorias si es admin.
        return request.user and request.user.is_staff


# Solo puede verlo el propio user
class IsOwner(permissions.BasePermission):
    """Solo el dueño de la propia instancia."""

    def has_permission(self, request, view):
        """Redefinido has permision."""
        if request.method in permissions.SAFE_METHODS:
            # import pdb; pdb.set_trace()
            try:
                client = int(request.query_params['client'])
                return request.user.id == client
            except Exception as e:
                string_error = u"Exception " + str(e)
                raise serializers.ValidationError(detail=string_error)

        if request.method == "POST":
            return request.user.id == request.data["client"]


class IsAdminOrOwner(permissions.BasePermission):
    """Solo el administrador el mismo usuario."""

    def has_object_permission(self, request, view, obj):
        """Metodo redefinido."""
        return (request.user and request.user.is_staff) or request.user.id == obj.id


class IsClient(permissions.BasePermission):
    """Permiso solo para el rol cliente."""

    def has_permission(self, request, view):
        """Solo el vendedor puede crear."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.role_id == 2
        return True


class IsSeller(permissions.BasePermission):
    """Permiso para solo el vendedor."""

    def has_permission(self, request, view):
        """Solo el vendedor puede crear."""
        if request.method == "POST":
            return request.user and request.user.role_id == 4
        return True

# En listado solo el admin
class IsAdminOnList(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff

        return True
