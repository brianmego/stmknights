from django.db import models

class DegreeRegistration(models.Model):
    attending_council = models.CharField(max_length=100)
    attending_council_num = models.PositiveIntegerField()
    medallions = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()

    def __str__(self):
        return self.attending_council
