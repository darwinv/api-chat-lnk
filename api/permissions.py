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
    """Solo el administrador o el mismo usuario."""

    def has_object_permission(self, request, view, obj):
        """Metodo redefinido."""
        return (request.user and request.user.is_staff) or request.user.id == obj.id


class IsAdmin(permissions.BasePermission):
    """Solo el administrador."""

    def has_object_permission(self, request, view, obj):
        """Metodo redefinido."""
        return request.user and request.user.is_staff


class isAdminBackWrite(permissions.BasePermission):
    """Administrador Rol 1."""

    def has_permission(self, request, view):
        """Permiso general."""
        if request.method == "POST":
            return request.user and request.user.role_id == 1


class IsClient(permissions.BasePermission):
    """Permiso solo para el rol cliente."""

    def has_object_permission(self, request, view, obj):
        """Permiso a nivel de objeto."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.role_id == 2
        return True

    def has_permission(self, request, view):
        """Permiso general."""
        return request.user and request.user.role_id == 2

class IsAdminOrClient(permissions.BasePermission):
    """Solo Administradores o Clientes."""

    def has_permission(self, request, view):
        """Permiso General."""
        if request.user and request.user.is_staff:
            return True
        elif request.user and request.user.role_id == 2:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Permiso a nivel de objeto."""
        if request.user and request.user.is_staff:
            return True
        elif request.user and request.user.role_id == 2:
            return True
        return False


class IsAdminOrSeller(permissions.BasePermission):
    """Solo Administradores o Vendedores."""

    def has_permission(self, request, view):
        """Permiso General."""
        if request.user and request.user.is_staff:
            return True
        elif request.user and request.user.role_id == 4:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Permiso de nivel objeto. PAara saber si se trata del vendedor del obj o un admin """

        if request.method == "POST" or request.method == "PUT":
            # Si es el vendedor asignado del clliente
            is_seller_assigned = hasattr(obj, 'seller_assigned') and request.user.id == obj.seller_assigned.id
            # Si es el vendedor del contacto
            is_seller_of_contact = hasattr(obj, 'seller') and request.user.id == obj.seller.id

            return is_seller_assigned  or is_seller_of_contact or request.user.is_staff


class IsClientOrSpecialistAndOwner(permissions.BasePermission):
    """Solo Cliente y Dueño del objeto actual."""

    def has_permission(self, request, view):
        """Permiso General."""
        if (request.user
                and (request.user.role_id == 2 or request.user.role_id == 3)):
            return True
        return False

    def has_object_permission(self, request, view, owner_id):
        """Permiso nivel objeto."""
        if request.method == "POST" or request.method == "PUT":
            return request.user.id == owner_id


class IsOwnerAndClient(permissions.BasePermission):
    """Solo Dueños y que sea cliente."""

    def has_permission(self, request, view):
        """Permiso General."""
        if (request.user and (request.user.role_id == 2)):
            return True
        return False

    def has_object_permission(self, request, view, owner_id):
        """Permiso nivel objeto."""
        if request.method == "POST" or request.method == "PUT":
            return request.user.id == owner_id



class IsAdminReadOrSpecialistOwner(permissions.BasePermission):
    """Solo Administradores o Especialistas."""

    def has_permission(self, request, view):
        """Permiso General."""
        if request.user and request.user.is_staff:
            return True
        elif request.user and request.user.role_id == 3:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Permiso a nivel de objeto."""
        if request.method == "POST" or request.method == "PUT":
            return (request.user and request.user.role_id == 3) and request.user.id == obj.id


class IsSpecialist(permissions.BasePermission):
    """Es administrador o especialista."""

    def has_permission(self, request, view):
        """Solo Admin o Especialista."""
        if request.user and request.user.role_id == 3:
            return True
        return False


class IsAdminOrSpecialist(permissions.BasePermission):
    """Es administrador o especialista."""

    def has_permission(self, request, view):
        """Solo Admin o Especialista."""
        if request.user and request.user.is_staff:
            return True
        elif request.user and request.user.role_id == 3:
            return True
        return False


class IsSeller(permissions.BasePermission):
    """Permiso para solo el vendedor."""

    def has_permission(self, request, view):
        """Solo el vendedor puede crear."""
        if request.method == "POST":
            return request.user and request.user.role_id == 4
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.role_id == 4


# En listado solo el admin
class IsAdminOnList(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        return True
