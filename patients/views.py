"""
Views for Patient Profile and Medical History
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import PatientProfile, MedicalHistory
from .serializers import (
    PatientProfileSerializer,
    MedicalHistorySerializer,
    MedicalHistoryCreateSerializer
)
from .permissions import IsPatient, IsDoctor, CanAccessMedicalHistory


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsPatient])
def patient_profile(request):
    """
    Get or create patient profile for current user
    """
    if request.method == 'GET':
        try:
            profile = PatientProfile.objects.get(user=request.user)
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data)
        except PatientProfile.DoesNotExist:
            return Response({
                'message': 'Profile not created yet'
            }, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        # Check if profile already exists
        if PatientProfile.objects.filter(user=request.user).exists():
            return Response({
                'error': 'Profile already exists. Use PUT to update.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PatientProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsPatient])
def update_patient_profile(request):
    """
    Update patient profile
    """
    try:
        profile = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        return Response({
            'error': 'Profile does not exist. Create one first.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_profile_by_id(request, patient_id):
    """
    Get patient profile by ID (for doctors to view assigned patients)
    """
    if request.user.role == 'DOCTOR':
        # Check if patient is assigned to this doctor
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'You do not have access to this patient'
            }, status=status.HTTP_403_FORBIDDEN)
    
    elif request.user.id != patient_id:
        return Response({
            'error': 'You can only view your own profile'
        }, status=status.HTTP_403_FORBIDDEN)
    
    profile = get_object_or_404(PatientProfile, user_id=patient_id)
    serializer = PatientProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medical_history_list(request):
    """
    Get medical history for current user or assigned patients
    """
    if request.user.role == 'PATIENT':
        # Patients see their own history
        history = MedicalHistory.objects.filter(patient=request.user)
    elif request.user.role == 'DOCTOR':
        # Doctors see history of assigned patients
        from doctors.models import DoctorPatientAssignment
        assigned_patients = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            is_active=True
        ).values_list('patient_id', flat=True)
        history = MedicalHistory.objects.filter(patient_id__in=assigned_patients)
    else:
        return Response({
            'error': 'Invalid user role'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = MedicalHistorySerializer(history, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medical_history_by_patient(request, patient_id):
    """
    Get medical history for a specific patient
    """
    # Check access permissions
    if request.user.role == 'PATIENT' and request.user.id != patient_id:
        return Response({
            'error': 'You can only view your own medical history'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'You do not have access to this patient'
            }, status=status.HTTP_403_FORBIDDEN)
    
    history = MedicalHistory.objects.filter(patient_id=patient_id)
    serializer = MedicalHistorySerializer(history, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def create_medical_history(request):
    """
    Create a medical history entry (doctors only)
    """
    serializer = MedicalHistoryCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Verify doctor is assigned to patient
        from doctors.models import DoctorPatientAssignment
        patient_id = serializer.validated_data['patient'].id
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'You are not assigned to this patient'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer.save(doctor=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medical_history_detail(request, history_id):
    """
    Get specific medical history entry
    """
    history = get_object_or_404(MedicalHistory, id=history_id)
    
    # Check permissions
    if request.user.role == 'PATIENT' and history.patient != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient=history.patient,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = MedicalHistorySerializer(history)
    return Response(serializer.data)