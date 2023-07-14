from django.contrib.auth.models import AbstractUser
from django.db import models
from payment.models import Plan
from decimal import Decimal




class CustomUser(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null = True, blank = True)
    credits = models.DecimalField(default=Decimal('0.00'), max_digits=8, decimal_places=2)
    def __str__(self):
        return self.email
    
    