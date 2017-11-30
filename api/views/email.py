from rest_framework.decorators import api_view
from api.emails import BasicEmailAmazon
from rest_framework.response import Response


# metodo para enviar el mail
@api_view(['POST'])
def mail(request):
    if request.method == 'POST':
        mail = BasicEmailAmazon(subject='epale',to='darwin.vasqz@gmail.com',
                                template='base')
        # import pdb; pdb.set_trace()
        return Response(mail.sendmail(args=request.data))
    #     return Response({"message": "Got some data!", "data": request.data})
    # return Response({"message": "Hello, world!"})
