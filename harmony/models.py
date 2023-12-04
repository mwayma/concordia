from django.db import models
from django.utils import timezone

class LogType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Log(models.Model):
    type = models.ForeignKey(LogType, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    area = models.CharField(max_length=255)
    message = models.CharField(max_length=255)

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
        return f"{self.base_url} {self.company_id}"
    
    def get_sync_company_types_list(self):
        return list(self.sync_company_types.all())

    def get_sync_company_statuses_list(self):
        return list(self.sync_company_statuses.all())
    
    class Meta:
        unique_together = ('base_url', 'company_id')
    
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

class ConnectWiseCompany(models.Model):
    connectwise_config = models.ForeignKey(ConnectWiseConfig, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    connectwise_manage_name = models.CharField(max_length=255,blank=True, null=True)
    primary_contact = models.ForeignKey('ConnectWiseContact', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.connectwise_manage_name}"

class ConnectWiseSite(models.Model):
    company = models.ForeignKey(ConnectWiseCompany, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    connectwise_manage_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f"{self.connectwise_manage_name} - ConnectWise ID: {self.connectwise_manage_id}"

class ConnectWiseContact(models.Model):
    connectwise_company = models.ForeignKey('ConnectWiseCompany', on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    first_name = models.CharField(max_length=255,blank=True, null=True)
    last_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - ConnectWise ID: {self.connectwise_manage_id}"

class SyncMapping(models.Model):
    name = models.CharField(max_length=255)
    connectwise_config = models.OneToOneField('ConnectWiseConfig', on_delete=models.CASCADE)
    dataverse_config = models.OneToOneField('DataverseConfig', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"
    
class DataverseAccount(models.Model):
    dataverse_config = models.ForeignKey(DataverseConfig, on_delete=models.CASCADE)
    dataverse_id = models.UUIDField()
    dataverse_name = models.CharField(max_length=255, blank=True, null=True)
    primary_contact = models.ForeignKey('DataverseContact', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return f"{self.dataverse_name}"
    
class DataverseContact(models.Model):
    dataverse_account = models.ForeignKey(DataverseAccount, on_delete=models.CASCADE)
    dataverse_id = models.UUIDField()
    first_name = models.CharField(max_length=255,blank=True, null=True)
    last_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Dataverse ID: {self.dataverse_id}"
    
class DataverseCustomerAddress(models.Model):
    dataverse_account = models.ForeignKey(DataverseAccount, on_delete=models.CASCADE)
    dataverse_id = models.UUIDField()
    dataverse_name = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return f"{self.dataverse_name} - Dataverse ID: {self.dataverse_id}"
    
class CompanyMapping(models.Model):
    sync_mapping = models.ForeignKey(SyncMapping, on_delete=models.CASCADE)
    connectwise_company = models.ForeignKey(ConnectWiseCompany, on_delete=models.CASCADE)
    dataverse_account = models.ForeignKey(DataverseAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.connectwise_company.connectwise_manage_id}: {self.connectwise_company.connectwise_manage_name} - {self.dataverse_account.dataverse_name}"
    
class ContactMapping(models.Model):
    sync_mapping = models.ForeignKey(SyncMapping, on_delete=models.CASCADE)
    connectwise_contact = models.ForeignKey(ConnectWiseContact, on_delete=models.CASCADE)
    dataverse_contact = models.ForeignKey(DataverseContact, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.connectwise_contact.connectwise_manage_id}: {self.connectwise_contact.first_name} {self.connectwise_contact.last_name} - {self.dataverse_contact.dataverse_id}"
    
class SiteMapping(models.Model):
    sync_mapping = models.ForeignKey(SyncMapping, on_delete=models.CASCADE)
    connectwise_site = models.ForeignKey(ConnectWiseSite, on_delete=models.CASCADE)
    dataverse_customer_address = models.ForeignKey(DataverseCustomerAddress, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.connectwise_site.connectwise_manage_id}: {self.connectwise_site.connectwise_manage_name} - {self.dataverse_customer_address.dataverse_name}"