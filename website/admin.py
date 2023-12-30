from django.contrib import admin
from website.models import Employee,PDF,Violation

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['ptc_id', 'employee_name','ID_number']
admin.site.register(Employee,EmployeeAdmin)

admin.site.register(PDF)


class ViolationAdmin(admin.ModelAdmin):
    list_display = ["violation_id", "violation_type", "employee"]

admin.site.register(Violation,ViolationAdmin)
