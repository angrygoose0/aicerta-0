from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaExam

class Command(BaseCommand) :
    help = 'import booms'
    
    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        df = pd.read_csv('.csv/NceaExam.csv')
        for index, row in df.iterrows():
            NceaExam.objects.update_or_create(
                standard = row['Standard'],
                year = row["Year"],
                exam_name = row["Name"])
            print("updated or created")
