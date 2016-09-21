from django import forms
from .models import Registrant


class PostForm(forms.ModelForm):
    class Meta:
        model = Registrant
        fields = ('name', 'email', 'campaign',)
