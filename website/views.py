from django.shortcuts import render
from django.shortcuts import HttpResponse

# Create your views here.

def home(request):
    return render(request, "home.html")

def view_violation(request):
    return render(request,"view_violations.html")

def add_violations(request):
    return render(request,"add_violations.html")