from django.core.management.base import BaseCommand
import pandas as pd
from main.models import NceaOne, NceaTwo

class Command(BaseCommand):
    help = 'import booms'
    
    def handle(self, *args, **options):
        try:
            df = pd.read_csv('csv/NceaTwo.csv')
            for index, row in df.iterrows():
                standard = row["Standard"]
                year = row["Year"]
                try:
                    ncea_one_instance = NceaOne.objects.get(standard=standard, year=year,)
                    ncea_two_instance = ncea_one_instance.nceatwo_set.create(
                        QUESTION=row["QUESTION"],
                        primary=row["Primary"],
                        secondary=row["Secondary"],
                        achieved=row["Achieved"],
                        merit=row["Merit"],
                        excellence=row["Excellence"])
                    
                    self.stdout.write(self.style.SUCCESS(f'Created NceaTwo instance {ncea_two_instance}'))
                except NceaOne.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f'NceaOne instance with standard={standard}, year={year}, QUESTION={row["QUESTION"]} does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
