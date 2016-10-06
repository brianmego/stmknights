from django import forms
from .models import DegreeRegistration


class DegreeRegistrationForm(forms.ModelForm):
    class Meta:
        model = DegreeRegistration
        fields = (
            'attending_council',
            'attending_council_num',
            'candidates',
            'guests',
            'medallions',
        )
