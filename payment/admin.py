from django.contrib import admin
from .models import Plan, Product, ProductPrice

# Register your models here.
admin.site.register(Plan)
admin.site.register(Product)
admin.site.register(ProductPrice)