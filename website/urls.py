"""
URL configuration for systemizer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views 


urlpatterns = [
    
    path("", views.home,name='home'),
    path("login", views.login_view,name='login'),
    path("logout", views.logout_view,name='logout'),

    path("violations",views.view_violation,name='violations'),
    path('export_violations/', views.export_violations, name='export_violations'),
    path("new-violations",views.add_violations,name='new-violations'),
    path("print-violation",views.print_document,name="print-violation"),
    
    path("assign_employee",views.assign_employee,name='assign_employee'),
    path("get-employee",views.get_employee,name="get-employee")

]
