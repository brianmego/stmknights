from django.db import models


class Registrant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DegreeRegistration(models.Model):
    attending_council = models.CharField(max_length=100)
    attending_council_num = models.PositiveIntegerField()
    candidates = models.PositiveIntegerField()
    guests = models.PositiveIntegerField()
    medallions = models.PositiveIntegerField()

    def __str__(self):
        return self.attending_council
