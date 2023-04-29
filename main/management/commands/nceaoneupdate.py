from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaOne

class Command(BaseCommand) :
    help = 'import booms'
    
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        df = pd.read_csv('csv/NceaOne.csv')
        for index, row in df.iterrows():
            t=NceaOne(
                standard = row['Standard'],
                year = row["year"],)
            t.save()
            