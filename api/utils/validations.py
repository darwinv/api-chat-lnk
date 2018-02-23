from django.http import Http404

class Operations():
    def get_id_IsAdminOrClient(self, request):
        #metodo que obtiene el id de un administrador o un cliente
        data = request.data
        # validar si es cliente o admin par sacar el id
        if request.user and request.user.role_id == 1:
            # si es admin se necesita sacar el id de body
            return data['client_id']
        elif request.user and request.user.role_id == 2:
            # si es cliente sacar el id del token
            return request.user.id
        else:
            raise Http404