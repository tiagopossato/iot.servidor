from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed
from django.utils.decorators import method_decorator

from manutencao.log import log
from sentinela.models import Central, Certificado

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
def nova_central(request):

    if(request.method != 'POST'):
        return HttpResponseNotAllowed(['POST'])
    try:
        username = request.POST.get('username')
        if(username == None):
            raise KeyError('username')
        password = request.POST.get('password')
        if(password == None):
            raise KeyError('password')
        descricao = request.POST.get('descricao')
        if(descricao == None):
            raise KeyError('descricao')
        if(len(descricao)<2):
            return JsonResponse({'erro': "Descrição muito curta"})
    except KeyError as e:
        print(e)
        return JsonResponse({'erro': "Parâmetro " + str(e) + " não recebido"})
    
    # Autenticação
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'erro': "Usuário não autorizado"})
    try:
        central = Central(descricao=descricao)
        central.save()
        return JsonResponse(central.toJSON())
    except Exception as e:
        return JsonResponse({'erro': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
def novo_certificado(request, central_id):
    if(request.method != 'GET'):
        return HttpResponseNotAllowed(['GET'])
    try:
        username = request.GET.get('username')
        if(username == None):
            raise KeyError('username')
        password = request.GET.get('password') 
        if(password == None):
            raise KeyError('password')    
    except KeyError as e:
        print(e)
        return JsonResponse({'erro': "Parâmetro " + str(e) + " não recebido"})

    # Autenticação
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'erro': "Usuário não autorizado"})

    # Verifica existência da central
    central = None
    try:
        central = Central.objects.get(id=central_id)
    except Exception as e:
        return JsonResponse({'erro': str(e)})

    # Gera novo certificado
    try:
        nc = Certificado(clientName=central.id)
        nc.save()
        central.certificado.revoke()
        central.certificado_id = nc.id
        central.save()
        return JsonResponse(central.toJSON())
    except Exception as e:
        log('CENV02.0', str(e))
        JsonResponse({'erro': str(e)})
    pass