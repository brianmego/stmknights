from django import forms
from .models import DegreeRegistration


class DegreeRegistrationForm(forms.ModelForm):
    class Meta:
        model = DegreeRegistration
        fields = (
            'attending_council',
            'attending_council_num',
            'medallions',
        )
        labels = {
            "attending_council": "Attending council name",
            "attending_council_num": "Attending council #",
        }
