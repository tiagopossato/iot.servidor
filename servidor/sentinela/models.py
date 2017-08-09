import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from manutencao.log import log
import subprocess
from subprocess import CalledProcessError
from django.conf import settings
from os import remove
from time import sleep

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
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'

class TelefoneEmpresa(Telefone):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)   
    class Meta:
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'

class Endereco(models.Model):
    logradouro = models.CharField(max_length=255, null=False)
    def __str__(self):
        return self.logradouro

class EnderecoEmpresa(Endereco):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

class EnderecoUsuario(Endereco):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

class Certificado(models.Model):
    certName = models.CharField("Nome", max_length=255, null=False)
    clientName = models.CharField("Cliente", max_length=50)
    is_revoked = models.BooleanField("Revogado", default=False)
    created_at = models.DateTimeField("Criado em", default=now)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)
    
    def __str__(self):
        # return self.certName
        return self.certName + (" [Revogado]" if(self.is_revoked) else "")

    def save(self, *args, **kwargs):
        """
        Método sobrescrito para criar o certificado antes de salvar
        """
        try:
            # Verifica se é para criar um novo certificado
            if(len(self.certName) == 0):
                self.certName = uuid.uuid4().hex
                subprocess.check_call([settings.SSL_DIR+"/bin/create-client", "-n", str(self.certName), "-c", str(self.clientName)])

            # Chama o método real
            super(Certificado, self).save(*args, **kwargs)
        except CalledProcessError as e:
            if(e.returncode == 1):
                log("CERT01.0","Ja existe um certificado com este nome")
                raise
            elif(e.returncode == 2):
                log("CERT01.1","Argumentos incorretos: " + str(e.cmd))
                raise
            else:
                print()
                print(e.output.decode())
                print(e.returncode)
                raise
        except Exception as e:
            log("CERT01.2",str(e))
            raise

    def delete(self, *args, **kwargs):
        try:
            self.revoke()            
            super(Certificado, self).delete(*args, **kwargs)
        except Exception as e:
            log("CERT03.0",str(e))

    def revoke(self):
        """
        Revoga o certificado
        """
        try:
            razao = 5
            subprocess.check_call([settings.SSL_DIR+"/bin/revoke-cert", "-c", settings.SSL_DIR+"/certs/"+str(self.certName)+".client.crt", "-r", str(razao)])
            self.is_revoked = True
            self.save()
            remove(settings.SSL_DIR+"/certs/"+str(self.certName)+".client.crt")
            # Reinicia mosquitto
            print('restart mosquitto')
            print(subprocess.check_call(['sudo', '/bin/systemctl', 'stop', 'mosquitto']))
            sleep(1)
            print(subprocess.check_call(['sudo', '/bin/systemctl', 'start', 'mosquitto']))
            return True
        except CalledProcessError as e:
            if(e.returncode == 1):
                print("Nao pode encontrar um certificado com este nome. " + str(e.output.decode()))    
                raise
            elif(e.returncode == 2):
                print("Argumentos incorretos: " + str(e.cmd))
                raise
            else:
                print()
                print(e.output.decode())
                print(e.returncode)
                raise

    def getCertFile(self):
        try:
            return open(settings.SSL_DIR + "/certs/" + self.certName+ ".client.crt").read()
        except Exception as e:
            log("CERT02.0",str(e))
    
    def getKeyFile(self):
        try:
            keyFile = open(settings.SSL_DIR + "/private/" + self.certName+ ".client.key").read()
            remove(settings.SSL_DIR + "/private/" + self.certName+ ".client.key")
            return keyFile
        except Exception as e:
            log("CERT02.1",str(e))
            return None

    def getCaFile(self):
        try:
            return open(settings.SSL_DIR + "/ca/ca.crt").read()
        except Exception as e:
            log("CERT02.2",str(e))

class Central(models.Model):


    """
    Modelo para representar as centrais do sistema
    """
    id = models.UUIDField("Identificador", primary_key=True, default=uuid.uuid4)
    descricao = models.CharField("Descrição", max_length=255, default='')
    # Campos de controle
    is_active = models.BooleanField("Ativa",default=True)
    created_at = models.DateTimeField("Cadastrado em",default=now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relacionamentos
    certificado = models.ForeignKey(Certificado, on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Método sobrescrito para criar o certificado antes de salvar
        """
        try:
            if(self.is_active == False and self.certificado.is_revoked == False):
                self.certificado.revoke()
            # Chama o método real           
            super(Central, self).save(*args, **kwargs)
        except Exception as e:
            log('NCE01.0',str(e))

    def delete(self, *args, **kwargs):
        try:
            self.certificado.revoke()
            super(Central, self).delete(*args, **kwargs)
        except Exception as e:
            log("NCE02.0",str(e))

    def __str__(self):
        return self.descricao

    class Meta:
        unique_together = ('descricao', 'empresa',)
        verbose_name = 'Central'
        verbose_name_plural = 'Centrais'

class Grandeza(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=255, null=False, unique=True)
    unidade = models.CharField(max_length=15, null=False, unique=True)
    created_at = models.DateTimeField("Criado em", default=now)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)
    
    def __str__(self):
        return str(self.unidade) + ' (' + str(self.nome) + ')'

    class Meta:
        verbose_name = 'Grandeza'
        verbose_name_plural = 'Grandezas'

class Alarme(models.Model):
    uid = models.UUIDField(primary_key=True)
    codigoAlarme = models.UUIDField('Codigo')
    mensagemAlarme = models.CharField('Mensagem',max_length=255, null=False)
    prioridadeAlarme = models.IntegerField('Prioridade',null=False)
    ativo = models.BooleanField('Ativo',default=False, null=False)
    reconhecido = models.BooleanField('Reconhecido',default=False, null=False)
    tempoAtivacao = models.DateTimeField('Ativado em',null=False)
    tempoInativacao = models.DateTimeField('Desativado em',null=True)

    ambiente = models.UUIDField('Ambiente')
    grandeza = models.ForeignKey(
        Grandeza, to_field='codigo', on_delete=models.PROTECT)

    central = models.ForeignKey(
        Central, to_field='id', on_delete=models.PROTECT)

    def __str__(self):
        return self.mensagemAlarme + '[' + ('Ativo' if self.ativo else 'Inativo') + ']'

    class Meta:
        verbose_name = 'Alarme'
        verbose_name_plural = 'Alarmes'


class Leitura(models.Model):
    valor = models.FloatField('Valor')
    sensor = models.UUIDField('Sensor')
    ambiente = models.UUIDField('Ambiente')
    created_at = models.DateTimeField("Criado em", null=False)
    grandeza = models.ForeignKey(
        Grandeza, to_field='codigo', on_delete=models.PROTECT)
    central = models.ForeignKey(
        Central, to_field='id', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.valor) + " " + str(self.grandeza.unidade)

    class Meta:
        unique_together = ('sensor', 'ambiente','created_at')
        verbose_name = 'Leitura'
        verbose_name_plural = 'Leituras'