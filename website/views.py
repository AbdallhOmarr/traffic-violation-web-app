from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from website.models import Violation, Employee, PDF , Vehicle
from hijri_converter import convert


import json 
import pandas as pd 
from datetime import datetime

from docxtpl import InlineImage
from docxtpl import DocxTemplate


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('violations')  
    else:
        return render(request,'home.html')  

def simple_search(lst,req_item):
    for item in lst:
        if item.plate_ar == req_item:
            return item 
    return None


@login_required(login_url='home')
def view_violation(request):
    violations = Violation.objects.all()
    employees = Employee.objects.all()
    vehicles = Vehicle.objects.all()
    employees_ptc = [] 
    for employee in employees:
        employees_ptc.append(employee.ptc_id)
    
    
    merged_data= []
    for violation in violations:
        plate_ar = violation.bus_plate # check if its arabic? 
        vehicle= Vehicle.objects.get(plate_ar = plate_ar)
            
        violation_dict = model_to_dict(violation)
        vehicle_dict = model_to_dict(vehicle)
        if violation.employee:
            employee_dict = model_to_dict(violation.employee)
        else:
            employee_dict = {
                "ptc_id":"",
                "ID_number":None,
                "employee_name":None
            }
        if vehicle:
            merged_data.append({**violation_dict, **vehicle_dict,**employee_dict})        
        
    context = {
        "violations":merged_data,
        "employees_ptc":employees_ptc
    }
    
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
        'Bus Plate': [violation.bus_plate for violation in violations],
        'Fleet no': [Vehicle.objects.get(plate_ar = violation.bus_plate).fleet_no for violation in violations],
        'vehicle user': [Vehicle.objects.get(plate_ar = violation.bus_plate).vehicle_user for violation in violations],
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
                bus_plate = row['لوحة المركبة']
                amount = row['مبلغ المخالفة']
                violation_type = row['تفاصيل المخالفة بالانجليزي']
                violation_type_arabic = row['تفاصيل المخالفة بالعربي']

                print(f"bus plate:{bus_plate}")
                # Create a Violation instance
                vehicle = Vehicle.objects.get(plate_ar=bus_plate)

                print(f"vehicle:{vehicle}")
                
                if vehicle:
                    violation_instance = Violation(
                    violation_id=violation_id,
                    date=violation_georgian_date,
                    time=time,
                    bus_plate=bus_plate,
                    amount=amount,
                    violation_type=violation_type,
                    violation_type_arabic=violation_type_arabic,
                    )

                    violation_instance.save()
                else:
                    vehicle = Vehicle.objects.get(plate_ar=bus_plate)
                    if vehicle:
                        violation_instance = Violation(
                        violation_id=violation_id,
                        date=violation_georgian_date,
                        time=time,
                        bus_plate=vehicle.plate_ar,
                        amount=amount,
                        violation_type=violation_type,
                        violation_type_arabic=violation_type_arabic,
                        )
                        violation_instance.save()
                    else:
                        context = {'status': 'Failed', 'message': f"Plate no. doesn't belong to our fleet, please add vehicle to fleet!"}
            context = {'status': 'Success', 'message': 'Violation Added Successfully'}

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
            

            # Create a Violation instance
            # vehicle = Vehicle.objects.get(plate_ar=bus_plate)
            vehicle = True

            print(f"vehicle:{vehicle}")
            
            if True:
                violation_instance = Violation(
                violation_id=violation_no,
                date=date,
                time=time,
                bus_plate=bus_plate,
                amount=amount,
                violation_type=violation_type_english,
                violation_type_arabic=violation_type_arabic,
                )

                violation_instance.save()
                context = {'status': 'Success', 'message': 'Violation Added Successfully'}

            else:
                # vehicle = Vehicle.objects.get(plate_eng=bus_plate)
                vehicle = True
                if vehicle:
                    violation_instance = Violation(
                    violation_id=violation_id,
                    date=violation_georgian_date,
                    time=time,
                    bus_plate=vehicle.plate_ar,
                    amount=amount,
                    violation_type=violation_type,
                    violation_type_arabic=violation_type_arabic,
                    )
                    violation_instance.save()
                    context = {'status': 'Success', 'message': 'Violation Added Successfully'}

                else:
                    context = {'status': 'Failed', 'message': f"Plate no. doesn't belong to our fleet, please add vehicle to fleet!"}



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
    context = {'status': 'Failed', 'message': 'not post req'}

    if request.method =='POST' and not request.POST.get("pdf"):
        json_data = json.loads(request.body.decode('utf-8'))

        # Access the data using keys
        ptc_id = json_data.get("ptc_id")
        violation_no = json_data.get("violation_id")
        try:
            violation = Violation.objects.get(violation_id=violation_no)
            if violation.employee:
                context = {'status': 'Failed', 'message': f'an employee has been assigned before'}
                return JsonResponse(context)

            employee = Employee.objects.get(ptc_id=ptc_id)
            violation.employee = employee
            violation.save()
    
            context = {'status': 'Success', 'message': 'Violation Updated Successfully'}
    
        except Exception as e:
            context = {'status': 'Failed', 'message': f'Updating violation Failed due to :{e}'}
    
    
    elif request.method=='POST' and request.POST.get("pdf"):
        print("pdf")
        try:
            violation_no = request.POST.get('violation_no')    
            print(violation_no)
            violation = Violation.objects.get(violation_id=violation_no)
            
            if violation.pdf:
                context = {'status': 'Failed', 'message': f'PDF document has been assigned before'}
                return JsonResponse(context)

            pdf_file = request.FILES['pdfFile']
            pdf = PDF.objects.create(file=pdf_file)
            violation.pdf = pdf
            violation.save()
            context = {'status': 'Success', 'message': 'Violation Updated Successfully'}
        except Exception as e:
            context = {'status': 'Failed', 'message': f'Updating violation Failed due to :{e}'}

    return JsonResponse(context)



@login_required(login_url='home')
def get_employee(request):
    if request.method =="POST":
        # Parse the JSON data from the request
        json_data = json.loads(request.body.decode('utf-8'))

        # Access the data using keys
        ptc_id = json_data.get("ptc_id")
        
        employee = Employee.objects.get(ptc_id=ptc_id)
        data= {
            "ptc_id":employee.ptc_id,
            "employee_name":employee.employee_name,
            "ID_number":employee.ID_number
               }
        return JsonResponse(data)
    
    
    
## printing document with request value

@login_required(login_url='home')
def print_document(request):
    if request.method == 'POST':
        #request data
        # Retrieve JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        violation_no = data.get('violation_no')        #get violation from db
        violation = Violation.objects.get(violation_id=violation_no)
        vehicle = Vehicle.objects.get(plate_ar=violation.bus_plate)

        print(vehicle)        
        #employee data
        employee = violation.employee
        context = {
            "violation_no":violation.violation_id,
            "date":violation.date,
            "time":violation.time,
            "amount":violation.amount,
            "violation_type_eng":violation.violation_type,
            "violation_type_araic":violation.violation_type_arabic,
            
            "employee_name":employee.employee_name,
            "ptc_id":employee.ptc_id,
            "id_number":employee.ID_number,
            
            "vehicle_type":vehicle.vehicle_type,
            "plate_no":vehicle.plate_eng
        }
        document_path = "document.docx"
        doc = DocxTemplate(document_path)
        doc.render(context)
        
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename={violation_no}_violation_report.docx'
        doc.save(response)

        return response
        

        
    