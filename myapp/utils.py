import uuid

from django.http import JsonResponse

from myapp.models import TokenPourStagiaire
def new_token() : 
    token = uuid.uuid1().hex
    return token




def token_response(user):
    token = new_token()
    TokenPourStagiaire.objects.create(token=token, user=user) 
    response_data = {
        'message': 'login successful',
        'token': token,
        'username' : user.cin,    
    }
    print(token)
    return JsonResponse(response_data)