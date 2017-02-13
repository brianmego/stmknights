from django.contrib import admin
from . import models, admin_views


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'cost', 'meta_field_one', 'meta_field_two', 'sort_order']
    list_filter = ['campaign']
    search_fields = ['name']
    ordering = ['sort_order']


class AttendeeInline(admin.TabularInline):
    model = models.Attendee


class LineItemInline(admin.TabularInline):
    model = models.LineItem
    readonly_fields = ['product', 'price_snapshot', 'quantity']
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'modified_time', 'total', 'braintree_id', 'voided', 'claimed']
    inlines = [
        LineItemInline
    ]

    def total(self, obj):
        return obj.get_total()


class DegreeRegistrationAdmin(admin.ModelAdmin):
    inlines = [
        AttendeeInline
    ]


admin.site.register(models.DegreeRegistration, DegreeRegistrationAdmin)
admin.site.register(models.Campaign)
admin.site.register(models.Attendee)
admin.site.register(models.Contact)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer)

admin.site.register_view('fish_fry_aggregate_report', view=admin_views.fish_fry_agg_report, name='Lenten Fish Fry Aggregrate Report')
admin.site.register_view('fish_fry_detail_report', view=admin_views.fish_fry_detail_report, name='Lenten Fish Fry Detail Report')
admin.site.register_view('nut_sales_aggregrate_report', view=admin_views.nut_sales_agg_report, name='Nut Sales Aggregate Report')
admin.site.register_view('nut_sales_detail_report', view=admin_views.nut_sales_detail_report, name='Nut Sales Detail Report')
