from django.contrib import admin
from django.contrib.admin.sites import gettext_lazy
import datetime

from ..models import LineItem

class LineItemInline(admin.TabularInline):
    model = LineItem
    readonly_fields = ['product', 'price_snapshot', 'quantity']
    can_delete = False


class HasTotalFilter(admin.SimpleListFilter):
    title = gettext_lazy('Transaction Status')

    parameter_name = 'complete_transaction'

    def lookups(self, request, model_admin):
        return (
            ('Partial', gettext_lazy('Partial')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Partial':
            return queryset.filter(braintree_id=None)
        return queryset.exclude(braintree_id=None)

class UnclaimedFilter(admin.SimpleListFilter):
    title = gettext_lazy('Claimed Status')
    parameter_name = 'unclaimed_filter'

    def lookups(self, request, model_admin):
        return (
            ('Claimed', gettext_lazy('Claimed')),
            ('Unclaimed', gettext_lazy('Unclaimed')),
        )

    def queryset(self, request, queryset):
        match self.value():
            case "Claimed":
                return queryset.filter(claimed=True)
            case "Unclaimed":
                return queryset.filter(claimed=False)
            case _:
                return queryset

class AfterStartDate(admin.SimpleListFilter):
    title = gettext_lazy('After Start Date')
    parameter_name = 'after_start_date'

    def lookups(self, request, model_admin):
        return (
            ('AfterStartDate', gettext_lazy('After Start Date')),
        )

    def queryset(self, request, queryset):
        match self.value():
            case "AfterStartDate":
                return queryset.filter(modified_time__gte=datetime.date.today())
            case _:
                return queryset

class CampaignFilter(admin.SimpleListFilter):
    title = gettext_lazy('Campaign')
    parameter_name = 'campaign'

    def lookups(self, request, model_admin):
        campaigns = [(x.name, gettext_lazy(x.name)) for x in models.Campaign.objects.all()]
        return campaigns
        

    def queryset(self, request, queryset):
        match self.value():
            case "All":
                return queryset
            case _:
                return queryset.filter(campaign__name=self.value())

def claim(modeladmin, request, queryset):
    queryset.update(claimed=True)


def unclaim(modeladmin, request, queryset):
    queryset.update(claimed=False)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'modified_time', 'total', 'braintree_id', 'claimed', 'voided', 'deferred']
    list_filter = (HasTotalFilter, UnclaimedFilter, AfterStartDate)
    inlines = [
        LineItemInline
    ]
    actions = [claim, unclaim]

    def total(self, obj):
        return obj.get_total()

    def customer(self, obj):
        if obj.customer_set.exists():
            return obj.customer_set.first().full_name
        return None
