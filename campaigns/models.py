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

    def __str__(self):
        return self.name
