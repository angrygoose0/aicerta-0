from django.contrib.auth.models import AbstractUser
from django.db import models
from payment.models import Plan
from decimal import Decimal




class CustomUser(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null = True, blank = True)
    credits = models.IntegerField(default=0) #cents
    def __str__(self):
        return self.email
    
    def get_display_credits(self):
        return "{0:2f}".format(self.credits / 100)