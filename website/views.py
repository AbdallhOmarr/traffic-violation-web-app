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
