from django.contrib import admin
from django.db.utils import OperationalError

from . import admin_views, models
from .admin_pages.order import OrderAdmin
from .admin_pages.campaign import CampaignAdmin
from .admin_pages.degree import DegreeRegistrationAdmin
from .admin_pages.product import ProductAdmin

admin.site.site_header = 'STM Knights Admin Page'
admin.site.site_title = 'STM Knights Admin Page'
admin.site.enable_nav_sidebar = False

admin.site.register(models.DegreeRegistration, DegreeRegistrationAdmin)
admin.site.register(models.Campaign, CampaignAdmin)
admin.site.register(models.Attendee)
admin.site.register(models.Contact)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer)
admin.site.register(models.MerchantAccountId)
# admin.site.register(models.LineItem)  # Don't want to delete sales history!

try:
    campaign_list = [x for x in models.Campaign.objects.filter(closed=False)]
except OperationalError:
    campaign_list = []

for campaign in campaign_list:
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
        '{}_detailByLastName'.format(campaign.lookup_name),
        view=admin_views.detail_report_by_name,
        name='{} Detail Report By Last Name'.format(campaign.name))
    admin.site.register_view(
        '{}_customer'.format(campaign.lookup_name),
        view=admin_views.customer_report,
        name='{} Customer Report'.format(campaign.name))
