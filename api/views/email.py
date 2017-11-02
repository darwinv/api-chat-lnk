from rest_framework.decorators import api_view
from api.emails import BasicEmailAmazon
from rest_framework.response import Response

@api_view(['POST'])
def mail(request):
    if request.method == 'POST':
        mail = BasicEmailAmazon(subject='epale',to='darwin.vasqz@gmail.com',
                                template='base')
        return Response(mail.sendmail())
    #     return Response({"message": "Got some data!", "data": request.data})
    # return Response({"message": "Hello, world!"})
