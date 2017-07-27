from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from manutencao.log import log
from sentinela.models import Central, Certificado


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
        if(len(descricao) < 2):
            return JsonResponse(status=400, data={'erro': "Descrição muito curta"})
    except KeyError as e:
        print(e)
        return JsonResponse(status=400, data={'erro': "Parâmetro " + str(e) + " não recebido"})

    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse(status=400, data={'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})

    try:
        central = Central(descricao=descricao)
        central.save()
        return novo_certificado(central)
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})


@method_decorator(csrf_exempt, name='dispatch')
def editar(request, central_id):

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
        if(len(descricao) < 2):
            return JsonResponse(status=400, data={'erro': "Descrição muito curta"})
    except KeyError as e:
        print(e)
        return JsonResponse(status=400, data={'erro': "Parâmetro " + str(e) + " não recebido"})

    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse(status=400, data={'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})

    try:
        central = Central.objects.get(id=central_id, is_active=True)
        central.descricao = descricao
        central.save()
        return JsonResponse(status=200, data={})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})


def troca_certificado(request, central_id):
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
        return JsonResponse(status=400, data={'erro': "Parâmetro " + str(e) + " não recebido"})

    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse(status=400, data={'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})

    # Verifica existência da central
    try:
        central = Central.objects.get(id=central_id, is_active=True)
        # Revoga certificao antigo
        central.certificado.revoke()
        # Responde com o resultado do método para gerar o certificado
        return novo_certificado(central)
    except Central.DoesNotExist:
        return JsonResponse(status=400, data={'erro': "Central não encontrada ou inativa"})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})


def novo_certificado(central):
    """
    Método que gera um novo certificado para a central
    """
    # Gera novo certificado
    try:
        nc = Certificado(clientName=central.id)
        nc.save()
        # Associa novo certificado
        central.certificado_id = nc.id
        central.save()
        central = Central.objects.get(id=central.id)
        # Retorna com a nova estrutura da central
        j = {}
        j['id'] = central.id
        j['descricao'] = central.descricao if central.descricao else None
        j['empresa'] = central.empresa.nome if central.empresa else None
        j['caFile'] = central.certificado.getCaFile()
        j['certFile'] = central.certificado.getCertFile()
        j['keyFile'] = central.certificado.getKeyFile()
        return JsonResponse(status=200, data=j)
    except Exception as e:
        log('CENV02.0', str(e))
        return JsonResponse(status=400, data={'erro': str(e)})
    pass


def get_centrais_inativas(request):
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
        return JsonResponse(status=400, data={'erro': "Parâmetro " + str(e) + " não recebido"})
    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse(status=400, data={'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})

    try:
        central = Central.objects.get(id=central_id, is_active=True)
        central.is_active = False
        central.save()
        return JsonResponse({'sucesso': 'A central foi inativada'})
    except Central.DoesNotExist:
        return JsonResponse(status=400, data={'erro': 'nenhuma central ativa com esse identificador'})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})


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
        return JsonResponse(status=400, data={'erro': "Parâmetro " + str(e) + " não recebido"})
    # Autenticação
    try:
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse(status=400, data={'erro': "Usuário não autorizado"})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})

    try:
        central = Central.objects.get(id=central_id, is_active=False)
        central.is_active = True
        central.save()
        return novo_certificado(central)
    except Central.DoesNotExist:
        return JsonResponse(status=400, data={'erro': 'nenhuma central inativa com esse identificador'})
    except Exception as e:
        return JsonResponse(status=400, data={'erro': str(e)})
