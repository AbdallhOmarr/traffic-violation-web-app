from django.contrib import admin
from website.models import Employee,PDF,Violation,Vehicle,Violation_Type

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['ptc_id', 'employee_name','ID_number']
    search_fields = ['ptc_id', 'employee_name', 'ID_number']

    
admin.site.register(Employee,EmployeeAdmin)

admin.site.register(PDF)


class ViolationAdmin(admin.ModelAdmin):
    list_display = ["violation_id", "violation_type", "employee"]
    search_fields = ['violation_id', 'violation_type', 'employee__employee_name', 'employee__ptc_id']

class VehicleAdmin(admin.ModelAdmin):
    list_display = ['fleet_no','plate_eng','vehicle_user','vehicle_type']
    search_fields = ['fleet_no', 'plate_eng', 'vehicle_user']



class Violation_TypeAdmin(admin.ModelAdmin):
    list_display = ['violation_en','violation_ar',"violation_cost"]

admin.site.register(Violation,ViolationAdmin)
admin.site.register(Vehicle,VehicleAdmin)
admin.site.register(Violation_Type,Violation_TypeAdmin)