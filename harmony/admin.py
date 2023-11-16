from django.contrib import admin
from .models import ConnectWiseConfig
from .forms import ConnectWiseConfigForm

# Register your models here.
class ConnectWiseConfigAdmin(admin.ModelAdmin):
    form = ConnectWiseConfigForm

    def save_model(self, request, obj, form, change):
        # Check if the private key is None or an empty string
        if obj.api_private_key is None or obj.api_private_key == '':
            # Retrieve the current value from the database
            current_value = ConnectWiseConfig.objects.get(pk=obj.pk).api_private_key
            obj.api_private_key = current_value
        super().save_model(request, obj, form, change)


admin.site.register(ConnectWiseConfig, ConnectWiseConfigAdmin)