from django.db import models
from decimal import Decimal

# Create your models here.


    
class Product(models.Model):
    name = models.CharField(max_length=100)
    
    product_key = models.CharField(max_length=100) #eg. price_1NTveQKILxTrdOvGfLhJBT3l
    
    def __str__(self):
        return self.name
    
class ProductPrice(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    price_key = models.CharField(max_length=100)
    
    price = models.IntegerField(default=0) #cents (1000 = $10.00)
    credit = models.IntegerField(default=0) #cents
    
    
    type = models.CharField(max_length = 100)
    
    m_or_y=models.CharField(max_length=50, null=True, blank=True) #m for monthly, y for yearly
    
    def get_display_price(self):
        return "{0:2f}".format(self.price / 100)
    
    def get_displayt_credits(self):
        return "{0:2f}".format(self.credit / 100)
    
    def __str__(self):
        return "%s $%s, credits:%s" % (self.product.name, self.price, self.credit)