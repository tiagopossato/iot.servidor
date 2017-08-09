from django.db import models


class User(models.Model):
    username = models.CharField("Usuário",unique=True, max_length=255)
    pw = models.CharField("Senha", max_length=255, null=True, blank=True)
    publickey = models.CharField("Chave pública", max_length=300, null=True, blank=True)
    super = models.BooleanField("Super usuário", default=False)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.username


class Acl(models.Model):
    READ = 1
    READWRITE = 2
    TIPOS_ACESSO = (
        (READ, 'Leitura'),
        (READWRITE, 'Leitura e gravação'),
    )

    #username = models.CharField("Usuário", max_length=255)
    topic = models.CharField("Tópico", max_length=255)
    rw = models.IntegerField("Tipo de acesso",
                             choices=TIPOS_ACESSO, default=READ)
    username = models.ForeignKey(User,
                                 to_field='username', on_delete=models.PROTECT,
                                 verbose_name='Usuário')

    class Meta:
        verbose_name = 'Regra'
        verbose_name_plural = 'Regras'
