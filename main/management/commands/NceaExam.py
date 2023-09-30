from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaExam

class Command(BaseCommand) :
    help = 'import booms'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_number', type=int, help='CSV file number to import (e.g., 2 for NceaQUESTION2.csv)')

    def handle(self, *args, **options):
        csv_number = options['csv_number']
        df = pd.read_csv(f'.csv/NceaExam{csv_number}.csv')

        for index, row in df.iterrows():
            NceaExam.objects.update_or_create(
                standard = row['Standard'],
                year = row["Year"],
                exam_name = row["Name"])
            print("updated or created")
