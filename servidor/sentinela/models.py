import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class User(AbstractUser):
    pass

class Empresa(models.Model):
    """
    Classe que representa uma empresa
    """
    nome = models.CharField(max_length=255, default='')
    
    # Campos de controle
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    # Relacionamentos
    usuarios = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

class Telefone(models.Model):
    """
    Classe que representa um telefone
    """
    numero = models.CharField(max_length=128, default='')
    def __str__(self):
        return self.numero  

class TelefoneUsuario(Telefone):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'

class TelefoneEmpresa(Telefone):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)   
    class Meta:
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'

class Endereco(models.Model):
    logradouro = models.CharField(max_length=255, null=False)
    def __str__(self):
        return self.logradouro

class EnderecoEmpresa(Endereco):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

class EnderecoUsuario(Endereco):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

class Certificado(models.Model):
    certName = models.FilePathField(path='/etc/ssl/servidor/certs')
    keyName = models.FilePathField(path='/etc/ssl/servidor/private')
    is_revoked = models.BooleanField("Revogado", default=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.certName + "[Revogado]" if(self.is_revoked) else ""

class Central(models.Model):
    """
    Modelo para representar as centrais do sistema
    """
    id = models.UUIDField("Identificador",primary_key=True, default=uuid.uuid4)
    nome = models.CharField(max_length=255, default='')
    certificado = models.ForeignKey(Certificado, on_delete=models.CASCADE)
    # Campos de controle
    is_active = models.BooleanField("Ativa",default=True)
    created_at = models.DateTimeField("Cadastrado em",default=now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relacionamentos
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Central'
        verbose_name_plural = 'Centrais'
