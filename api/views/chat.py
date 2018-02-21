from rest_framework.decorators import api_view
from api.emails import BasicEmailAmazon
from rest_framework.response import Response


@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        # Code block for POST request
        print(request.data)
        return Response(request.data["text"])
    # else:
        # Code block for GET request (will also match PUT, HEAD, DELETE, etc)
