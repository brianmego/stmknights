import uuid
from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class DegreeRegistration(models.Model):
    attending_council = models.CharField(max_length=100)
    attending_council_num = models.PositiveIntegerField()
    medallions = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()

    def __str__(self):
        return self.attending_council


class Attendee(models.Model):
    name = models.CharField(max_length=100, blank=False)
    attendee_type = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE
    )
    degree_registration = models.ForeignKey(
        'DegreeRegistration',
        related_name="attendees",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    contact = models.ManyToManyField(Contact)

    def __str__(self):
        return self.name


class Product(models.Model):
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    meta_field_one = models.CharField(max_length=100, null=True, blank=True)
    meta_field_two = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


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


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    braintree_id = models.CharField(max_length=25, null=True, blank=True)
    voided = models.BooleanField(default=False)

    def get_total(self):
        return sum([x.price_snapshot * x.quantity for x in self.lineitem_set.all()])

    def __str__(self):
        campaign = self.lineitem_set.first().product.campaign
        return '{} - {}'.format(
            campaign,
            self.id
        )

    class Meta:
        ordering = ['-modified_time']


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
