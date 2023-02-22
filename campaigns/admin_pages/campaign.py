from django.contrib import admin
from ..models.campaign_tag import CampaignTag

class CampaignTagInline(admin.TabularInline):
    model = CampaignTag

class CampaignAdmin(admin.ModelAdmin):
    inlines = [
        CampaignTagInline
    ]
