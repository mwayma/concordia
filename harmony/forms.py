from django import forms
from .models import ConnectWiseConfig, DataverseConfig

class ConnectWiseConfigForm(forms.ModelForm):
    class Meta:
        model = ConnectWiseConfig
        fields = '__all__'
        widgets = {
            'api_private_key': forms.PasswordInput(attrs={'placeholder': '********'}),
            'sync_company_types': forms.CheckboxSelectMultiple(),
            'sync_company_statuses': forms.CheckboxSelectMultiple(),
        }

    def clean_api_private_key(self):
        # Check if the private key is None or an empty string
        api_private_key = self.cleaned_data['api_private_key']

        if api_private_key is None or api_private_key == '':
            # Retrieve the current value from the database
            current_value = ConnectWiseConfig.objects.get(pk=self.instance.pk).api_private_key
            return current_value

        return api_private_key
    
class DataverseConfigForm(forms.ModelForm):
    class Meta:
        model = DataverseConfig
        fields = '__all__'
        widgets = {
            'client_secret': forms.PasswordInput(attrs={'placeholder': '********'}),
        }
    
    def clean_client_secret(self):
        # Check if the private key is None or an empty string
        client_secret = self.cleaned_data['client_secret']

        if client_secret is None or client_secret == '':
            # Retrieve the current value from the database
            current_value = DataverseConfig.objects.get(pk=self.instance.pk).client_secret
            return current_value

        return client_secret