ActivationView




class ClientDetailByUsername(APIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self, username):
        try:
            return Client.objects.get(username=username)
        except Client.DoesNotExist:
            raise Http404

    def get(self, request, username):
        client = self.get_object(username)
        serializer = ClientSerializer(client)
        return Response(serializer.data)