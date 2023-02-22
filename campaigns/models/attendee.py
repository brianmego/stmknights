from django.db import models


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
