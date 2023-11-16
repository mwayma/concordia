from django.contrib import admin
from .models import CompanyType, CompanyStatus, ConnectWiseConfig
from .forms import ConnectWiseConfigForm

class ConnectWiseConfigAdmin(admin.ModelAdmin):
    form = ConnectWiseConfigForm

admin.site.register(ConnectWiseConfig, ConnectWiseConfigAdmin)
admin.site.register(CompanyType)
admin.site.register(CompanyStatus)