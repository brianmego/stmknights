from django.db import models

class CampaignTag(models.Model):
    order = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50, blank=True, null=True)
