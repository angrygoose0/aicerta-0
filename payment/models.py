from django.db import models
from decimal import Decimal

# Create your models here.

class Plan(models.Model):
    name = models.CharField(max_length=100)
    monthly_price = models.IntegerField(default=0)
    
    monthly_credits = models.IntegerField(default=0) #cents

    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def get_display_price(self):
        return "{0:2f}".format(self.monthly_price / 100)
    
    def get_displayt_credits(self):
        return "{0:2f}".format(self.monthly_credits / 100)
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    
    product_key = models.CharField(max_length=100) #eg. price_1NTveQKILxTrdOvGfLhJBT3l
    
    def __str__(self):
        return self.name
    
class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    price_key = models.CharField(max_length=100)
    
    def __str__(self):
        return "%s price" % self.product.name