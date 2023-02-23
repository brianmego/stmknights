from django.contrib import admin
from django.contrib.admin.sites import gettext_lazy
import datetime

from ..models import Campaign, LineItem

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

class IsActiveCampaignFilter(admin.SimpleListFilter):
    title = gettext_lazy('Campaign Status')
    parameter_name = 'campaign_active'

    def choices(self, changelist):
        choices = super().choices(changelist)
        next(choices)
        return choices

    def lookups(self, request, model_admin):
        return (
            ('Active', gettext_lazy('Active')),
            ('All', gettext_lazy('All'))
        )

    def queryset(self, request, queryset):
        match self.value():
            case "Active":
                return queryset.filter(campaign__closed=False)
            case "All":
                return queryset
            case None:
                return queryset.filter(campaign__closed=False)

class CampaignFilter(admin.SimpleListFilter):
    title = gettext_lazy('Campaign')
    parameter_name = 'campaign'

    def lookups(self, request, model_admin):
        campaigns = model_admin.get_queryset(request).filter(campaign__closed=False).order_by().values_list('campaign__name', flat=True).distinct()
        return [(x, gettext_lazy(x)) for x in campaigns]
        

    def queryset(self, request, queryset):
        match self.value():
            case None:
                return queryset
            case _:
                return queryset.filter(campaign__name=self.value())

def claim(modeladmin, request, queryset):
    queryset.update(claimed=True)


def unclaim(modeladmin, request, queryset):
    queryset.update(claimed=False)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'customer', 'created_time', 'detail', 'total', 'claimed']
    list_filter = (IsActiveCampaignFilter, HasTotalFilter, UnclaimedFilter, CampaignFilter)
    inlines = [
        LineItemInline
    ]
    actions = [claim, unclaim]
    list_per_page = 10
    search_fields = ('customer__first_name', 'customer__last_name')

    def total(self, obj):
        return obj.get_total()

    def customer(self, obj):
        if obj.customer_set.exists():
            return obj.customer_set.first().full_name
        return None

    def detail(self, obj):
        return obj.get_detail()
