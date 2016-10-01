from django import forms
from .models import DegreeRegistration, Registrant


class PostForm(forms.ModelForm):
    class Meta:
        model = Registrant
        fields = ('name', 'email', 'campaign',)


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
