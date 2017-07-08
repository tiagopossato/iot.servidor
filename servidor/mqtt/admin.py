from django.contrib import admin

from mqtt.models import User
from mqtt.models import Acl

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','pw','super',)
    #readonly_fields = ('',)
    ordering = ('username',)
    list_filter = ('username',)

class AclAdmin(admin.ModelAdmin):
    list_display = ('username','topic','rw',)
    #readonly_fields = ('',)
    ordering = ('username','topic','rw',)
    list_filter = ('username','topic','rw')

admin.site.register(User, UserAdmin)
admin.site.register(Acl, AclAdmin)