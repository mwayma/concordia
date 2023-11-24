from django.db import models

class DataverseConfig(models.Model):
    environment_url = models.URLField()
    tenant_id = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255,blank=True, null=True)
    def save(self, *args, **kwargs):
        # Remove trailing "/" from environment_url
        self.environment_url = self.environment_url.rstrip('/')
        super().save(*args, **kwargs)
    def __str__(self):
        return self.environment_url

class ConnectWiseConfig(models.Model):
    base_url = models.URLField()
    company_id = models.CharField(max_length=255)
    api_public_key = models.CharField(max_length=255)
    api_private_key = models.CharField(max_length=255,blank=True, null=True)
    sync_company_types = models.ManyToManyField('CompanyType', blank=True)
    sync_company_statuses = models.ManyToManyField('CompanyStatus', blank=True)
    def save(self, *args, **kwargs):
        # Remove trailing "/" from base_url
        self.base_url = self.base_url.rstrip('/')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ConnectWise Configuration for {self.company_id}"
    
    def get_sync_company_types_list(self):
        return list(self.sync_company_types.all())

    def get_sync_company_statuses_list(self):
        return list(self.sync_company_statuses.all())
    
class CompanyType(models.Model):
    connectwise_config = models.ForeignKey(ConnectWiseConfig, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    name = models.CharField(max_length=255)
    vendor_flag = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} (ID: {self.connectwise_manage_id})"

class CompanyStatus(models.Model):
    connectwise_config = models.ForeignKey(ConnectWiseConfig, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} (ID: {self.connectwise_manage_id})"

class CompanyMapping(models.Model):
    connectwise_config = models.ForeignKey(ConnectWiseConfig, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField(blank=True, null=True)
    connectwise_manage_name = models.CharField(max_length=255,blank=True, null=True)
    dynamics365_company_id = models.UUIDField(blank=True, null=True)
    dynamics365_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f"{self.connectwise_manage_name} - ConnectWise ID: {self.connectwise_manage_id} - Dynamics 365 ID: {self.dynamics365_company_id}"

class SiteMapping(models.Model):
    company = models.ForeignKey(CompanyMapping, on_delete=models.CASCADE)
    connectwise_manage_id = models.CharField(max_length=255,blank=True, null=True)
    connectwise_manage_name = models.CharField(max_length=255,blank=True, null=True)
    dynamics365_company_id = models.CharField(max_length=255,blank=True, null=True)
    dynamics365_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f"{self.connectwise_manage_name} - ConnectWise ID: {self.connectwise_manage_id} - Dynamics 365 ID: {self.dynamics365_company_id}"

class SyncMapping(models.Model):
    connectwise_config = models.OneToOneField('ConnectWiseConfig', on_delete=models.CASCADE)
    dataverse_config = models.OneToOneField('DataverseConfig', on_delete=models.CASCADE)

    def __str__(self):
        return f"Mapping between {self.connectwise_config} and {self.dataverse_config}"