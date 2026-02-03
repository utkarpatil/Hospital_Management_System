"""
URL Configuration for Patients App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Patient Profile endpoints
    path('profile/', views.patient_profile, name='patient-profile'),
    path('profile/update/', views.update_patient_profile, name='update-patient-profile'),
    path('profile/<int:patient_id>/', views.patient_profile_by_id, name='patient-profile-by-id'),
    
    # Medical History endpoints
    path('medical-history/', views.medical_history_list, name='medical-history-list'),
    path('medical-history/create/', views.create_medical_history, name='create-medical-history'),
    path('medical-history/<int:history_id>/', views.medical_history_detail, name='medical-history-detail'),
    path('medical-history/patient/<int:patient_id>/', views.medical_history_by_patient, name='medical-history-by-patient'),
]