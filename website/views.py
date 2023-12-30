from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from website.models import Violation, Employee, PDF
from hijri_converter import convert



import pandas as pd 
from datetime import datetime

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('violations')  
    else:
        return render(request,'home.html')  


@login_required(login_url='home')
def view_violation(request):
    violations = Violation.objects.all()
    context = {'violations':violations}
    return render(request,"view_violations.html",context)


@login_required(login_url='home')
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



@login_required(login_url='home')
def add_violations(request):
    if request.method == 'POST' and request.POST.get("excel"):
        try:
            file = request.FILES['excelFile']
            df = pd.read_excel(file)
            if "رقم المخالفة" in df.columns:
                pass 
            else:
                df = pd.read_excel(file,header=1)
                print("header on 2nd row")
            
            for index, row in df.iterrows():
                violation_id = str(row['رقم المخالفة'])
                print(violation_id)
                # Check if a Violation with the given violation_id already exists
                if Violation.objects.filter(violation_id=violation_id).exists():
                    # If it exists, skip to the next iteration
                    continue
                violation_date_hijri = row['تاريخ المخالفة بالهجري']
                year, month, day = map(int, violation_date_hijri.split('-'))

                # Convert to English Georgian date
                violation_georgian_date = convert.Hijri(year=year, month=month, day=day).to_gregorian()

                time_str = row['وقت المخالفة']
                time = datetime.strptime(time_str, '%H:%M').time()
                bus_panel = row['لوحة المركبة']
                amount = row['مبلغ المخالفة']
                violation_type = row['تفاصيل المخالفة بالانجليزي']
                violation_type_arabic = row['تفاصيل المخالفة بالعربي']

                # Create a Violation instance
                violation_instance = Violation(
                    violation_id=violation_id,
                    date=violation_georgian_date,
                    time=time,
                    bus_panel=bus_panel,
                    amount=amount,
                    violation_type=violation_type,
                    violation_type_arabic=violation_type_arabic,
                )
                violation_instance.save()
            context = {'status': 'Success', 'message': 'Adding Violation Successful'}

        except Exception as e:
            context = {'status': 'Failed', 'message': f'Adding violation Failed due to :{e}'}

        return render(request, "add_violations.html",context=context)
    
    elif request.method == 'POST' and request.POST.get("inputbyform"):
        try:
            
            violation_no = request.POST.get('violation_no')
                            # Check if a Violation with the given violation_id already exists
            if Violation.objects.filter(violation_id=violation_no).exists():
                context = {'status': 'Failed', 'message': f'Violation No. Duplicated'}
                return render(request, "add_violations.html",context=context)

            date = request.POST.get("date")
            time = request.POST.get("time")
            bus_plate = request.POST.get("bus_plate")
            amount = request.POST.get("amount")
            violation_type_arabic  = request.POST.get("violation_type_arabic")
            violation_type_english  = request.POST.get("violation_type_eng")
            
            violation_instance = Violation(
                violation_id=violation_no,
                date=date,
                time=time,
                bus_panel=bus_plate,
                amount=amount,
                violation_type=violation_type_english,
                violation_type_arabic=violation_type_arabic,
            )
            violation_instance.save()
            context = {'status': 'Success', 'message': 'Adding Violation Successful'}

        except Exception as e:
            context = {'status': 'Failed', 'message': f'Adding violation Failed due to :{e}'}

        return render(request, "add_violations.html",context=context)

    return render(request, "add_violations.html")



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        print(password)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print('user is not none')
            login(request,user)
            return redirect('violations')  # Change 'dashboard' to your desired redirect URL
        else:
            print("user is none")
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('home')  

@login_required(login_url='home')
def assign_employee(request):
    if request.method =='POST':
        if request.POST.get("table_row"):
            violation_no = request.POST.get('violation_no')
            print(f"violation no:{violation_no}")
            violation = Violation.objects.get(violation_id=violation_no)
            context = {
                    "violation":violation,
                }

            if violation.employee and not violation.pdf:
                return render(request,"assign_document.html",context)
            elif violation.employee and violation.pdf:
                return render(request,"success.html")
            else:
                employees = Employee.objects.all()
                
                employees_ptc = [] 
                for employee in employees:
                    employees_ptc.append(employee.ptc_id)
                context = {
                    "violation":violation,
                    "employees_ptc":employees_ptc
                }
                return render(request,"assign_employee.html",context)

        else:
            if request.POST.get("pdf"):
                violation_no = request.POST.get('violation_no')    
                violation = Violation.objects.get(violation_id=violation_no)
                pdf_file = request.FILES['pdfFile']
                pdf = PDF.objects.create(file=pdf_file)
                violation.pdf = pdf
                violation.save()
                return redirect("violations")

            else:
                violation_no = request.POST.get('violation_no')     
                print(violation_no)

                ptc_id = request.POST.get("employee_ptc")
                print(f"ptc id:{ptc_id}")
                # get violation from Violation
                violation = Violation.objects.get(violation_id=violation_no)
                
                employee = Employee.objects.get(ptc_id=ptc_id)
                
                violation.employee = employee
                violation.save()
                return redirect("violations")
        
    
    return redirect("violations")
