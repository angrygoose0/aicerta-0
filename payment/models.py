from django.db import models

# Create your models here.

class Plan(models.Model):
    name = models.CharField(max_length=100)
    monthly_price = models.IntegerField(default=0)
    
    marks_per_day = models.IntegerField

    
    
    def __str__(self):
        return self.name