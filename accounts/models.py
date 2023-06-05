from django.contrib.auth.models import AbstractUser
from django.db import models
from payment.models import Plan




class CustomUser(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.email
    
    