from django.db import models
from .contact import Contact


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    lookup_name = models.CharField(max_length=100, default='')
    merchant_account_id = models.ForeignKey(
        'MerchantAccountId',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="campaigns"
    )
    reporting_start = models.DateField()
    template_name = models.CharField(max_length=100, default='generic_sales')
    header = models.CharField(max_length=100, null=True, blank=True)
    where = models.TextField(null=True, blank=True)
    when = models.TextField(null=True, blank=True)
    closed = models.BooleanField(default=False)
    closed_message = models.TextField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    contact = models.ManyToManyField(Contact)
    test_mode = models.BooleanField(default=False)
    columns = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name
