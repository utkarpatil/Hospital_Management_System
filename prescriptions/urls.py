"""
URL Configuration for Prescriptions App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Prescription endpoints
    path('', views.prescription_list, name='prescription-list'),
    path('create/', views.create_prescription, name='create-prescription'),
    path('<int:prescription_id>/', views.prescription_detail, name='prescription-detail'),
    path('patient/<int:patient_id>/', views.prescriptions_by_patient, name='prescriptions-by-patient'),
    
    # Medicine endpoints
    path('<int:prescription_id>/add-medicine/', views.add_medicine_to_prescription, name='add-medicine'),
    path('medicine/<int:medicine_id>/', views.medicine_detail, name='medicine-detail'),
    
    # Reminder endpoints
    path('reminders/', views.medicine_reminders, name='medicine-reminders'),
    path('medicine/<int:medicine_id>/reminder/', views.update_medicine_reminder, name='update-medicine-reminder'),
]