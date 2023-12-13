from django.contrib import admin
from .models import *
from .forms import ConnectWiseConfigForm, DataverseConfigForm
from django.utils import timezone
from .utils import log

class LogAdmin(admin.ModelAdmin):
    def get_local_timestamp(self, obj):
        return obj.timestamp.astimezone(timezone.get_current_timezone())
    get_local_timestamp.short_description = 'Timestamp (Local Time)'
    
    list_display = ['get_local_timestamp', 'type', 'area', 'message']
    list_filter = ['type__name']
    search_fields = ['area', 'message']    

    def has_add_permission(self, request):
        # Disable the ability to add new logs
        return False
    
    def clear_all_logs(self, request, queryset):
        # Clear all logs
        Log.objects.all().delete()

        # Log the action
        log('info', 'Log', f'All logs cleared by {request.user.username}')
    
    clear_all_logs.short_description = "Clear logs (select at least one)"
    actions = ['clear_all_logs']
    def get_actions(self, request):
        # Disable the default delete action
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
class ConnectWiseContactInline(admin.TabularInline):
    model = ConnectWiseContact
    extra = 0

class DataverseContactInline(admin.TabularInline):
    model = DataverseContact
    extra = 0

class ConnectWiseConfigAdmin(admin.ModelAdmin):
    form = ConnectWiseConfigForm

class DataverseConfigAdmin(admin.ModelAdmin):
    form = DataverseConfigForm

class ConnectWiseCompanyAdmin(admin.ModelAdmin):
    list_display = ['connectwise_manage_name', 'connectwise_manage_id']
    list_filter = ['connectwise_config__base_url', 'connectwise_config__company_id']
    search_fields = ['connectwise_manage_name', 'connectwise_manage_id']

    ordering = ['connectwise_manage_name']
    inlines = [ConnectWiseContactInline]

    def clear_all_cmpanies(self, request, queryset):
        # Clear all logs
        ConnectWiseCompany.objects.all().delete()

        # Log the action
        log('info', 'Log', f'All ConnectWise Companies cleared by {request.user.username}')
    
    clear_all_cmpanies.short_description = "Delete all companies (select at least one)"
    actions = ['clear_all_cmpanies']

class DataverseAccountAdmin(admin.ModelAdmin):
    list_display = ['dataverse_name', 'dataverse_id']
    list_filter = ['dataverse_config__environment_url']
    search_fields = ['dataverse_name', 'dataverse_id']

    ordering = ['dataverse_name']
    inlines= [DataverseContactInline]

class CompanyMappingAdmin(admin.ModelAdmin):
    list_display = ['connectwise_company', 'dataverse_account']
    list_filter = ['sync_mapping__name']
    search_fields = ['connectwise_company__connectwise_manage_name', 'dataverse_account__dataverse_name', 'connectwise_company__connectwise_manage_id', 'dataverse_account__dataverse_id']

class ContactMappingAdmin(admin.ModelAdmin):
    list_display = ['connectwise_contact', 'dataverse_contact']
    list_filter = ['sync_mapping__name']
    search_fields = ['connectwise_contact__connectwise_manage_first_name', 'connectwise_contact__connectwise_manage_last_name', 'dataverse_contact__dataverse_first_name', 'dataverse_contact__dataverse_last_name', 'connectwise_contact__connectwise_manage_id', 'dataverse_contact__dataverse_id']

admin.site.register(Log, LogAdmin)
admin.site.register(ConnectWiseConfig, ConnectWiseConfigAdmin)
admin.site.register(ConnectWiseCompany, ConnectWiseCompanyAdmin)
admin.site.register(DataverseConfig, DataverseConfigAdmin)
admin.site.register(ConnectWiseContact)
admin.site.register(SyncMapping)
admin.site.register(DataverseAccount, DataverseAccountAdmin)
admin.site.register(DataverseContact)
admin.site.register(CompanyMapping, CompanyMappingAdmin)
admin.site.register(ContactMapping, ContactMappingAdmin)
admin.site.register(ConnectWiseSite)
admin.site.register(DataverseCustomerAddress)
admin.site.register(SiteMapping)