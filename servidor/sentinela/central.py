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
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse({'erro': str(e)})

    try:
        central = Central(descricao=descricao)
        central.save()
        return JsonResponse(central.toJSON())
    except Exception as e:
        return JsonResponse({'erro': str(e)})


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
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse({'erro': str(e)})

    # Responde com o resultado do método para trocar o certificado
    return troca_certificado(central_id)

def troca_certificado(central_id):
    """
    Método que revoga o certificado atual e gera um novo certificado para a central
    """
    # Verifica existência da central
    try:
        central = Central.objects.get(id=central_id, is_active=True)
    except Central.DoesNotExist:
        return JsonResponse({'erro': "Central não encontrada ou inativa"})      
    except Exception as e:
        return JsonResponse({'erro': str(e)})
   
    # Gera novo certificado
    try:
        nc = Certificado(clientName=central.id)
        nc.save()
        # Revoga certificao antigo
        central.certificado.revoke()
        # Associa novo certificado
        central.certificado_id = nc.id
        central.save()
        central = Central.objects.get(id=central_id)
        # Retorna com a nova estrutura da central
        return JsonResponse(central.toJSON())
    except Exception as e:
        log('CENV02.0', str(e))
        return JsonResponse({'erro': str(e)})
    pass

def inativas(request):
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
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse({'erro': str(e)})

    centrais = Central.objects.filter(is_active=False)
    saida = []
    for central in centrais:
        r = {}
        r['id'] = central.id
        r['descricao'] = central.descricao
        r['empresa'] = central.empresa.nome if central.empresa else None
        saida.append(r)
    print(saida)
    return JsonResponse(saida, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
def inativar(request, central_id):
    if(request.method != 'POST'):
        return HttpResponseNotAllowed(['POST'])
    try:
        username = request.POST.get('username')
        if(username == None):
            raise KeyError('username')
        password = request.POST.get('password')
        if(password == None):
            raise KeyError('password')
    except KeyError as e:
        print(e)
        return JsonResponse({'erro': "Parâmetro " + str(e) + " não recebido"})    
    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse({'erro': str(e)})

    try:
        central = Central.objects.get(id=central_id, is_active=True)
        central.is_active = False
        central.save()
        return JsonResponse({'sucesso':'A central foi inativada'})
    except Central.DoesNotExist:
        return JsonResponse({'erro':'nenhuma central ativa com esse identificador'})
    except Exception as e:
        return JsonResponse({'erro': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
def reativar(request, central_id):
    if(request.method != 'POST'):
        return HttpResponseNotAllowed(['POST'])
    try:
        username = request.POST.get('username')
        if(username == None):
            raise KeyError('username')
        password = request.POST.get('password')
        if(password == None):
            raise KeyError('password')
    except KeyError as e:
        print(e)
        return JsonResponse({'erro': "Parâmetro " + str(e) + " não recebido"})    
    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse({'erro': str(e)})

    try:
        central = Central.objects.get(id=central_id, is_active=False)
        central.is_active = True
        central.save()
        return troca_certificado(central_id)
    except Central.DoesNotExist:
        return JsonResponse({'erro':'nenhuma central inativa com esse identificador'})
    except Exception as e:
        return JsonResponse({'erro': str(e)})
