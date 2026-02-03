"""
URL Configuration for Lab Reports App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Lab Report CRUD
    path('', views.lab_report_list, name='lab-report-list'),
    path('create/', views.create_lab_report, name='create-lab-report'),
    path('<int:report_id>/', views.lab_report_detail, name='lab-report-detail'),
    path('patient/<int:patient_id>/', views.reports_by_patient, name='reports-by-patient'),
    
    # Visualization endpoints
    path('visualize/report/<int:report_id>/', views.visualize_report, name='visualize-report'),
    path('visualize/trend/<int:patient_id>/', views.visualize_parameter_trend, name='visualize-parameter-trend'),
    
    # Statistics and analysis
    path('statistics/<int:patient_id>/', views.parameter_statistics, name='parameter-statistics'),
    path('parameters/<int:patient_id>/', views.available_parameters, name='available-parameters'),
]