from django import forms
from .models import ConnectWiseConfig

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