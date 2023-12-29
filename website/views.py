from django.shortcuts import render
from django.shortcuts import HttpResponse
import pandas as pd 
from website.models import Violation
from datetime import datetime
# Create your views here.

def home(request):
    return render(request, "home.html")

def view_violation(request):
    violations = Violation.objects.all()
    print(violations[0].time)
    context = {'violations':violations}
    return render(request,"view_violations.html",context)


def export_violations(request):
    # Fetch all violations from the database
    violations = Violation.objects.all()

    # Convert queryset to DataFrame
    data = {
        'Violation No.': [violation.violation_id for violation in violations],
        'Violation Date': [violation.date for violation in violations],
        'Time': [violation.time for violation in violations],
        'Bus Panel (English)': [violation.bus_panel for violation in violations],
        'Amount (SAR)': [violation.amount for violation in violations],
        'Violation Type (English)': [violation.violation_type for violation in violations],
        'Violation Type (Arabic)': [violation.violation_type_arabic for violation in violations],
        'PTC ID#': [violation.employee.ptc_id if violation.employee else '' for violation in violations],
    }

    df = pd.DataFrame(data)

    # Create an Excel writer object
    excel_writer = pd.ExcelWriter('violations_export.xlsx', engine='xlsxwriter')
    
    # Write the DataFrame to the Excel file
    df.to_excel(excel_writer, index=False, sheet_name='Violations')

    # Close the Excel writer to save the file
    excel_writer.close()

    # Create a response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=violations_export.xlsx'
    df.to_excel(response, index=False, sheet_name='Violations')

    return response




def add_violations(request):
    if request.method == 'POST':
        file = request.FILES['excelFile']
        df = pd.read_excel(file)
        if "رقم المخالفة" in df.columns:
            pass 
        else:
            df = pd.read_excel(file,header=1)
            print("header on 2nd row")
        
        for index, row in df.iterrows():
            violation_id = str(row['رقم المخالفة'])
            # Check if a Violation with the given violation_id already exists
            if Violation.objects.filter(violation_id=violation_id).exists():
                # If it exists, skip to the next iteration
                continue
            
            print(violation_id)
            violation_date_hijri = row['تاريخ المخالفة بالهجري']
            time_str = row['وقت المخالفة']
            time = datetime.strptime(time_str, '%H:%M').time()
            bus_panel = row['لوحة المركبة']
            amount = row['مبلغ المخالفة']
            violation_type = row['تفاصيل المخالفة بالانجليزي']
            violation_type_arabic = row['تفاصيل المخالفة بالعربي']

            # Create a Violation instance
            violation_instance = Violation(
                violation_id=violation_id,
                violation_date=violation_date_hijri,
                time=time,
                bus_panel=bus_panel,
                Amount=amount,
                Violation_type=violation_type,
                violation_type_arabic=violation_type_arabic,
                # Add other fields as needed
            )
            violation_instance.save()

        print("Data imported successfully")

    return render(request, "add_violations.html")



