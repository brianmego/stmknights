from django.db import models
import uuid

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    deferred = models.BooleanField(default=False)
    braintree_id = models.CharField(max_length=25, null=True, blank=True)
    voided = models.BooleanField(default=False)
    claimed = models.BooleanField(default=False)
    extra = models.TextField(null=True, blank=True)

    def get_total(self):
        return sum([x.price_snapshot * x.quantity for x in self.lineitem_set.all()])

    def __str__(self):
        campaign = None
        if self.lineitem_set.first():
            campaign = self.lineitem_set.first().product.campaign
        return '{} - {}'.format(
            campaign,
            self.id
        )

    class Meta:
        ordering = ['-modified_time']


class LineItem(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.PROTECT
    )
    price_snapshot = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return '{} - {} - {}'.format(
            self.product.name,
            self.quantity,
            self.order.modified_time
        )
