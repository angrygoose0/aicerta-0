from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaQUESTIONcalc, NceaQUESTION, NceaSecondaryQuestion, NceaExam

class Command(BaseCommand):
    help = 'import booms'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_number', type=int, help='CSV file number to import (e.g., 2 for NceaQUESTION2.csv)')

    def handle(self, *args, **options):
        try:
            csv_number = options['csv_number']
            df = pd.read_csv(f'.csv/NceaCalc{csv_number}.csv')
            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                QUESTION=row["QUESTION"]
                try:
                    ncea_exam_instance = NceaExam.objects.get(standard=standard, year=year,)
                    ncea_question_instance = NceaQUESTION.objects.get(exam=ncea_exam_instance, QUESTION=QUESTION)
                    NceaQUESTIONcalc.objects.create(
                        QUESTION = ncea_question_instance,
                        type = row["type"],
                        a = row["a"],
                        m = row["m"],
                        e = row["e"],
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Created NceaQUESTIONcalc'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
