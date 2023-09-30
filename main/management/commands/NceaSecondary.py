from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaExam, NceaQUESTION, NceaSecondaryQuestion

class Command(BaseCommand):
    help = 'import booms'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_number', type=int, help='CSV file number to import (e.g., 2 for NceaQUESTION2.csv)')

    
    def handle(self, *args, **options):
        try:
            csv_number = options['csv_number']
            df = pd.read_csv(f'.csv/NceaSecondary{csv_number}.csv')

            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                QQ = row["QUESTION"]
                try:
                    ncea_exam = NceaExam.objects.get(standard=standard, year=year)
                    question = NceaQUESTION.objects.get(exam=ncea_exam, QUESTION=QQ)

                    NceaSecondaryQuestion.objects.update_or_create(
                        QUESTION = question,
                        primary = row["Primary"],
                        secondary = row["Secondary"],
                    )
                        
                    self.stdout.write(self.style.SUCCESS(f'Created NCEA SECONDARIES'))
                except (NceaExam.DoesNotExist, NceaQUESTION.DoesNotExist):
                    self.stderr.write(self.style.WARNING(f'NceaOne instance with standard={standard}, year={year}, QUESTION={QQ} does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
