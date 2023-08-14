from django.core.management.base import BaseCommand
import pandas as pd
from payment.models import Product, ProductPrice

class Command(BaseCommand):
    help = 'import booms'
    
    def handle(self, *args, **options):
        try:
            df = pd.read_csv('.csv/ProductPrice.csv')
            for index, row in df.iterrows():
                product_name = row["Product"]
                try:
                    product_instance = Product.objects.get(name=product_name)
                    ProductPrice.objects.update_or_create(
                        
                        name=row["Name"],
                        product=product_instance,
                        price_key=row["PriceKey"],
                        price=row["Price"],
                        credit=row["Credit"],
                        Type=row["Type"],
                        m_or_y=row["m_or_y"],

                        )  
                    self.stdout.write(self.style.SUCCESS(f'Created productprice'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
