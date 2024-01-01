from django.contrib import admin
from website.models import Employee,PDF,Violation,Vehicle

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['ptc_id', 'employee_name','ID_number']
admin.site.register(Employee,EmployeeAdmin)

admin.site.register(PDF)


class ViolationAdmin(admin.ModelAdmin):
    list_display = ["violation_id", "violation_type", "employee"]

class VehicleAdmin(admin.ModelAdmin):
    list_display = ['fleet_no','plate_eng','vehicle_user','vehicle_type']

admin.site.register(Violation,ViolationAdmin)
admin.site.register(Vehicle,VehicleAdmin)