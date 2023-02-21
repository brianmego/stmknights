from django.contrib import admin
from .. import models

class CampaignTagInline(admin.TabularInline):
    model = models.CampaignTag

class CampaignAdmin(admin.ModelAdmin):
    inlines = [
        CampaignTagInline
    ]
