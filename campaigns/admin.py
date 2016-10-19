from django.contrib import admin
from . import models


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'cost', 'meta_field_one', 'meta_field_two')
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
