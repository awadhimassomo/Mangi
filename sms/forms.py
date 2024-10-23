# forms.py
from django import forms
from .models import NetworkCredit


class CreditForm(forms.ModelForm):
    class Meta:
        model = NetworkCredit
        fields = ['credit', 'network_type']
        widgets = {
            'credit': forms.NumberInput(attrs={
                'placeholder': 'Enter Credit Amount', 
                'min': '1', 
                'step': '1'
            }),
            'network_type': forms.Select(choices=NetworkCredit.NETWORK_CHOICES),
        }