from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaExam, NceaQUESTION, NceaSecondaryQuestion, AssesmentSchedule

class Command(BaseCommand):
    help = 'import booms'
    
    def handle(self, *args, **options):
        try:
            df = pd.read_csv('.csv/AssesmentSchedule.csv')
            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                QQ = row["QUESTION"]
                primary = row["Primary"]
                secondary = row["Secondary"]
                try:
                    ncea_exam = NceaExam.objects.get(standard=standard, year=year)
                    question = NceaQUESTION.objects.get(exam=ncea_exam, QUESTION=QQ)
                    type = row["type"]
                    
                    if type == "n":
                        secondary_question = NceaSecondaryQuestion.objects.get(QUESTION=question, primary=primary, secondary=secondary)
                    else:
                        secondary_question = None
                    AssesmentSchedule.objects.update_or_create(
                        QUESTION = question,
                        secondary_question = secondary_question,
                        text = row["text"],
                        order = row["order"],
                        type = row["type"],
                    )
                        
                    self.stdout.write(self.style.SUCCESS(f'Created NCEA Assesment Schedules'))
                except (NceaExam.DoesNotExist, NceaQUESTION.DoesNotExist):
                    self.stderr.write(self.style.WARNING(f'NceaOne instance with standard={standard}, year={year}, QUESTION={QQ} does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
