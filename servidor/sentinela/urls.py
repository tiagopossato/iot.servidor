from django.conf.urls import url
from . import central

urlpatterns = [
    url(r'^central/inativas', central.get_centrais_inativas),
    url(r'^central/nova', central.nova_central),
    url(r'^central/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/novo-certificado', central.troca_certificado),
    url(r'^central/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/editar', central.editar),
    url(r'^central/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/inativar', central.inativar),
    url(r'^central/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/reativar', central.reativar),    
]