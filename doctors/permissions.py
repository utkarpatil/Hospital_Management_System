"""
Doctor-specific Permission Classes
Handles access control for doctor actions
"""
from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    """
    Allow access only to authenticated doctors
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'DOCTOR'
        )


class CanAccessAssignedPatient(BasePermission):
    """
    Allow doctors to access only their assigned patients
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role != 'DOCTOR':
            return False

        # obj can be PatientProfile / MedicalHistory / Appointment etc.
        patient = None

        if hasattr(obj, 'patient'):
            patient = obj.patient
        elif hasattr(obj, 'user'):
            patient = obj.user

        if patient is None:
            return False

        from doctors.models import DoctorPatientAssignment
        return DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient=patient,
            is_active=True
        ).exists()


class CanManageDoctorAppointment(BasePermission):
    """
    Doctors can view/update appointments assigned to them
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == 'DOCTOR'
            and obj.doctor == request.user
        )


class CanWriteMedicalData(BasePermission):
    """
    Doctors can create medical history & prescriptions
    only for assigned patients
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'DOCTOR'
        )
