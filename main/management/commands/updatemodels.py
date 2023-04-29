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
                year = row["year"],
                QUESTION = row["QUESTION"],
                n0 = row["n0"],
                a1 = row["n1"],
                n2 = row["n2"],
                a3 = row["a3"],
                a4 = row["a4"],
                m5 = row["m5"],
                m6 = row["m6"],
                e7 = row["e7"],
                e8 = row["e8"]
            )
            t.save()
            
            
            