from django.core.management.base import BaseCommand, CommandError
from website.models import Violation_Type
import pandas as pd

class Command(BaseCommand):
    help = "Upload violations from Excel file"

    def handle(self, *args, **options):
        excel_file_path = r"E:\Repository\traffic violation web app\project_data\Violation list.xlsx"  # Change this to the actual path of your Excel file

        try:
            df = pd.read_excel(excel_file_path)
        except FileNotFoundError:
            raise CommandError(f"Excel file not found at {excel_file_path}")

        for index, row in df.iterrows():
            violation_data = {
                "violation_en": row["English violation"],
                "violation_ar": row["المخالفة بالعربية"],
                "violation_cost": row["Amount"],
            }

            try:
                violation = Violation_Type.objects.get(violation_en=violation_data["violation_en"])
            except Violation_Type.DoesNotExist:
                # Create a new instance if the violation does not exist
                violation = Violation_Type(**violation_data)
                violation.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully added violation "{violation.violation_en}"'))
            else:
                # Update the existing instance if it already exists
                violation.violation_ar = violation_data["violation_ar"]
                violation.violation_cost = violation_data["violation_cost"]
                violation.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated violation "{violation.violation_en}"'))
