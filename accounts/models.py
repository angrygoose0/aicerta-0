from django.contrib.auth.models import AbstractUser
from django.db import models
from plans.models import Plan


def get_default_plan():
    default_plan = Plan.objects.get(name="Basic")
    return default_plan.pk

class CustomUser(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default=get_default_plan, null=True)
    
    def __str__(self):
        return self.email
    
    