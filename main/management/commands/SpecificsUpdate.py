from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaExam, NceaQUESTION, NceaSecondaryQuestion, Specifics

class Command(BaseCommand):
    help = 'import booms'
    
    def handle(self, *args, **options):
        try:
            df = pd.read_csv('.csv/NceaSpecifics.csv')
            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                QUESTION = row["QUESTION"]
                try:
                    ncea_exam = NceaExam.objects.get(standard=standard, year=year)
                    question = NceaQUESTION.objects.get(exam=ncea_exam, QUESTION=QUESTION)

                    Specifics.objects.update_or_create(
                        nceaQUESTION = question,
                        order = row["order"],
                        type = row["type"],
                        text = row["text"],
                    )
                        
                    self.stdout.write(self.style.SUCCESS(f'Created NCEA schedules'))
                except (NceaExam.DoesNotExist, NceaQUESTION.DoesNotExist):
                    self.stderr.write(self.style.WARNING(f'NceaOne instance with standard={standard}, year={year}, QUESTION={QUESTION} does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
