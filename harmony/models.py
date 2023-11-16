from django.db import models

# Create your models here.
class ConnectWiseConfig(models.Model):
    base_url = models.URLField()
    company_id = models.CharField(max_length=255)
    api_public_key = models.CharField(max_length=255)
    api_private_key = models.CharField(max_length=255,blank=True, null=True)
    def save(self, *args, **kwargs):
        # Remove trailing "/" from base_url
        self.base_url = self.base_url.rstrip('/')
        super().save(*args, **kwargs)
    def __str__(self):
        return f"ConnectWise Configuration for {self.company_id}"