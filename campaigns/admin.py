from django.contrib import admin
from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'cost')
    list_filter = ('campaign',)
    search_fields = ('name',)


class AttendeeInline(admin.TabularInline):
    model = models.Attendee


class DegreeRegistrationAdmin(admin.ModelAdmin):
    inlines = [
        AttendeeInline
    ]

admin.site.register(models.DegreeRegistration, DegreeRegistrationAdmin)
admin.site.register(models.Campaign)
admin.site.register(models.Attendee)
admin.site.register(models.Contact)
admin.site.register(models.Product, ProductAdmin)
