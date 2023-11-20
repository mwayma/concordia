from django.contrib import admin
from .models import ConnectWiseConfig, CompanyMapping, SiteMapping
from .forms import ConnectWiseConfigForm

class SiteMappingInline(admin.TabularInline):  # You can also use admin.StackedInline
    model = SiteMapping
    extra = 0  # Show all existing SiteMapping objects

class ConnectWiseConfigAdmin(admin.ModelAdmin):
    form = ConnectWiseConfigForm

class CompanyMappingAdmin(admin.ModelAdmin):
    list_display = ['connectwise_manage_name', 'connectwise_manage_id', 'dynamics365_company_id', 'dynamics365_name']
    list_filter = ['connectwise_config']
    search_fields = ['connectwise_manage_name', 'connectwise_manage_id', 'dynamics365_company_id', 'dynamics365_name']

    ordering = ['connectwise_manage_name']  # Sort alphabetically by connectwise_manage_name
    inlines = [SiteMappingInline]
   
admin.site.register(ConnectWiseConfig, ConnectWiseConfigAdmin)
admin.site.register(CompanyMapping, CompanyMappingAdmin)
admin.site.register(SiteMapping)