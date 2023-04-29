from django.db import models
from django.conf import settings

# Create your models here.

class Plan(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50) #individual or school account.
    monthly_marking = models.IntegerField()
    
    custom_monthly=models.IntegerField()
    
    pricing_monthly = models.IntegerField(default=0)
    pricing_yearly = models.IntegerField()
    
    def __str__(self):
        return self.name
    