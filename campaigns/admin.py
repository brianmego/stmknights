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

class CampaignTagInline(admin.TabularInline):
    model = models.CampaignTag

class CampaignAdmin(admin.ModelAdmin):
    inlines = [
        CampaignTagInline
    ]

admin.site.register(models.DegreeRegistration, DegreeRegistrationAdmin)
admin.site.register(models.Campaign, CampaignAdmin)
admin.site.register(models.Attendee)
admin.site.register(models.Contact)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer)
admin.site.register(models.MerchantAccountId)
# admin.site.register(models.LineItem)  # Don't want to delete sales history!

for campaign in models.Campaign.objects.filter(closed=False):
    admin.site.register_view(
        '{}_aggregate'.format(campaign.lookup_name),
        view=admin_views.aggregate_report,
        name='{} Aggregrate Report'.format(campaign.name)
    )
    admin.site.register_view(
        '{}_detail'.format(campaign.lookup_name),
        view=admin_views.detail_report,
        name='{} Detail Report'.format(campaign.name))
    admin.site.register_view(
        '{}_customer'.format(campaign.lookup_name),
        view=admin_views.customer_report,
        name='{} Customer Report'.format(campaign.name))
