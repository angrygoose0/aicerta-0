from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaQUESTION, NceaSecondaryQuestion, NceaExam

class Command(BaseCommand):
    help = 'import booms'
    
    def handle(self, *args, **options):
        try:
            df = pd.read_csv('csv/NceaQUESTION.csv')
            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                try:
                    ncea_exam_instance = NceaExam.objects.get(standard=standard, year=year,)
                    NceaQUESTION.objects.update_or_create(
                        exam=ncea_exam_instance,
                        QUESTION=row["QUESTION"],
                        system=row["system"],
                        n0 = row["n0"],
                        n1 = row["n1"],
                        n2 = row["n2"],
                        a3 = row["a3"],
                        a4 = row["a4"],
                        m5 = row["m5"],
                        m6 = row["m6"],
                        e7 = row["e7"],
                        e8 = row["e8"],
                        )  
                    self.stdout.write(self.style.SUCCESS(f'Created NceaQUESTION'))
                except NceaExam.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f'NceaExam instance with standard={standard}, year={year}, does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
