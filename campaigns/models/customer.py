from django.db import models
import uuid

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField()
    order = models.ForeignKey(
        'Order',
        on_delete=models.PROTECT,
        editable=False
    )

    def __str__(self):
        return '{} - {} - {}'.format(
            self.first_name,
            self.last_name,
            self.order.modified_time
        )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
