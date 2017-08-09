from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from sentinela.models import User, TelefoneUsuario, EnderecoUsuario
from sentinela.models import Empresa, EnderecoEmpresa, TelefoneEmpresa
from sentinela.models import Central
from sentinela.models import Certificado
from sentinela.models import Grandeza, Alarme, Leitura

class TelefoneEmpresaInline(admin.StackedInline):
    model = TelefoneEmpresa
    can_delete = True
    verbose_name_plural = 'Telefone'
    extra = 0

class EnderecoEmpresaInline(admin.StackedInline):
    model = EnderecoEmpresa
    can_delete = True
    verbose_name_plural = 'Endereço'
    extra = 0
    max_num = 1

class EmpresaAdmin(admin.ModelAdmin):
     inlines = (TelefoneEmpresaInline,EnderecoEmpresaInline,)

class TelefoneUsuarioInline(admin.StackedInline):
    model = TelefoneUsuario
    can_delete = True
    verbose_name_plural = 'Telefone'
    extra = 0

class EnderecoUsuarioInline(admin.StackedInline):
    model = EnderecoUsuario
    can_delete = True
    verbose_name_plural = 'Endereço'
    extra = 0
    max_num = 1

class UserAdmin(BaseUserAdmin):
    inlines = (TelefoneUsuarioInline, EnderecoUsuarioInline,)

class CentralAdmin(admin.ModelAdmin):
    list_display = ('descricao','id','certificado','is_active',)
    readonly_fields = ('id','created_at','certificado',)    

class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('certName','clientName', 'is_revoked','created_at','updated_at',)
    readonly_fields = ('certName','is_revoked','clientName','created_at',)
    list_filter = ('is_revoked',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if(obj and obj.is_revoked):
            return True
        else:
            return False

class AlarmeAdmin(admin.ModelAdmin):
    def tempoAtivacao_mod(self, obj):
        if(obj.tempoAtivacao):
            return obj.tempoAtivacao.strftime("%d %b %Y %H:%M:%S")

    def tempoInativacao_mod(self, obj):
        if(obj.tempoInativacao):
            return obj.tempoInativacao.strftime("%d %b %Y %H:%M:%S")

    readonly_fields = ('uid','codigoAlarme', 'ativo','reconhecido', 'mensagemAlarme',
                     'prioridadeAlarme','central', 'ambiente', 'grandeza', 'tempoAtivacao','tempoInativacao',)
    list_display = ('mensagemAlarme', 'ativo', 'reconhecido', 'prioridadeAlarme',
                    'ambiente', 'grandeza', 'tempoAtivacao_mod', 'tempoInativacao_mod',)
    list_filter = ('ativo','reconhecido', 'tempoAtivacao', 'ambiente','grandeza', 'mensagemAlarme',)
    ordering = ('-ativo', '-reconhecido','-tempoAtivacao',)
    # list_per_page = EntradaDigital.objects.count() + AlarmeAnalogico.objects.count()

    def has_add_permission(self, request):
        return False

class GrandezaAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','updated_at',)
    list_display = ('nome', 'unidade', 'codigo',)
    ordering = ('codigo',)

class LeituraAdmin(admin.ModelAdmin):
    list_display = ('ambiente','sensor','grandeza','valor', 'created_at',)
    readonly_fields = ('ambiente','sensor','grandeza','valor', 'central', 'created_at',)
    list_filter = ('ambiente','sensor', 'grandeza', 'central',)
    ordering = ('-created_at', '-sensor','-grandeza',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(User, UserAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Central, CentralAdmin)
admin.site.register(Certificado, CertificadoAdmin)
admin.site.register(Alarme, AlarmeAdmin)
admin.site.register(Grandeza, GrandezaAdmin)
admin.site.register(Leitura, LeituraAdmin)