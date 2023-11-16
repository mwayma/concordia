from django import forms
from .models import ConnectWiseConfig

class ConnectWiseConfigForm(forms.ModelForm):
    class Meta:
        model = ConnectWiseConfig
        fields = '__all__'
        widgets = {
            'api_private_key': forms.PasswordInput(attrs={'placeholder': '********'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add checkboxes for sync_company_types and sync_company_statuses
        self.fields['sync_company_types'].widget = forms.CheckboxSelectMultiple()
        self.fields['sync_company_statuses'].widget = forms.CheckboxSelectMultiple()