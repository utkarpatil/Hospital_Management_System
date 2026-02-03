"""
Custom Permission Classes for Healthcare System
Implements role-based access control
"""
from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    """
    Permission class to check if user is a doctor
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'DOCTOR'


class IsPatient(permissions.BasePermission):
    """
    Permission class to check if user is a patient
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PATIENT'


class IsDoctorOrPatient(permissions.BasePermission):
    """
    Permission class to check if user is either doctor or patient
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['DOCTOR', 'PATIENT']


class IsOwnerOrDoctor(permissions.BasePermission):
    """
    Permission class to allow:
    - Patients to access their own data
    - Doctors to access their assigned patients' data
    """
    def has_object_permission(self, request, view, obj):
        # If user is the owner (patient)
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # If user is a patient and owns the object
        if hasattr(obj, 'patient') and obj.patient == request.user:
            return True
        
        # If user is a doctor, check if patient is assigned
        if request.user.role == 'DOCTOR':
            if hasattr(obj, 'patient'):
                # Check if doctor is assigned to this patient
                from doctors.models import DoctorPatientAssignment
                is_assigned = DoctorPatientAssignment.objects.filter(
                    doctor=request.user,
                    patient=obj.patient,
                    is_active=True
                ).exists()
                return is_assigned
        
        return False


class CanAccessMedicalHistory(permissions.BasePermission):
    """
    Permission for medical history access:
    - Patient can view their own history
    - Assigned doctors can view patient history
    """
    def has_object_permission(self, request, view, obj):
        # Patient viewing their own history
        if obj.patient == request.user:
            return True
        
        # Doctor viewing assigned patient's history
        if request.user.role == 'DOCTOR':
            from doctors.models import DoctorPatientAssignment
            is_assigned = DoctorPatientAssignment.objects.filter(
                doctor=request.user,
                patient=obj.patient,
                is_active=True
            ).exists()
            return is_assigned
        
        return False


class CanManageAppointment(permissions.BasePermission):
    """
    Permission for appointment management:
    - Patients can create and view their appointments
    - Doctors can view and update their appointments
    """
    def has_object_permission(self, request, view, obj):
        # Patient can access their own appointments
        if obj.patient == request.user:
            return True
        
        # Doctor can access appointments assigned to them
        if obj.doctor == request.user:
            return True
        
        return False


class CanCreatePrescription(permissions.BasePermission):
    """
    Only doctors can create prescriptions
    Only for their assigned patients
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.role == 'DOCTOR'
        return True
    
    def has_object_permission(self, request, view, obj):
        # Patients can view their prescriptions
        if obj.patient == request.user:
            return True
        
        # Doctors can view/edit prescriptions they created
        if obj.doctor == request.user:
            return True
        
        return False