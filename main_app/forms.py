from django.forms import ModelForm
from .models import Checking, Travel

class CheckingForm(ModelForm):
    class Meta:
        model = Checking
        fields = ['date']


class TravelForm(ModelForm):
    class Meta:
        model = Travel
        fields = ['image']