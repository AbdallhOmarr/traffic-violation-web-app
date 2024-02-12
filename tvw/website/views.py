from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from website.models import Violation, Employee, PDF , Vehicle, Violation_Type
from hijri_converter import convert
from django.db.models import F

import json 
import pandas as pd 
from datetime import datetime

from docxtpl import InlineImage
from docxtpl import DocxTemplate
from django.contrib import messages


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
     # adding violation by excel
    if request.method == 'POST' and request.POST.get("excel"):
        print("adding violation by excel")
        # try:
        file = request.FILES['excelFile']
        df = pd.read_excel(file)
        
        #dynamically get table header from info in it
        if "رقم المخالفة" in df.columns:
            pass 
        else:
            df = pd.read_excel(file,header=1)
            print("header on 2nd row")
        
        # loop over each row in violations
        for index, row in df.iterrows():
            violation_id = str(row['رقم المخالفة'])  # getting this value to construct violation instance
            print(f"processing violation:{violation_id}")
            
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
            
            # getting bus plate in arabic will be used to construct vehicle instance 
            bus_plate = row['لوحة المركبة']
            amount = row['مبلغ المخالفة']
            violation_type = row['تفاصيل المخالفة بالانجليزي']
            violation_type_arabic = row['تفاصيل المخالفة بالعربي']

            violation_type_instance = Violation_Type.objects.get(violation_type_en=violation_type)
            # Create a Violation instance
            try:
                vehicle = Vehicle.objects.get(plate_ar=bus_plate)
            except:
                vehicle = Vehicle.objects.get(plate_eng=bus_plate)

            if vehicle:
                violation_instance = Violation(
                violation_id=violation_id,
                date=violation_georgian_date,
                time=time,
                vehicle=vehicle,
                amount=amount,
                violation_type=violation_type,
                violation_type_arabic=violation_type_arabic,
                status= violation_type_instance.status
                )

                violation_instance.save()
                    
        context = {'status': 'Success', 'message': 'Violation Added Successfully'}

        # except Exception as e:
        #     context = {'status': 'Failed', 'message': f'Adding violation Failed due to :{e}'}
        messages.success(request, 'success')

        return redirect("violations")
    
    elif request.method == 'POST' and request.POST.get("inputbyform"):
        try:
            
            violation_no = request.POST.get('violation_no')
                            # Check if a Violation with the given violation_id already exists
            if Violation.objects.filter(violation_id=violation_no).exists():
                context = {'status': 'Failed', 'message': f'Violation No. Duplicated'}
                messages.warning(request, 'duplicate')

                return redirect("violations")

            date = request.POST.get("date")
            time = request.POST.get("time")
            bus_plate = request.POST.get("bus_plate")
            
            
            
            violation_type_en = request.POST.get("violation_en")
            ## violation type
            violation_type = Violation_Type.objects.get(violation_en=violation_type_en)

            amount = violation_type.violation_cost
            violation_type_arabic  = violation_type.violation_ar
            violation_type_english  = violation_type.violation_en

            # Create a Violation instance
            try:
                vehicle = Vehicle.objects.get(plate_ar=bus_plate)
            except:
                vehicle = Vehicle.objects.get(plate_eng=bus_plate)

            if vehicle:
                violation_instance = Violation(
                violation_id=violation_no,
                date=date,
                time=time,
                vehicle=vehicle,
                amount=amount,
                violation_type=violation_type_english,
                violation_type_arabic=violation_type_arabic,
                status= violation_type.status
                )

                violation_instance.save()
                context = {'status': 'Success', 'message': 'Violation Added Successfully'}


        except Exception as e:
            context = {'status': 'Failed', 'message': f'Adding violation Failed due to :{e}'}
        
        messages.success(request, 'sucess')
        return redirect("violations")
    
    
    if request.user.is_authenticated:
        user_groups = request.user.groups.values_list('name', flat=True)  # Assuming user groups are related to vehicles
        print(user_groups)
        if user_groups:
            # Assuming each group corresponds to a vehicle user
            # violations = Violation.objects.filter(vehicle__vehicle_user__in=user_groups)

            violations = Violation.objects.filter(vehicle__vehicle_user__in=user_groups).exclude(status="excluded")

        else:
            violations = []
    employees = Employee.objects.all()
    vehicles = Vehicle.objects.all()
    violation_types = Violation_Type.objects.all()
    
    employees_ptc = [] 
    for employee in employees:
        employees_ptc.append(employee.ptc_id)
    
    
    merged_data= []
    for violation in violations:
        vehicle= violation.vehicle
            
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
        "employees_ptc":employees_ptc,
        "violation_types":violation_types
    }
    
    return render(request,"view_violations.html",context)


@login_required(login_url='home')
def ex_violations(request):
    context = {}
    if request.user.is_authenticated:
        user_groups = request.user.groups.values_list('name', flat=True)  # Assuming user groups are related to vehicles
        
        if "admin" in user_groups:
            # Filter Violation objects where violation_type_id is in the list of excluded IDs
            violations = Violation.objects.filter(status="excluded")
            
            context['violations'] = violations
                
    return render(request, "ex_violations.html", context)


@login_required(login_url='home')
def export_violations(request):
    # Fetch all violations from the database
    violations = Violation.objects.all()
    
    # Convert queryset to DataFrame
    data = {
        'Violation No.': [violation.violation_id for violation in violations],
        'Violation Date': [violation.date for violation in violations],
        'Time': [violation.time for violation in violations],
        'Bus Plate': [violation.vehicle.plate_ar for violation in violations],
        'Fleet no': [violation.vehicle.fleet_no for violation in violations],
        'vehicle user': [violation.vehicle.vehicle_user for violation in violations],
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
    # # Get the xlsxwriter workbook and worksheet objects
    # workbook = excel_writer.book
    # worksheet = excel_writer.sheets['Violations']

    # # Close the Excel writer to save the file
    excel_writer.close()

    # # wb = xw.Book('violations_export.xlsx')
    # # sheet = wb.sheets['Violations'] 

    # # column_widths = {
    # #     'A': 50,
    # #     'B': 50,
    # #     'C': 50,
    # #     'D': 50,
    # #     'E': 50,
    # #     'F': 100,
    # #     'G': 50,
    # #     'H': 100,
    # #     'I': 100,
    # #     'J': 50,
    # # }

    # # for col, width in column_widths.items():
    # #     sheet.range(f'{col}:{col}').column_width = width

    # # # Save the Excel file
    # # file_path = 'violations_export.xlsx'
    # # wb.save(file_path)
    # # wb.close()


    # Create a response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=violations_export.xlsx'
    df.to_excel(response, index=False, sheet_name='Violations')

    return response



@login_required(login_url='home')
def add_violations(request):
    
    # adding violation by excel
    if request.method == 'POST' and request.POST.get("excel"):
        print("adding violation by excel")
        # try:
        file = request.FILES['excelFile']
        df = pd.read_excel(file)
        
        #dynamically get table header from info in it
        if "رقم المخالفة" in df.columns:
            pass 
        else:
            df = pd.read_excel(file,header=1)
            print("header on 2nd row")
        
        # loop over each row in violations
        for index, row in df.iterrows():
            violation_id = str(row['رقم المخالفة'])  # getting this value to construct violation instance
            print(f"processing violation:{violation_id}")
            
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
            
            # getting bus plate in arabic will be used to construct vehicle instance 
            bus_plate = row['لوحة المركبة']
            amount = row['مبلغ المخالفة']
            violation_type = row['تفاصيل المخالفة بالانجليزي']
            violation_type_arabic = row['تفاصيل المخالفة بالعربي']
            violation_type = Violation_Type.objects.get(violation_en=violation_type)


            print(f"bus plate:{bus_plate}")
            # Create a Violation instance
            try:
                vehicle = Vehicle.objects.get(plate_ar=bus_plate)
            except:
                vehicle = Vehicle.objects.get(plate_eng=bus_plate)

            if vehicle:
                violation_instance = Violation(
                violation_id=violation_id,
                date=violation_georgian_date,
                time=time,
                vehicle=vehicle,
                amount=amount,
                violation_type=violation_type,
                violation_type_arabic=violation_type_arabic,
                status=violation_type.status
                
                )

                violation_instance.save()
                    
        context = {'status': 'Success', 'message': 'Violation Added Successfully'}

        # except Exception as e:
        #     context = {'status': 'Failed', 'message': f'Adding violation Failed due to :{e}'}

        return render(request, "add_violations.html",context=context)
    
    elif request.method == 'POST' and request.POST.get("inputbyform"):
        try:
            
            violation_no = request.POST.get('violation_no')
            print(f"violation_no:{violation_no}")
                            # Check if a Violation with the given violation_id already exists
            if Violation.objects.filter(violation_id=violation_no).exists():
                context = {'status': 'Failed', 'message': f'Violation No. Duplicated'}
                return render(request, "add_violations.html",context=context)

            date = request.POST.get("date")
            time = request.POST.get("time")
            bus_plate = request.POST.get("bus_plate")
            violation_type_en = request.POST.get("violation_en")
            ## violation type
            violation_type = Violation_Type.objects.get(violation_en=violation_type_en)
            print(f"date:{date}")
            print(f"time:{time}")
            print(f"violation_type_en:{violation_type_en}")
            print(f"bus plate:{bus_plate}")
            
            # Create a Violation instance
            try:
                vehicle = Vehicle.objects.get(plate_ar=bus_plate)
            except:
                vehicle = Vehicle.objects.get(plate_eng=bus_plate)

            if vehicle:
                violation_instance = Violation(
                violation_id=violation_no,
                date=date,
                time=time,
                vehicle=vehicle,
                amount=violation_type.violation_cost,
                violation_type=violation_type.violation_en,
                violation_type_arabic=violation_type.violation_ar,
                status=violation_type.status
                )

                violation_instance.save()
                context = {'status': 'Success', 'message': 'Violation Added Successfully'}


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
            messages.error(request,"Invalid login credentials")
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('home')  

@login_required(login_url='home')
def assign_employee(request):
    context = {'status': 'Failed', 'message': 'not post req'}

    if request.method in ('POST','PUT') and not request.POST.get("pdf"):
        json_data = json.loads(request.body.decode('utf-8'))

        # Access the data using keys
        ptc_id = json_data.get("ptc_id")
        violation_no = json_data.get("violation_id")
        try:
            violation = Violation.objects.get(violation_id=violation_no)
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
class EmployeeAssignmentError(Exception):
    pass

@login_required(login_url='home')
def print_document(request):
    if request.method == 'POST':
        #request data
        # Retrieve JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        violation_no = data.get('violation_no')        #get violation from db
        violation = Violation.objects.get(violation_id=violation_no)
        
        if violation.employee:
            vehicle = violation.vehicle

            print(vehicle)        
            #employee data
            employee = violation.employee
            context = {
                "violation_no":violation.violation_id,
                "date":violation.date,
                "time":violation.time,
                "amount":violation.amount,
                "violation_type_eng":violation.violation_type,
                "violation_type_arabic":violation.violation_type_arabic,
                
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
        

        else:
            raise EmployeeAssignmentError("Assign employee")



@login_required(login_url='home')
def get_cost_by_violation_en(request):
    if request.method == 'POST':
        print("post req")
        data = json.loads(request.body)
        violation_en = data.get('violation_en', None)
        print(violation_en)
        if violation_en:
            try:
                violation = Violation_Type.objects.get(violation_en=violation_en)
                violation_cost = violation.violation_cost
                return JsonResponse({'violation_cost': violation_cost})
            except Violation_Type.DoesNotExist:
                return JsonResponse({'error': 'Violation not found'}, status=404)


    print("invalid req")
    return JsonResponse({'error': 'Invalid request'}, status=400)
