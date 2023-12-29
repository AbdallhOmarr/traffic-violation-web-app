from django.db import models

class Employee(models.Model):
    ptc_id = models.IntegerField(primary_key=True)
    employee_name = models.CharField(max_length=255)
    ID_number = models.BigIntegerField()

class PDF(models.Model):
    pdf_id = models.IntegerField(primary_key=True)
    file = models.FileField(upload_to='pdfs/')

class Violation(models.Model):
    violation_id = models.CharField(max_length=255, primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    bus_panel = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    violation_type = models.TextField()
    violation_type_arabic = models.TextField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True,blank=True)
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE,null=True,blank=True)
    
