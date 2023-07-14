from django.db import models
from decimal import Decimal

# Create your models here.

class Plan(models.Model):
    name = models.CharField(max_length=100)
    monthly_price = models.IntegerField(default=0)
    
    monthly_credits = models.DecimalField(default=Decimal('0.00'), max_digits=8, decimal_places=2)

    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name