from django.contrib import admin

from manutencao.models import Log

class LogAdmin(admin.ModelAdmin):
    def tempo_mod(self, obj):
        if(obj.tempo):
            return obj.tempo.strftime("%d %b %Y %H:%M:%S")

    readonly_fields = ('tipo', 'mensagem', 'tempo', 'sync',)
    list_display = ('tipo', 'mensagem', 'tempo',)
    ordering = ('-tempo',)
    list_filter = ('tipo', 'tempo',)
    list_per_page = 50

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 0:
            return False
        else:
            return True

admin.site.register(Log, LogAdmin)
