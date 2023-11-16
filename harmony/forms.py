from django import forms
from .models import ConnectWiseConfig

class ConnectWiseConfigForm(forms.ModelForm):
    class Meta:
        model = ConnectWiseConfig
        fields = '__all__'
        widgets = {
            'api_private_key': forms.PasswordInput(attrs={'placeholder': '********'}),
        }