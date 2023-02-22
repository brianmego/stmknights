from django.db import models


class Product(models.Model):
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    sort_order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    meta_field_one = models.CharField(max_length=100, null=True, blank=True)
    meta_field_two = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
