from django.contrib.auth.models import AbstractUser
from django.db import models
from plans.models import Plan


def get_default_plan():
    try:
        default_plan = Plan.objects.get(name="Basic")
        return default_plan.pk
    except Plan.DoesNotExist:
        # Handle the case when the "Basic" plan does not exist, e.g., create it
        default_plan = Plan.objects.create(name="Basic", type="Individual", monthly_marking=9, custom_monthly=0, pricing_monthly=10, pricing_yearly=7)
        return default_plan.pk


class CustomUser(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default=get_default_plan, null=True)
    
    def __str__(self):
        return self.email
    
    