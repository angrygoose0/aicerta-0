from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaExam, NceaQUESTION, NceaSecondaryQuestion, AssesmentSchedule, Criteria

class Command(BaseCommand):
    help = 'import booms'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_number', type=int, help='CSV file number to import (e.g., 2 for NceaQUESTION2.csv)')

    
    def handle(self, *args, **options):
        try:
            csv_number = options['csv_number']
            df = pd.read_csv(f'.csv/Criteria{csv_number}.csv')

            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                
                exam = NceaExam.objects.get(standard=standard, year=year)
                secondary = str(row["Secondary"])
                
                text = row["Text"]
                type = row["Type"]
                image = row["Image"]
                
                criteria = Criteria.objects.create(text=text, type=type, image=image)
                
                numbers = secondary.split("|")

                if len(numbers) == 1:
                    # If there's only one number, assign it to a variable
                    num = str(numbers[0])
                    digits = [int(char) for char in num]
                    a, b, c = digits
                    QUESTION = NceaQUESTION.objects.get(exam=exam, QUESTION=a)
                    secondary_question = NceaSecondaryQuestion.objects.get(QUESTION=QUESTION, primary=b, secondary=c)
                    
                    criteria.secondary_questions.add(secondary_question)
                else:
                    # If there's more than one number, loop through the list
                    for num in numbers:
                        num = str(numbers[0])
                        digits = [int(char) for char in num]
                        a, b, c = digits
                        QUESTION = NceaQUESTION.objects.get(exam=exam, QUESTION=a)
                        secondary_question = NceaSecondaryQuestion.objects.get(QUESTION=QUESTION, primary=b, secondary=c)
                        
                        criteria.secondary_questions.add(secondary_question)
                print("goodjob")

                            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
