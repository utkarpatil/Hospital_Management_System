"""
URL Configuration for Appointments App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Appointment CRUD
    path('', views.appointment_list, name='appointment-list'),
    path('create/', views.create_appointment, name='create-appointment'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('<int:appointment_id>/update-status/', views.update_appointment_status, name='update-appointment-status'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel-appointment'),
    
    # Doctor-specific endpoints
    path('upcoming/', views.upcoming_appointments, name='upcoming-appointments'),
    path('pending/', views.pending_appointments, name='pending-appointments'),
    
    # Availability
    path('available-slots/<int:doctor_id>/', views.available_slots, name='available-slots'),
]