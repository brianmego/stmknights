from django.contrib import admin
from .models import Attendee, AttendeeType, Campaign, DegreeRegistration, Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'cost')
    list_filter = ('campaign',)
    search_fields = ('name',)


admin.site.register(DegreeRegistration)
admin.site.register(Campaign)
admin.site.register(Attendee)
admin.site.register(AttendeeType)
admin.site.register(Product, ProductAdmin)
