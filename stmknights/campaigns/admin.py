from django.contrib import admin
from .models import Campaign, Registrant


class RegistrantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'campaign')
    fields = ('name', 'email', 'campaign')

admin.site.register(Registrant, RegistrantAdmin)
admin.site.register(Campaign)
