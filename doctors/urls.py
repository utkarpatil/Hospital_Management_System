"""
URL Configuration for Doctors App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Doctor Profile endpoints
    path('profile/', views.doctor_profile, name='doctor-profile'),
    path('profile/update/', views.update_doctor_profile, name='update-doctor-profile'),
    path('list/', views.doctor_list, name='doctor-list'),
    path('search/', views.search_doctors, name='search-doctors'),
    path('<int:doctor_id>/', views.doctor_detail, name='doctor-detail'),
    
    # Patient Assignment endpoints
    path('patients/', views.assigned_patients, name='assigned-patients'),
    path('patients/assign/', views.assign_patient, name='assign-patient'),
    path('patients/unassign/<int:patient_id>/', views.unassign_patient, name='unassign-patient'),
]