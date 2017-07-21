from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from sentinela.models import User, TelefoneUsuario, EnderecoUsuario
from sentinela.models import Empresa, EnderecoEmpresa, TelefoneEmpresa
from sentinela.models import Central
from sentinela.models import Certificado
    
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
    list_display = ('nome','id',)
    readonly_fields = ('id','created_at',)

class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('certName','is_revoked',)
    readonly_fields = ('certName','keyName','created_at',)
    
admin.site.register(User, UserAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Central, CentralAdmin)
admin.site.register(Certificado, CertificadoAdmin)