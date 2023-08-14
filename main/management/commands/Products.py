from django.core.management.base import BaseCommand
import pandas as pd
from payment.models import Product

class Command(BaseCommand) :
    help = 'import booms'
    
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        df = pd.read_csv('.csv/Products.csv')
        for index, row in df.iterrows():
            Product.objects.update_or_create(
                name = row['Name'],
                product_key = row["ProductKey"],
                )
            print("updated or created")