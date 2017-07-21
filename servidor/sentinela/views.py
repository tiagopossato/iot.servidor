from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed

from sentinela.models import Central

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
def central(request):

    if(request.method != 'POST'):
        return HttpResponseNotAllowed(['POST'])
    try:
        username = str(request.POST['username'])
        password = str(request.POST['password'])
        descricao = str(request.POST['descricao'])
    except KeyError as e:
       return JsonResponse({'error': "Parâmetro " + str(e) + " não recebido"})
    
    # Autenticação
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error': "Usuário não autorizado"})
    try:
        central = Central(descricao=descricao)
        central.save()
        return JsonResponse(central.toJSON())
    except Exception as e:
        return JsonResponse({'error': str(e)})