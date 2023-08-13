from django.contrib.auth.models import AbstractUser
from django.db import models
from payment.models import ProductPrice
from decimal import Decimal




class CustomUser(AbstractUser):
    plan = models.ForeignKey(ProductPrice, on_delete=models.SET_NULL, null = True, blank = True)
    credits = models.IntegerField(default=0) #cents
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.email
    
    def get_display_credits(self):
        return "{0:2f}".format(self.credits / 100)