from django.contrib import admin
from .models import  Product, ProductPrice

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductPrice)