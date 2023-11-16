from django.db import models

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
    
class CompanyType(models.Model):
    connectwise_config = models.ForeignKey(ConnectWiseConfig, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    name = models.CharField(max_length=255)
    vendor_flag = models.BooleanField(default=False)
    sync_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} (ID: {self.connectwise_manage_id})"

class CompanyStatus(models.Model):
    connectwise_config = models.ForeignKey(ConnectWiseConfig, on_delete=models.CASCADE)
    connectwise_manage_id = models.IntegerField()
    name = models.CharField(max_length=255)
    inactive_flag = models.BooleanField(default=False)
    sync_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (ID: {self.connectwise_manage_id})"