from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaQUESTION, NceaSecondaryQuestion, NceaExam

class Command(BaseCommand):
    help = 'import booms'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_number', type=int, help='CSV file number to import (e.g., 2 for NceaQUESTION2.csv)')

    def handle(self, *args, **options):
        try:
            csv_number = options['csv_number']
            df = pd.read_csv(f'.csv/NceaQUESTION{csv_number}.csv')
            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                try:
                    ncea_exam_instance = NceaExam.objects.get(standard=standard, year=year,)
                    NceaQUESTION.objects.update_or_create(
                        exam=ncea_exam_instance,
                        QUESTION=row["QUESTION"],
                        )  
                    self.stdout.write(self.style.SUCCESS(f'Created NceaQUESTION'))
                except NceaExam.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f'NceaExam instance with standard={standard}, year={year}, does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
