from django.db import models

class Employee(models.Model):
    ptc_id = models.IntegerField(primary_key=True)
    employee_name = models.CharField(max_length=255)
    ID_number = models.BigIntegerField()

class PDF(models.Model):
    pdf_id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='pdfs/')
    
class Vehicle(models.Model):
    fleet_no = models.BigIntegerField()
    vehicle_user = models.CharField(max_length=255)
    plate_eng = models.CharField(max_length=255, primary_key=True)
    plate_ar = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=255, default='Bus')

class Violation(models.Model):
    violation_id = models.CharField(max_length=255, primary_key=True, blank=False, null=False)
    date = models.DateField()
    time = models.TimeField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    violation_type = models.TextField()
    violation_type_arabic = models.TextField()

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, default="")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, default="")
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE, null=True, blank=True, default="")
